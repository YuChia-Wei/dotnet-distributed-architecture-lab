export interface Product { id: string; name: string; description: string; price: number }
export interface OrderDetail { orderId: string; lineItems: { productId: string; quantity: number }[] }
export interface InventoryStock { productId: string; availableQuantity: number }
export interface Quote { sku: string; name: string; unitPrice: number; currency: string; origin: string }
export type Provider = 'direct' | 'wiremock' | 'microcks'
export type PurchaseState = 'PendingSubmission' | 'SubmissionUnknown' | 'Accepted' | 'Rejected' | 'PartiallyReceived' | 'Received'
export interface PurchaseIdentity { clientRequestId: string; productId: string; supplierSku: string; quantity: number; unitPrice: number; currency: 'TWD'; provider: Provider }
export interface Receipt { receiptId: string; purchaseOrderId: string; productId: string; quantity: number; receivedAt: string }
export interface PurchaseOrder { id: string; identity: PurchaseIdentity; state: PurchaseState; supplierOrderId: string | null; receivedQuantity: number; version: number; createdAt: string; updatedAt: string; receipts: Receipt[] }
export interface ReceiveResult { order: PurchaseOrder; receipt: Receipt; created: boolean }

const record = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v)
export const uuidValid = (v: string) => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v) && v !== '00000000-0000-0000-0000-000000000000'
export const positiveInt = (v: number) => Number.isInteger(v) && v > 0 && v <= 2147483647
export const stockInt = (v: number) => Number.isInteger(v) && v >= 0 && v <= 2147483647
export const moneyValid = (v: number) => Number.isFinite(v) && v >= 0 && Number.isSafeInteger(Math.round(v * 100)) && Math.abs(Math.round(v * 100) - v * 100) < 1e-7
export const skuValid = (v: string) => /^[A-Za-z0-9_-]{1,64}$/.test(v)
export const money = (v: number) => `NT$ ${new Intl.NumberFormat('zh-TW', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v)}`
export const dateTime = (v: string) => { const d = new Date(v); return Number.isNaN(d.getTime()) ? v : new Intl.DateTimeFormat('zh-TW', { dateStyle: 'medium', timeStyle: 'short' }).format(d) }
export const newId = () => { if (!globalThis.crypto?.randomUUID) throw new Error('此瀏覽器無法產生安全識別碼，請使用 localhost 或 HTTPS。'); return globalThis.crypto.randomUUID() }

export class ApiError extends Error { constructor(message: string, public uncertain = false) { super(message) } }
function errorText(body: unknown): string {
  if (typeof body === 'string') return body.trim().slice(0, 240)
  if (record(body)) for (const key of ['message', 'detail', 'title', 'code']) if (typeof body[key] === 'string' && body[key]) return String(body[key]).slice(0, 240)
  return ''
}
export async function request<T>(path: `/api/${string}`, options: RequestInit = {}, valid: (v: unknown) => v is T): Promise<T> {
  const mutation = !!options.method && options.method !== 'GET'
  let response: Response
  try { response = await fetch(path, { ...options, headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers } }) }
  catch { throw new ApiError('連線中斷，請查詢最新資料確認結果。', mutation) }
  let raw: string
  try { raw = await response.text() }
  catch { throw new ApiError('回應中斷，請查詢最新資料確認結果。', mutation) }
  let body: unknown = undefined
  try { body = raw ? JSON.parse(raw) : undefined } catch { body = raw }
  if (!response.ok) throw new ApiError(response.status >= 500 ? '服務暫時無法完成請求，請查詢最新資料確認結果。' : errorText(body) || `服務回應 ${response.status}，請稍後重試。`, mutation && response.status >= 500)
  if (!valid(body)) throw new ApiError('服務回應格式不符合預期，請查詢最新資料確認結果。', mutation)
  return body
}
const isProduct = (v: unknown): v is Product => record(v) && uuidValid(String(v.id)) && typeof v.name === 'string' && typeof v.description === 'string' && typeof v.price === 'number' && moneyValid(v.price)
const isOrder = (v: unknown): v is OrderDetail => record(v) && uuidValid(String(v.orderId)) && Array.isArray(v.lineItems) && v.lineItems.every((x: unknown) => record(x) && uuidValid(String(x.productId)) && typeof x.quantity === 'number' && positiveInt(x.quantity))
const isStock = (v: unknown): v is InventoryStock => record(v) && uuidValid(String(v.productId)) && typeof v.availableQuantity === 'number' && stockInt(v.availableQuantity)
const isQuote = (v: unknown): v is Quote => record(v) && typeof v.sku === 'string' && typeof v.name === 'string' && typeof v.unitPrice === 'number' && moneyValid(v.unitPrice) && typeof v.currency === 'string' && typeof v.origin === 'string'
const states: PurchaseState[] = ['PendingSubmission','SubmissionUnknown','Accepted','Rejected','PartiallyReceived','Received']
const isReceipt = (v: unknown): v is Receipt => record(v) && uuidValid(String(v.receiptId)) && uuidValid(String(v.purchaseOrderId)) && uuidValid(String(v.productId)) && typeof v.quantity === 'number' && positiveInt(v.quantity) && typeof v.receivedAt === 'string'
const isPurchase = (v: unknown): v is PurchaseOrder => record(v) && uuidValid(String(v.id)) && record(v.identity) && uuidValid(String(v.identity.clientRequestId)) && uuidValid(String(v.identity.productId)) && skuValid(String(v.identity.supplierSku)) && typeof v.identity.quantity === 'number' && positiveInt(v.identity.quantity) && typeof v.identity.unitPrice === 'number' && moneyValid(v.identity.unitPrice) && v.identity.currency === 'TWD' && ['direct','wiremock','microcks'].includes(String(v.identity.provider)) && states.includes(v.state as PurchaseState) && typeof v.receivedQuantity === 'number' && stockInt(v.receivedQuantity) && typeof v.version === 'number' && typeof v.createdAt === 'string' && typeof v.updatedAt === 'string' && Array.isArray(v.receipts) && v.receipts.every(isReceipt)
export const products = (signal?: AbortSignal) => request('/api/products', { signal }, (v): v is Product[] => Array.isArray(v) && v.every(isProduct))
export const product = (id: string, signal?: AbortSignal) => request(`/api/products/${id}`, { signal }, isProduct)
export const order = (id: string, signal?: AbortSignal) => request(`/api/orders/${id}`, { signal }, isOrder)
export async function createOrder(input: { product: Product; quantity: number; operationId: string }) {
  if (!uuidValid(input.product.id) || !uuidValid(input.operationId) || !positiveInt(input.quantity) || !moneyValid(input.product.price)) throw new ApiError('請確認商品與數量。')
  const totalAmount = Math.round(input.product.price * input.quantity * 100) / 100
  if (!moneyValid(totalAmount)) throw new ApiError('訂單金額超出可用範圍。')
  return request('/api/orders', { method: 'POST', body: JSON.stringify({ operationId: input.operationId, orderDate: new Date().toISOString(), totalAmount, productId: input.product.id, productName: input.product.name, quantity: input.quantity }) }, (v): v is { isSuccess: true; value: { orderId: string }; errorMessage: null } => record(v) && v.isSuccess === true && record(v.value) && uuidValid(String(v.value.orderId)))
}
export const inventory = (id: string, signal?: AbortSignal) => request(`/api/inventory/product/${id}`, { signal }, isStock)
export const changeStock = (id: string, operation: 'initialize'|'increase'|'decrease'|'restock', stock: number) => {
  if (!uuidValid(id) || !stockInt(stock)) throw new ApiError('請輸入 0 至 2,147,483,647 的整數。')
  return request(`/api/inventory/product/${id}${operation === 'initialize' ? '' : `/${operation}`}`, { method: 'POST', body: JSON.stringify({ stock }) }, isStock)
}
export const quote = (provider: Provider, sku: string, signal?: AbortSignal) => {
  if (!skuValid(sku)) throw new ApiError('SKU 限 1–64 個英文字母、數字、底線或連字號。')
  return request(`/api/procurement/suppliers/${provider}/catalog/${sku}`, { signal }, isQuote)
}
export const purchases = (signal?: AbortSignal) => request('/api/procurement/purchase-orders', { signal }, (v): v is PurchaseOrder[] => Array.isArray(v) && v.every(isPurchase))
export const purchase = (id: string, signal?: AbortSignal) => request(`/api/procurement/purchase-orders/${id}`, { signal }, isPurchase)
export function createPurchase(identity: PurchaseIdentity) {
  if (!uuidValid(identity.clientRequestId) || !uuidValid(identity.productId) || !skuValid(identity.supplierSku) || !positiveInt(identity.quantity) || !moneyValid(identity.unitPrice) || !['direct','wiremock','microcks'].includes(identity.provider)) throw new ApiError('採購資料有誤，請檢查欄位。')
  return request('/api/procurement/purchase-orders', { method: 'POST', body: JSON.stringify(identity) }, isPurchase)
}
export const reconcile = (id: string) => request(`/api/procurement/purchase-orders/${id}/reconcile`, { method: 'POST' }, isPurchase)
export function receive(id: string, receiptId: string, quantity: number) {
  if (!uuidValid(id) || !uuidValid(receiptId) || !positiveInt(quantity)) throw new ApiError('請輸入有效的收貨數量。')
  return request(`/api/procurement/purchase-orders/${id}/receipts`, { method: 'POST', body: JSON.stringify({ receiptId, quantity }) }, (v): v is ReceiveResult => record(v) && isPurchase(v.order) && v.order.id === id && isReceipt(v.receipt) && v.receipt.receiptId === receiptId && v.receipt.purchaseOrderId === id && v.receipt.quantity === quantity && typeof v.created === 'boolean')
}
