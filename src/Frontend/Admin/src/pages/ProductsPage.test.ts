// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ProductsPage from './ProductsPage.vue'

afterEach(() => vi.restoreAllMocks())

describe('product deletion', () => {
  it('keeps the row until explicit in-page confirmation and reads back after deletion', async () => {
    let products = [{ id: 'd77fa33a-4d40-49ce-9a8a-1138c152802a',
      name: '測試商品', description: '可刪除', price: 12 }]
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const path = String(input)
      if (path === '/api/products' && init?.method === 'GET') {
        return new Response(JSON.stringify(products), { status: 200 })
      }
      if (path.endsWith(products[0]?.id ?? 'not-present') && init?.method === 'DELETE') {
        products = []
        return new Response('', { status: 200 })
      }
      throw new Error(`Unexpected ${path}`)
    })
    vi.stubGlobal('fetch', fetchMock)
    const nativeConfirm = vi.spyOn(window, 'confirm').mockImplementation(() => {
      throw new Error('Native dialog must not be used')
    })
    const host = document.createElement('div')
    document.body.appendChild(host)
    const wrapper = mount(ProductsPage, { attachTo: host })
    await flushPromises()

    const deleteButton = wrapper.find('button[aria-label="刪除 測試商品"]')
    await deleteButton.trigger('click')
    await deleteButton.trigger('click')
    expect(wrapper.findAll('[role="alertdialog"]')).toHaveLength(1)
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'DELETE')).toHaveLength(0)
    await wrapper.find('[data-testid="confirm-cancel"]').trigger('click')
    expect(wrapper.text()).toContain('測試商品')
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'DELETE')).toHaveLength(0)

    await deleteButton.trigger('click')
    await wrapper.find('[data-testid="confirm-accept"]').trigger('click')
    await flushPromises()
    expect(fetchMock.mock.calls.filter(([, init]) => init?.method === 'DELETE')).toHaveLength(1)
    expect(wrapper.text()).toContain('已刪除商品')
    expect(wrapper.find('button[aria-label="刪除 測試商品"]').exists()).toBe(false)
    expect(nativeConfirm).not.toHaveBeenCalled()
    wrapper.unmount()
    host.remove()
  })
})
