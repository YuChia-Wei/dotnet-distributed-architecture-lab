import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, createOrder, createPurchase, moneyValid, positiveInt, receive, request, skuValid, stockInt } from './api'

const id = '11111111-1111-4111-8111-111111111111'
const other = '22222222-2222-4222-8222-222222222222'
afterEach(() => vi.unstubAllGlobals())

describe('input and response guards', () => {
  it('blocks invalid quantities, money and SKU before a mutation', async () => {
    const fetch = vi.fn(); vi.stubGlobal('fetch', fetch)
    expect(positiveInt(0)).toBe(false)
    expect(positiveInt(1.5)).toBe(false)
    expect(stockInt(-1)).toBe(false)
    expect(moneyValid(1.234)).toBe(false)
    expect(moneyValid(19.99)).toBe(true)
    expect(skuValid('REAL/001')).toBe(false)
    await expect(createOrder({ product: { id, name: '商品', description: '', price: 2 }, quantity: -2, operationId: other })).rejects.toThrow()
    expect(() => createPurchase({ clientRequestId: id, productId: other, supplierSku: 'bad/sku', quantity: 1, unitPrice: 2, currency: 'TWD', provider: 'direct' })).toThrow()
    expect(() => receive(id, other, 0)).toThrow()
    expect(fetch).not.toHaveBeenCalled()
  })

  it('uses same-origin API and accepts only the expected order success body', async () => {
    const fetch = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ isSuccess: true, value: { orderId: other }, errorMessage: null }), { status: 200 })).mockResolvedValueOnce(new Response('not-json', { status: 200 }))
    vi.stubGlobal('fetch', fetch)
    const input = { product: { id, name: '商品', description: '', price: 12.25 }, quantity: 2, operationId: other }
    const result = await createOrder(input)
    expect(result.value.orderId).toBe(other)
    expect(fetch.mock.calls[0][0]).toBe('/api/orders')
    const sent = JSON.parse(fetch.mock.calls[0][1].body)
    expect(sent).toMatchObject({ operationId: other, totalAmount: 24.5, quantity: 2 })
    await expect(createOrder(input)).rejects.toMatchObject({ uncertain: true })
    expect(fetch).toHaveBeenCalledTimes(2)
  })

  it('keeps a server failure or transport loss uncertain for writes, with no retry', async () => {
    const fetch = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ detail: '上游暫時無法回應' }), { status: 503, headers: { 'Content-Type': 'application/problem+json' } })).mockRejectedValueOnce(new TypeError('network'))
    vi.stubGlobal('fetch', fetch)
    const identity = { clientRequestId: id, productId: other, supplierSku: 'REAL-001', quantity: 2, unitPrice: 10, currency: 'TWD' as const, provider: 'direct' as const }
    await expect(createPurchase(identity)).rejects.toMatchObject({ uncertain: true, message: '服務暫時無法完成請求，請查詢最新資料確認結果。' })
    await expect(createPurchase(identity)).rejects.toMatchObject({ uncertain: true })
    expect(fetch).toHaveBeenCalledTimes(2)
    expect(JSON.parse(fetch.mock.calls[0][1].body).clientRequestId).toBe(id)
    expect(JSON.parse(fetch.mock.calls[1][1].body).clientRequestId).toBe(id)
  })

  it('rejects an unexpected empty success rather than treating 204 as completed data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })))
    await expect(request('/api/orders', { method: 'POST' }, (v): v is object => !!v)).rejects.toBeInstanceOf(ApiError)
  })

  it('treats a response-body disconnect after write headers as uncertain', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, status: 200, text: () => Promise.reject(new TypeError('stream lost')) }))
    await expect(request('/api/orders', { method: 'POST' }, (v): v is object => !!v)).rejects.toMatchObject({ uncertain: true, message: '回應中斷，請查詢最新資料確認結果。' })
  })
})
