// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import Inventory from './Inventory.vue'

const a = '11111111-1111-4111-8111-111111111111', b = '22222222-2222-4222-8222-222222222222'
const { getProducts, getInventory, changeStock } = vi.hoisted(() => ({ getProducts: vi.fn(), getInventory: vi.fn(), changeStock: vi.fn() }))
vi.mock('../api', async (importOriginal) => ({ ...(await importOriginal<typeof import('../api')>()), products: getProducts, inventory: getInventory, changeStock }))
afterEach(() => { vi.clearAllMocks() })

describe('inventory operator behavior', () => {
  it('does not let a stale product response replace the later selection', async () => {
    getProducts.mockResolvedValue([{ id: a, name: 'A', description: '', price: 1 }, { id: b, name: 'B', description: '', price: 1 }])
    let first!: (v: unknown) => void, second!: (v: unknown) => void
    getInventory.mockImplementationOnce(() => new Promise(resolve => { first = resolve })).mockImplementationOnce(() => new Promise(resolve => { second = resolve }))
    const wrapper = mount(Inventory)
    await flushPromises()
    await wrapper.get('#stock-product').setValue(a)
    await wrapper.get('#stock-product').setValue(b)
    second({ productId: b, availableQuantity: 8 }); await flushPromises()
    first({ productId: a, availableQuantity: 90 }); await flushPromises()
    expect(wrapper.text()).toContain('8 件')
    expect(wrapper.text()).not.toContain('90 件')
    wrapper.unmount()
  })

  it('keeps failed stock lookup unavailable and blocks malformed mutation quantity', async () => {
    getProducts.mockResolvedValue([{ id: a, name: 'A', description: '', price: 1 }])
    getInventory.mockRejectedValue(new Error('查詢失敗'))
    const wrapper = mount(Inventory)
    await flushPromises()
    await wrapper.get('#stock-product').setValue(a); await flushPromises()
    expect(wrapper.text()).toContain('庫存尚未確認')
    expect(wrapper.text()).toContain('查詢失敗')
    await wrapper.get('#stock-amount').setValue('-2')
    expect((wrapper.get('button[type="submit"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(changeStock).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})
