// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api'
import ProductDetail from './ProductDetail.vue'

const id = '11111111-1111-4111-8111-111111111111', key = '22222222-2222-4222-8222-222222222222'
const { getProduct, postOrder } = vi.hoisted(() => ({ getProduct: vi.fn(), postOrder: vi.fn() }))
vi.mock('../api', async (importOriginal) => ({ ...(await importOriginal<typeof import('../api')>()), product: getProduct, createOrder: postOrder, newId: () => key }))
afterEach(() => vi.clearAllMocks())

describe('sales order form', () => {
  it('blocks invalid quantity and a second submit while the first result is unknown', async () => {
    getProduct.mockResolvedValue({ id, name: '測試商品', description: '', price: 19.99 })
    let fail!: (reason: Error) => void
    postOrder.mockImplementation(() => new Promise((_resolve, reject) => { fail = reject }))
    const router = createRouter({ history: createMemoryHistory('/web/'), routes: [{ path: '/products/:id', component: ProductDetail }, { path: '/products', component: { template: '<div />' } }, { path: '/orders/:id', component: { template: '<div />' } }] })
    await router.push(`/products/${id}`); await router.isReady()
    const wrapper = mount(ProductDetail, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.get('#order-qty').setValue('0')
    expect((wrapper.get('button[type="submit"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(postOrder).not.toHaveBeenCalled()
    await wrapper.get('#order-qty').setValue('2')
    await wrapper.get('form').trigger('submit')
    await wrapper.get('form').trigger('submit')
    expect(postOrder).toHaveBeenCalledTimes(1)
    expect(postOrder.mock.calls[0][0]).toMatchObject({ operationId: key, quantity: 2 })
    fail(new ApiError('連線中斷', true)); await flushPromises()
    expect(wrapper.text()).toContain(key)
    await wrapper.get('form').trigger('submit')
    expect(postOrder).toHaveBeenCalledTimes(1)
    wrapper.unmount()
  })
})
