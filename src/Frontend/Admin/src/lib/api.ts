export class ApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

type Method = 'GET' | 'POST' | 'PUT' | 'DELETE'

function textField(value: unknown): string | undefined {
  if (typeof value !== 'string' || !value.trim()) return undefined
  const plain = value.trim()
  return /[<>]|\n|\r|\bat\s+\S+:\d+|Exception|StackTrace/i.test(plain) ? undefined : plain
}

function errorFromBody(body: string): string | undefined {
  try {
    const data: unknown = JSON.parse(body)
    if (data && typeof data === 'object') {
      const details = data as Record<string, unknown>
      return textField(details.message) ?? textField(details.detail) ??
        textField(details.title) ?? textField(details.code)
    }
  } catch {
    return textField(body)
  }
  return undefined
}

export async function request(
  path: `/api/${string}`,
  options: { method?: Method; body?: unknown; signal?: AbortSignal; expectBody?: boolean } = {},
): Promise<unknown> {
  let response: Response
  try {
    response = await fetch(path, {
      method: options.method ?? 'GET',
      signal: options.signal,
      headers: options.body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new ApiError('無法連線至服務；請查核目前狀態。')
  }

  const raw = await response.text().catch(() => {
    throw new ApiError('無法讀取服務回應。', response.status)
  })
  if (!response.ok) {
    const detail = errorFromBody(raw)
    throw new ApiError((detail ?? `服務回應錯誤（HTTP ${response.status}）。`).slice(0, 240), response.status)
  }
  if (!raw.trim()) {
    if (options.expectBody) throw new ApiError('服務回應缺少預期資料。', response.status)
    return undefined
  }
  try {
    return JSON.parse(raw) as unknown
  } catch {
    throw new ApiError('服務回應格式不正確。', response.status)
  }
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value)
}

export function requireRecord(value: unknown): Record<string, unknown> {
  if (!isRecord(value)) throw new ApiError('服務回應格式不正確。')
  return value
}

export function requireArray(value: unknown): unknown[] {
  if (!Array.isArray(value)) throw new ApiError('服務回應格式不正確。')
  return value
}

export function messageOf(error: unknown): string {
  if (error instanceof ApiError) return error.message
  return '操作結果尚未確認；請重新讀取目前狀態。'
}

export function isAbort(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}
