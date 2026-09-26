// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import IntegrationsPage from './IntegrationsPage.vue'

afterEach(() => vi.restoreAllMocks())

function wireResponse(mode: string) {
  return new Response(JSON.stringify({
    mode, status: 'ready', upstream: 'http://supplier-sandbox:8080',
    persistence: 'runtime',
  }), { status: 200 })
}

describe('dangerous controls', () => {
  it('requires confirmation and prevents a second mode POST while applying', async () => {
    let currentMode = 'hybrid'
    let finishPost: ((value: Response) => void) | undefined
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const path = String(input)
      if (path.endsWith('/control/state')) return wireResponse(currentMode)
      if (path.endsWith('/control/mappings')) return new Response('{"mappings":[]}')
      if (path.endsWith('/control/requests')) return new Response('{"requests":[]}')
      if (path.endsWith('/control/mode') && init?.method === 'POST') {
        return new Promise<Response>(resolve => { finishPost = resolve })
      }
      throw new Error(`Unexpected ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const nativeConfirm = vi.spyOn(window, 'confirm').mockImplementation(() => {
      throw new Error('Native dialog must not be used')
    })
    const host = document.createElement('div')
    document.body.appendChild(host)
    const wrapper = mount(IntegrationsPage, { attachTo: host })
    await flushPromises()

    const mockButton = wrapper.findAll('button').find(button => button.text().includes('套用 Mock'))
    expect(mockButton).toBeDefined()
    ;(mockButton!.element as HTMLButtonElement).focus()
    await mockButton!.trigger('click')
    expect(wrapper.find('[role="alertdialog"]').text()).toContain('清除現有請求紀錄')
    expect(document.activeElement).toBe(wrapper.find('[data-testid="confirm-cancel"]').element)
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/mode') && init?.method === 'POST')).toHaveLength(0)

    await wrapper.find('[role="alertdialog"]').trigger('keydown', { key: 'Escape' })
    await flushPromises()
    expect(wrapper.find('[role="alertdialog"]').exists()).toBe(false)
    expect(document.activeElement).toBe(mockButton!.element)

    await mockButton!.trigger('click')
    await mockButton!.trigger('click')
    expect(wrapper.findAll('[role="alertdialog"]')).toHaveLength(1)
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/mode') && init?.method === 'POST')).toHaveLength(0)
    await wrapper.find('[data-testid="confirm-cancel"]').trigger('click')
    expect(wrapper.find('[role="alertdialog"]').exists()).toBe(false)
    await mockButton!.trigger('click')
    await wrapper.find('[data-testid="confirm-accept"]').trigger('click')
    expect(mockButton!.attributes('disabled')).toBeDefined()
    await mockButton!.trigger('click')
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/mode') && init?.method === 'POST')).toHaveLength(1)

    currentMode = 'mock'
    finishPost?.(new Response('{}', { status: 200 }))
    await flushPromises()
    expect(wrapper.text()).toContain('服務已讀回所選模式')
    expect(nativeConfirm).not.toHaveBeenCalled()
    wrapper.unmount()
    host.remove()
  })

  it('blocks out-of-range sandbox delay before PUT', async () => {
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      const path = String(input)
      if (path.endsWith('/control/state')) return wireResponse('hybrid')
      if (path.endsWith('/control/mappings')) return new Response('{"mappings":[]}')
      if (path.endsWith('/control/requests')) return new Response('{"requests":[]}')
      if (path.endsWith('/sandbox/control')) return new Response('{"delayAfterCommitMs":0,"persistence":"runtime"}')
      if (path.endsWith('/sandbox/orders') || path.endsWith('/sandbox/requests')) return new Response('[]')
      throw new Error(`Unexpected ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(IntegrationsPage)
    await flushPromises()
    await wrapper.find('#tab-sandbox').trigger('click')
    await flushPromises()
    await wrapper.find('#delay-input').setValue('10001')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('延遲須為 0 至 10000')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(0)
    wrapper.unmount()
  })

  it('cannot submit the default delay before control GET or during refresh', async () => {
    const pendingControls: Array<(response: Response) => void> = []
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const path = String(input)
      if (path.endsWith('/control/state')) return wireResponse('hybrid')
      if (path.endsWith('/control/mappings')) return new Response('{"mappings":[]}')
      if (path.endsWith('/control/requests')) return new Response('{"requests":[]}')
      if (path.endsWith('/sandbox/control') && init?.method === 'GET') {
        return new Promise<Response>(resolve => { pendingControls.push(resolve) })
      }
      if (path.endsWith('/sandbox/orders') || path.endsWith('/sandbox/requests')) return new Response('[]')
      throw new Error(`Unexpected ${init?.method} ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(IntegrationsPage)
    await flushPromises()
    await wrapper.find('#tab-sandbox').trigger('click')
    expect(pendingControls).toHaveLength(1)
    expect(wrapper.find('#delay-input').attributes('disabled')).toBeDefined()
    expect(wrapper.find('#panel-sandbox button[type="submit"]').attributes('disabled')).toBeDefined()
    await wrapper.find('#panel-sandbox form').trigger('submit')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(0)

    pendingControls.shift()?.(new Response('{"delayAfterCommitMs":750,"persistence":"runtime"}'))
    await flushPromises()
    expect((wrapper.find('#delay-input').element as HTMLInputElement).value).toBe('750')
    expect(wrapper.find('#delay-input').attributes('disabled')).toBeUndefined()

    await wrapper.find('#delay-input').setValue('900')
    await wrapper.find('.page-head button').trigger('click')
    expect(pendingControls).toHaveLength(1)
    expect(wrapper.find('#delay-input').attributes('disabled')).toBeDefined()
    await wrapper.find('#panel-sandbox form').trigger('submit')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(0)
    pendingControls.shift()?.(new Response('{"delayAfterCommitMs":750,"persistence":"runtime"}'))
    await flushPromises()
    expect((wrapper.find('#delay-input').element as HTMLInputElement).value).toBe('900')
    wrapper.unmount()
  })

  it('keeps the requested delay when native GET reads back a different value', async () => {
    let controlReads = 0
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const path = String(input)
      if (path.endsWith('/control/state')) return wireResponse('hybrid')
      if (path.endsWith('/control/mappings')) return new Response('{"mappings":[]}')
      if (path.endsWith('/control/requests')) return new Response('{"requests":[]}')
      if (path.endsWith('/sandbox/control') && init?.method === 'GET') {
        controlReads++
        return new Response(JSON.stringify({
          delayAfterCommitMs: controlReads === 1 ? 650 : 250, persistence: 'runtime',
        }))
      }
      if (path.endsWith('/sandbox/control') && init?.method === 'PUT') {
        return new Response('{"delayAfterCommitMs":900,"persistence":"runtime"}')
      }
      if (path.endsWith('/sandbox/orders') || path.endsWith('/sandbox/requests')) return new Response('[]')
      throw new Error(`Unexpected ${init?.method} ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(IntegrationsPage)
    await flushPromises()
    await wrapper.find('#tab-sandbox').trigger('click')
    await flushPromises()
    const delay = wrapper.find('#delay-input')
    expect((delay.element as HTMLInputElement).value).toBe('650')
    await delay.setValue('900')
    await wrapper.find('#panel-sandbox form').trigger('submit')
    await flushPromises()

    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'PUT')).toHaveLength(1)
    expect(controlReads).toBe(2)
    expect(wrapper.text()).toContain('服務讀回 250 毫秒，與要求的 900 毫秒不同')
    expect(wrapper.text()).not.toContain('延遲設定已由服務讀回')
    expect((delay.element as HTMLInputElement).value).toBe('900')
    wrapper.unmount()
  })

  it('uses the in-page dialog for WireMock reset and log clearing', async () => {
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const path = String(input)
      if (path.endsWith('/control/state')) return wireResponse('hybrid')
      if (path.endsWith('/control/mappings')) return new Response('{"mappings":[]}')
      if (path.endsWith('/control/requests') && init?.method === 'GET') return new Response('{"requests":[{"id":"one"}]}')
      if (path.endsWith('/control/requests') && init?.method === 'DELETE') return new Response(null, { status: 204 })
      if (path.endsWith('/control/reset') && init?.method === 'POST') return wireResponse('hybrid')
      throw new Error(`Unexpected ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const nativeConfirm = vi.spyOn(window, 'confirm').mockImplementation(() => {
      throw new Error('Native dialog must not be used')
    })
    const wrapper = mount(IntegrationsPage)
    await flushPromises()

    const resetButton = wrapper.findAll('button').find(button => button.text() === '還原啟動模式')
    await resetButton!.trigger('click')
    expect(wrapper.find('[role="alertdialog"]').text()).toContain('重建規則並清除請求紀錄')
    await wrapper.find('[data-testid="confirm-cancel"]').trigger('click')
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/reset') && init?.method === 'POST')).toHaveLength(0)

    const clearButton = wrapper.findAll('button').find(button => button.text() === '清除紀錄')
    await clearButton!.trigger('click')
    expect(wrapper.find('[role="alertdialog"]').text()).toContain('無法復原')
    await wrapper.find('[data-testid="confirm-cancel"]').trigger('click')
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/requests') && init?.method === 'DELETE')).toHaveLength(0)

    await resetButton!.trigger('click')
    await wrapper.find('[data-testid="confirm-accept"]').trigger('click')
    await flushPromises()
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/reset') && init?.method === 'POST')).toHaveLength(1)
    expect(nativeConfirm).not.toHaveBeenCalled()
    wrapper.unmount()
  })

  it('keeps Microcks custom state until its preset import is confirmed and read back', async () => {
    let mode: string | null = null
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const path = String(input)
      if (path.endsWith('/control/state')) return wireResponse('hybrid')
      if (path.endsWith('/control/mappings')) return new Response('{"mappings":[]}')
      if (path.endsWith('/control/requests')) return new Response('{"requests":[]}')
      if (path.endsWith('/control/microcks/state')) {
        return new Response(JSON.stringify({
          mode, status: mode ? 'ready' : 'custom', serviceId: 'id',
          serviceName: 'Supplier API', serviceVersion: '1.0.0', operations: [], message: null,
        }))
      }
      if (path.endsWith('/control/microcks/mode') && init?.method === 'POST') {
        mode = 'proxy'
        return new Response('{}')
      }
      throw new Error(`Unexpected ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const nativeConfirm = vi.spyOn(window, 'confirm').mockImplementation(() => {
      throw new Error('Native dialog must not be used')
    })
    const wrapper = mount(IntegrationsPage)
    await flushPromises()
    await wrapper.find('#tab-microcks').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('自訂設定')
    const proxyButton = wrapper.find('#panel-microcks').findAll('button').find(button => button.text() === '套用 Proxy')
    await proxyButton!.trigger('click')
    expect(wrapper.find('[role="alertdialog"]').text()).toContain('自訂設定也會被取代')
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/microcks/mode') && init?.method === 'POST')).toHaveLength(0)
    await wrapper.find('[data-testid="confirm-accept"]').trigger('click')
    await flushPromises()
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/microcks/mode') && init?.method === 'POST')).toHaveLength(1)
    expect(wrapper.text()).toContain('原生服務已讀回所選模式')
    expect(nativeConfirm).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})
