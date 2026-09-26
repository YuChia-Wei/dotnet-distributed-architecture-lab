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
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const wrapper = mount(IntegrationsPage)
    await flushPromises()

    const mockButton = wrapper.findAll('button').find(button => button.text().includes('套用 Mock'))
    expect(mockButton).toBeDefined()
    await mockButton!.trigger('click')
    expect(confirm).toHaveBeenCalledOnce()
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/mode') && init?.method === 'POST')).toHaveLength(0)

    confirm.mockReturnValue(true)
    await mockButton!.trigger('click')
    expect(mockButton!.attributes('disabled')).toBeDefined()
    await mockButton!.trigger('click')
    expect(fetchMock.mock.calls.filter(([path, init]) =>
      String(path).endsWith('/control/mode') && init?.method === 'POST')).toHaveLength(1)

    currentMode = 'mock'
    finishPost?.(new Response('{}', { status: 200 }))
    await flushPromises()
    expect(wrapper.text()).toContain('服務已讀回所選模式')
    wrapper.unmount()
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
})
