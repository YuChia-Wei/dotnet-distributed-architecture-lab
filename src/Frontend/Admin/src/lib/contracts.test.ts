import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, request } from './api'
import {
  createProduct, getMicrocks, getSandboxControl, getWire, listProducts,
  parseMicrocks, setMicrocksMode, updateProduct, validDelay, validateProduct,
} from './contracts'

const fetchMock = vi.fn<typeof fetch>()
vi.stubGlobal('fetch', fetchMock)
afterEach(() => fetchMock.mockReset())

describe('HTTP contract', () => {
  it('uses same-origin URLs and handles a successful empty update response', async () => {
    fetchMock.mockResolvedValueOnce(new Response('', { status: 200 }))
    await updateProduct('abc-123', { name: '商品', description: '', price: 20 })
    expect(fetchMock).toHaveBeenCalledWith('/api/products/abc-123', expect.objectContaining({
      method: 'PUT', body: JSON.stringify({ name: '商品', description: '', price: 20 }),
    }))
  })

  it('does not treat an empty create response as success', async () => {
    fetchMock.mockResolvedValueOnce(new Response('', { status: 200 }))
    await expect(createProduct({ name: '商品', description: '', price: 20 })).rejects.toThrow('缺少預期資料')
  })

  it('keeps empty, malformed, and transport failures distinct', async () => {
    fetchMock.mockResolvedValueOnce(new Response('[]', { status: 200 }))
    expect(await listProducts()).toEqual([])
    fetchMock.mockResolvedValueOnce(new Response('<html>bad gateway</html>', { status: 200 }))
    await expect(listProducts()).rejects.toThrow('格式不正確')
    fetchMock.mockRejectedValueOnce(new TypeError('offline'))
    await expect(listProducts()).rejects.toThrow('無法連線')
  })

  it('extracts bounded API errors without claiming success', async () => {
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ detail: '主檔無法修改' }), { status: 409 }))
    await expect(updateProduct('id', { name: 'X', description: '', price: 1 })).rejects.toMatchObject({
      message: '主檔無法修改', status: 409,
    } satisfies Partial<ApiError>)
    fetchMock.mockResolvedValueOnce(new Response('supplier unavailable', { status: 503 }))
    await expect(getWire()).rejects.toThrow('supplier unavailable')
    fetchMock.mockResolvedValueOnce(new Response('<html><body>at SecretPath:3</body></html>', { status: 502 }))
    await expect(getWire()).rejects.toThrow('服務回應錯誤（HTTP 502）')
  })

  it('forwards an abort signal for stale reads', async () => {
    const controller = new AbortController()
    fetchMock.mockResolvedValueOnce(new Response('[]', { status: 200 }))
    await listProducts(controller.signal)
    expect(fetchMock).toHaveBeenCalledWith('/api/products', expect.objectContaining({ signal: controller.signal }))
  })
})

describe('admin mutation and control contracts', () => {
  it('rejects invalid product price and sandbox delay before mutation', () => {
    expect(validateProduct({ name: ' ', description: '', price: 1 })).toBe('請輸入商品名稱。')
    expect(validateProduct({ name: 'X', description: '', price: -1 })).toContain('價格')
    expect(validateProduct({ name: 'X', description: '', price: 1.234 })).toContain('價格')
    expect(validateProduct({ name: 'X', description: '', price: 1.1 })).toBeNull()
    expect(validDelay(-1)).toBe(false)
    expect(validDelay(10001)).toBe(false)
    expect(validDelay(1.5)).toBe(false)
    expect(validDelay(10000)).toBe(true)
  })

  it('recognizes a custom Microcks state without inventing a preset mode', () => {
    const state = parseMicrocks({
      mode: null, status: 'custom', serviceId: 'service-1', serviceName: 'Supplier API',
      serviceVersion: '1.0.0', operations: [{ name: 'catalog', method: 'GET', dispatcher: 'URI_PARTS',
        dispatcherRules: 'native custom rules' }], message: 'custom mapping',
    })
    expect(state.mode).toBeNull()
    expect(state.status).toBe('custom')
    expect(state.operations[0].dispatcherRules).toBe('native custom rules')
    const nativeDefault = parseMicrocks({
      mode: null, status: 'custom', serviceId: 'service-1', serviceName: 'Supplier API',
      serviceVersion: '1.0.0', operations: [{ name: 'order', method: 'POST',
        dispatcher: null, dispatcherRules: null }], message: null,
    })
    expect(nativeDefault.operations[0].dispatcher).toBeNull()
    expect(() => parseMicrocks({ mode: 'mock', status: 'ready' })).toThrow('Microcks 狀態格式不正確')
  })

  it('shows an unavailable Microcks native readback truthfully', async () => {
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({
      mode: null, status: 'unavailable', serviceId: null, serviceName: 'Supplier API',
      serviceVersion: '1.0.0', operations: [], message: 'native unavailable',
    }), { status: 200 }))
    expect(await getMicrocks()).toMatchObject({ mode: null, status: 'unavailable' })
  })

  it('sends only a bounded Microcks mode to the control facade', async () => {
    fetchMock.mockResolvedValueOnce(new Response('{}', { status: 200 }))
    await setMicrocksMode('hybrid')
    expect(fetchMock).toHaveBeenCalledWith('/api/admin/supplier-mock/control/microcks/mode',
      expect.objectContaining({ method: 'POST', body: '{"mode":"hybrid"}' }))
  })

  it('requires expected state fields in a supplier response', async () => {
    fetchMock.mockResolvedValueOnce(new Response('{}', { status: 200 }))
    await expect(getWire()).rejects.toThrow('引擎狀態格式不正確')
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ delayAfterCommitMs: 0, persistence: 'runtime' }), { status: 200 }))
    expect(await getSandboxControl()).toMatchObject({ delayAfterCommitMs: 0 })
  })

  it('does not accept missing body on a required read', async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }))
    await expect(request('/api/products', { expectBody: true })).rejects.toThrow('缺少預期資料')
  })
})
