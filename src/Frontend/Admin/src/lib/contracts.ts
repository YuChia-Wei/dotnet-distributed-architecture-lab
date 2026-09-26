import { ApiError, requireArray, requireRecord, request } from './api'

export interface Product {
  id: string
  name: string
  description: string
  price: number
}

export interface ProductDraft {
  name: string
  description: string
  price: number
}

export type Mode = 'mock' | 'proxy' | 'hybrid'
export const modes: Mode[] = ['mock', 'proxy', 'hybrid']

export interface EngineState {
  mode: string | null
  status: string
  message?: string | null
}

export interface WireState extends EngineState {
  upstream: string
  persistence: string
}

export interface MicrocksState extends EngineState {
  serviceId: string | null
  serviceName: string
  serviceVersion: string
  operations: { name: string; method: string; dispatcher: string | null; dispatcherRules: unknown }[]
}

export interface SandboxControl {
  delayAfterCommitMs: number
  persistence: string
}

const products = '/api/products'
const mock = '/api/admin/supplier-mock/control'
const sandbox = '/api/admin/supplier-sandbox/sandbox'

export function parseProduct(value: unknown): Product {
  const data = requireRecord(value)
  if (typeof data.id !== 'string' || !data.id ||
      typeof data.name !== 'string' ||
      typeof data.description !== 'string' ||
      typeof data.price !== 'number' || !Number.isFinite(data.price)) {
    throw new ApiError('商品資料格式不正確。')
  }
  return { id: data.id, name: data.name, description: data.description, price: data.price }
}

export function validateProduct(draft: ProductDraft): string | null {
  if (!draft.name.trim()) return '請輸入商品名稱。'
  if (!Number.isFinite(draft.price) || draft.price < 0 ||
      Math.abs(Math.round(draft.price * 100) - draft.price * 100) > 1e-7) {
    return '價格須為非負數，最多兩位小數。'
  }
  return null
}

export async function listProducts(signal?: AbortSignal): Promise<Product[]> {
  return requireArray(await request(products, { signal, expectBody: true })).map(parseProduct)
}

export async function createProduct(draft: ProductDraft): Promise<Product> {
  const result = await request(products, { method: 'POST', body: draft, expectBody: true })
  return parseProduct(result)
}

export async function updateProduct(id: string, draft: ProductDraft): Promise<void> {
  await request(`${products}/${encodeURIComponent(id)}`, { method: 'PUT', body: draft })
}

export async function deleteProduct(id: string): Promise<void> {
  await request(`${products}/${encodeURIComponent(id)}`, { method: 'DELETE' })
}

function parseEngine(value: unknown): EngineState {
  const data = requireRecord(value)
  if ((data.mode !== null && typeof data.mode !== 'string') || typeof data.status !== 'string') {
    throw new ApiError('引擎狀態格式不正確。')
  }
  return { mode: data.mode as string | null, status: data.status,
    message: typeof data.message === 'string' ? data.message : null }
}

export function parseWire(value: unknown): WireState {
  const data = requireRecord(value)
  return { ...parseEngine(value),
    upstream: typeof data.upstream === 'string' ? data.upstream : '',
    persistence: typeof data.persistence === 'string' ? data.persistence : '' }
}

export function parseMicrocks(value: unknown): MicrocksState {
  const data = requireRecord(value)
  const base = parseEngine(value)
  if (typeof data.serviceName !== 'string' || typeof data.serviceVersion !== 'string' ||
      (data.serviceId !== null && typeof data.serviceId !== 'string') ||
      !Array.isArray(data.operations)) throw new ApiError('Microcks 狀態格式不正確。')
  const operations = data.operations.map((item) => {
    const op = requireRecord(item)
    if (typeof op.name !== 'string' || typeof op.method !== 'string' ||
        (op.dispatcher !== null && typeof op.dispatcher !== 'string')) {
      throw new ApiError('Microcks 操作格式不正確。')
    }
    return { name: op.name, method: op.method, dispatcher: op.dispatcher as string | null,
      dispatcherRules: op.dispatcherRules }
  })
  return { ...base, serviceId: data.serviceId as string | null,
    serviceName: data.serviceName, serviceVersion: data.serviceVersion, operations }
}

export const getWire = async (signal?: AbortSignal): Promise<WireState> =>
  parseWire(await request(`${mock}/state`, { signal, expectBody: true }))
export const getMicrocks = async (signal?: AbortSignal): Promise<MicrocksState> =>
  parseMicrocks(await request(`${mock}/microcks/state`, { signal, expectBody: true }))
export const setWireMode = async (mode: Mode): Promise<void> => {
  await request(`${mock}/mode`, { method: 'POST', body: { mode }, expectBody: true })
}
export const resetWire = async (): Promise<void> => {
  await request(`${mock}/reset`, { method: 'POST', expectBody: true })
}
export const setMicrocksMode = async (mode: Mode): Promise<void> => {
  await request(`${mock}/microcks/mode`, { method: 'POST', body: { mode }, expectBody: true })
}
export const getMappings = (signal?: AbortSignal): Promise<unknown> =>
  request(`${mock}/mappings`, { signal, expectBody: true })
export const getWireRequests = (signal?: AbortSignal): Promise<unknown> =>
  request(`${mock}/requests`, { signal, expectBody: true })
export const clearWireRequests = async (): Promise<void> => {
  await request(`${mock}/requests`, { method: 'DELETE' })
}
export const getSandboxOrders = (signal?: AbortSignal): Promise<unknown[]> =>
  request(`${sandbox}/orders`, { signal, expectBody: true }).then(requireArray)
export const getSandboxRequests = (signal?: AbortSignal): Promise<unknown[]> =>
  request(`${sandbox}/requests`, { signal, expectBody: true }).then(requireArray)

export function parseSandboxControl(value: unknown): SandboxControl {
  const data = requireRecord(value)
  if (!Number.isInteger(data.delayAfterCommitMs) ||
      typeof data.persistence !== 'string') throw new ApiError('沙盒設定格式不正確。')
  return { delayAfterCommitMs: data.delayAfterCommitMs as number, persistence: data.persistence }
}

export const getSandboxControl = async (signal?: AbortSignal): Promise<SandboxControl> =>
  parseSandboxControl(await request(`${sandbox}/control`, { signal, expectBody: true }))
export const setSandboxDelay = async (delayAfterCommitMs: number): Promise<SandboxControl> =>
  parseSandboxControl(await request(`${sandbox}/control`, {
    method: 'PUT', body: { delayAfterCommitMs }, expectBody: true,
  }))

export function validDelay(value: number): boolean {
  return Number.isInteger(value) && value >= 0 && value <= 10000
}
