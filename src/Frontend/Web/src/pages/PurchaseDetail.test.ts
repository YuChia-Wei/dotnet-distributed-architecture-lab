// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api'
import PurchaseDetail from './PurchaseDetail.vue'

const a = '11111111-1111-4111-8111-111111111111', b = '22222222-2222-4222-8222-222222222222', rid = '33333333-3333-4333-8333-333333333333'
const { getPurchase, sendReceipt } = vi.hoisted(() => ({ getPurchase: vi.fn(), sendReceipt: vi.fn() }))
vi.mock('../api', async (importOriginal) => ({ ...(await importOriginal<typeof import('../api')>()), purchase: getPurchase, receive: sendReceipt, newId: () => rid }))
const record = (id: string) => ({ id, identity: { clientRequestId: id, productId: b, supplierSku: 'REAL-001', quantity: 4, unitPrice: 19.99, currency: 'TWD', provider: 'direct' }, state: 'Accepted', supplierOrderId: 'supplier-1', receivedQuantity: 0, version: 1, createdAt: '2026-09-26T00:00:00Z', updatedAt: '2026-09-26T00:00:00Z', receipts: [] })
async function setup() { const router = createRouter({ history: createMemoryHistory('/web/'), routes: [{ path: '/procurement/:id', component: PurchaseDetail }, { path: '/procurement', component: { template: '<div />' } }] }); await router.push(`/procurement/${a}`); await router.isReady(); const wrapper = mount(PurchaseDetail, { global: { plugins: [router] } }); await flushPromises(); return { wrapper, router } }
afterEach(() => vi.clearAllMocks())

describe('purchase detail identity and readback', () => {
  it('ignores a late read from another purchase after route change', async () => {
    let first!: (v: unknown) => void
    getPurchase.mockImplementationOnce(() => new Promise(resolve => { first = resolve })).mockResolvedValueOnce(record(b))
    const { wrapper, router } = await setup()
    await router.push(`/procurement/${b}`); await flushPromises()
    first(record(a)); await flushPromises()
    expect(wrapper.text()).toContain(b)
    expect(wrapper.text()).not.toContain('11111111-1111-4111-8111-111111111111')
    wrapper.unmount()
  })

  it('does not carry an uncertain receipt identity to another purchase', async () => {
    getPurchase.mockImplementation(id => Promise.resolve(record(id)))
    sendReceipt.mockRejectedValue(new ApiError('回應中斷', true))
    const { wrapper, router } = await setup()
    await wrapper.get('#receipt-qty').setValue('2')
    await wrapper.get('form').trigger('submit'); await flushPromises()
    expect(wrapper.text()).toContain(rid)
    expect(sendReceipt).toHaveBeenCalledWith(a, rid, 2)
    await router.push(`/procurement/${b}`); await flushPromises()
    expect(wrapper.text()).not.toContain(rid)
    expect(wrapper.findAll('button').some(button => button.text().includes('相同 ID 重送'))).toBe(false)
    wrapper.unmount()
  })
})
