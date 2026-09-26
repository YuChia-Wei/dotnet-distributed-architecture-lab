<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { isAbort, messageOf } from '../lib/api'
import {
  clearWireRequests, getMappings, getMicrocks, getSandboxControl, getSandboxOrders,
  getSandboxRequests, getWire, getWireRequests, modes, resetWire, setMicrocksMode,
  setSandboxDelay, setWireMode, validDelay, type MicrocksState, type Mode,
  type SandboxControl, type WireState,
} from '../lib/contracts'

type Tab = 'wire' | 'microcks' | 'sandbox'
const active = ref<Tab>('wire')
const wire = ref<WireState | null>(null)
const microcks = ref<MicrocksState | null>(null)
const sandbox = ref<SandboxControl | null>(null)
const mappings = ref<unknown>(null)
const wireRequests = ref<unknown>(null)
const sandboxOrders = ref<unknown[] | null>(null)
const sandboxRequests = ref<unknown[] | null>(null)
const delayInput = ref<number>(0)
const loading = ref<Record<Tab, boolean>>({ wire: false, microcks: false, sandbox: false })
const busy = ref<Record<Tab, boolean>>({ wire: false, microcks: false, sandbox: false })
const errors = ref<Record<Tab, string>>({ wire: '', microcks: '', sandbox: '' })
const feedback = ref<Record<Tab, string>>({ wire: '', microcks: '', sandbox: '' })
const wireController = ref<AbortController | null>(null)
const microcksController = ref<AbortController | null>(null)
const sandboxController = ref<AbortController | null>(null)
const modeLabel: Record<Mode, string> = { mock: 'Mock', proxy: 'Proxy', hybrid: 'Hybrid' }
const displayMode = (mode: string | null) => mode === null ? '未辨識' : modeLabel[mode as Mode] ?? mode
const displayStatus = (status: string) => ({
  ready: '已就緒', applying: '套用中', failed: '套用失敗', custom: '自訂設定',
  unconfigured: '尚未設定', unavailable: '無法連線',
})[status] ?? status
const formatted = (value: unknown) => JSON.stringify(value, null, 2)
const count = (value: unknown): number | null => {
  if (Array.isArray(value)) return value.length
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>
    if (Array.isArray(record.mappings)) return record.mappings.length
    if (Array.isArray(record.requests)) return record.requests.length
  }
  return null
}
const wireCount = computed(() => count(wireRequests.value))
const mappingCount = computed(() => count(mappings.value))

async function loadWire() {
  wireController.value?.abort()
  const current = new AbortController()
  wireController.value = current
  loading.value.wire = true
  errors.value.wire = ''
  const results = await Promise.allSettled([
    getWire(current.signal), getMappings(current.signal), getWireRequests(current.signal),
  ])
  if (current.signal.aborted) return
  const failed: string[] = []
  if (results[0].status === 'fulfilled') wire.value = results[0].value
  else if (!isAbort(results[0].reason)) failed.push(`狀態：${messageOf(results[0].reason)}`)
  if (results[1].status === 'fulfilled') mappings.value = results[1].value
  else if (!isAbort(results[1].reason)) failed.push(`規則：${messageOf(results[1].reason)}`)
  if (results[2].status === 'fulfilled') wireRequests.value = results[2].value
  else if (!isAbort(results[2].reason)) failed.push(`紀錄：${messageOf(results[2].reason)}`)
  errors.value.wire = failed.join('　')
  loading.value.wire = false
}

async function loadMicrocks() {
  microcksController.value?.abort()
  const current = new AbortController()
  microcksController.value = current
  loading.value.microcks = true
  errors.value.microcks = ''
  try {
    const result = await getMicrocks(current.signal)
    if (!current.signal.aborted) microcks.value = result
  } catch (error) {
    if (!current.signal.aborted && !isAbort(error)) errors.value.microcks = messageOf(error)
  } finally {
    if (!current.signal.aborted) loading.value.microcks = false
  }
}

async function loadSandbox() {
  sandboxController.value?.abort()
  const current = new AbortController()
  sandboxController.value = current
  loading.value.sandbox = true
  errors.value.sandbox = ''
  const results = await Promise.allSettled([
    getSandboxControl(current.signal), getSandboxOrders(current.signal),
    getSandboxRequests(current.signal),
  ])
  if (current.signal.aborted) return
  const failed: string[] = []
  if (results[0].status === 'fulfilled') {
    sandbox.value = results[0].value
    // Keep an unfinished operator edit intact when refreshing.
    if (document.activeElement?.id !== 'delay-input') delayInput.value = results[0].value.delayAfterCommitMs
  } else if (!isAbort(results[0].reason)) failed.push(`設定：${messageOf(results[0].reason)}`)
  if (results[1].status === 'fulfilled') sandboxOrders.value = results[1].value
  else if (!isAbort(results[1].reason)) failed.push(`訂單：${messageOf(results[1].reason)}`)
  if (results[2].status === 'fulfilled') sandboxRequests.value = results[2].value
  else if (!isAbort(results[2].reason)) failed.push(`請求：${messageOf(results[2].reason)}`)
  errors.value.sandbox = failed.join('　')
  loading.value.sandbox = false
}

function showTab(tab: Tab) {
  active.value = tab
  if (tab === 'wire' && !wire.value) void loadWire()
  if (tab === 'microcks' && !microcks.value) void loadMicrocks()
  if (tab === 'sandbox' && !sandbox.value) void loadSandbox()
}

function onTabKeydown(event: KeyboardEvent) {
  const tabs: Tab[] = ['wire', 'microcks', 'sandbox']
  const index = tabs.indexOf(active.value)
  let target: Tab | undefined
  if (event.key === 'ArrowRight') target = tabs[(index + 1) % tabs.length]
  if (event.key === 'ArrowLeft') target = tabs[(index + tabs.length - 1) % tabs.length]
  if (event.key === 'Home') target = tabs[0]
  if (event.key === 'End') target = tabs[tabs.length - 1]
  if (!target) return
  event.preventDefault()
  showTab(target)
  void nextTick(() => document.getElementById(`tab-${target}`)?.focus())
}

function refreshActive() {
  if (active.value === 'wire') void loadWire()
  else if (active.value === 'microcks') void loadMicrocks()
  else void loadSandbox()
}

async function changeWire(mode: Mode) {
  if (busy.value.wire) return
  if (!window.confirm(`套用 WireMock ${modeLabel[mode]} 模式？這會重建規則並清除現有請求紀錄。`)) return
  wireController.value?.abort()
  busy.value.wire = true
  errors.value.wire = ''
  feedback.value.wire = '正在套用；完成後將重新讀取服務狀態。'
  try {
    await setWireMode(mode)
    await loadWire()
    feedback.value.wire = !errors.value.wire && wire.value?.status === 'ready' && wire.value.mode === mode
      ? '服務已讀回所選模式。' : '操作已回應，但狀態尚未確認；請重新整理查核。'
  } catch (error) {
    errors.value.wire = messageOf(error)
    feedback.value.wire = '操作結果尚未確認；請重新讀取狀態。'
  } finally { busy.value.wire = false }
}

async function restoreWire() {
  if (busy.value.wire || !window.confirm('還原 WireMock 啟動模式？這會重建規則並清除請求紀錄。')) return
  wireController.value?.abort()
  busy.value.wire = true
  errors.value.wire = ''
  feedback.value.wire = '正在還原；完成後將重新讀取服務狀態。'
  try {
    await resetWire()
    await loadWire()
    feedback.value.wire = !errors.value.wire && wire.value?.status === 'ready'
      ? '啟動模式已由服務讀回。' : '操作已回應，但狀態尚未確認；請重新整理查核。'
  } catch (error) {
    errors.value.wire = messageOf(error)
    feedback.value.wire = '操作結果尚未確認；請重新讀取狀態。'
  } finally { busy.value.wire = false }
}

async function clearLogs() {
  if (busy.value.wire || !window.confirm('確定清除 WireMock 請求紀錄？此操作無法復原。')) return
  wireController.value?.abort()
  busy.value.wire = true
  errors.value.wire = ''
  feedback.value.wire = ''
  try {
    await clearWireRequests()
    await loadWire()
    feedback.value.wire = !errors.value.wire && wireCount.value === 0
      ? '請求紀錄已清除並讀回。' : '清除請求已回應；請檢查重新讀取的紀錄。'
  } catch (error) {
    errors.value.wire = messageOf(error)
    feedback.value.wire = '清除結果尚未確認；原紀錄仍保留於畫面供查核。'
  } finally { busy.value.wire = false }
}

async function changeMicrocks(mode: Mode) {
  if (busy.value.microcks) return
  if (!window.confirm(`匯入 Microcks ${modeLabel[mode]} 預設？這會覆蓋目前 Supplier API 規則，自訂設定也會被取代。`)) return
  microcksController.value?.abort()
  busy.value.microcks = true
  errors.value.microcks = ''
  feedback.value.microcks = '正在匯入預設並讀回原生服務設定。'
  try {
    await setMicrocksMode(mode)
    await loadMicrocks()
    feedback.value.microcks = !errors.value.microcks && microcks.value?.status === 'ready' && microcks.value.mode === mode
      ? '原生服務已讀回所選模式。' : '匯入請求已回應，但原生狀態尚未確認；請重新整理查核。'
  } catch (error) {
    errors.value.microcks = messageOf(error)
    feedback.value.microcks = '匯入結果尚未確認；請重新讀取原生狀態。'
  } finally { busy.value.microcks = false }
}

async function saveDelay() {
  if (busy.value.sandbox) return
  if (!validDelay(delayInput.value)) {
    errors.value.sandbox = '延遲須為 0 至 10000 的整數毫秒。'
    return
  }
  sandboxController.value?.abort()
  busy.value.sandbox = true
  errors.value.sandbox = ''
  feedback.value.sandbox = ''
  try {
    await setSandboxDelay(delayInput.value)
    await loadSandbox()
    feedback.value.sandbox = !errors.value.sandbox && sandbox.value?.delayAfterCommitMs === delayInput.value
      ? '延遲設定已由服務讀回。' : '設定已送出，但讀回結果尚未確認；請重新整理查核。'
  } catch (error) {
    errors.value.sandbox = messageOf(error)
    feedback.value.sandbox = '設定結果尚未確認；輸入值已保留。'
  } finally { busy.value.sandbox = false }
}

onMounted(() => { void loadWire() })
onUnmounted(() => {
  wireController.value?.abort()
  microcksController.value?.abort()
  sandboxController.value?.abort()
})
</script>

<template>
  <div class="page-head"><div><p class="eyebrow">DEVELOPER OPERATIONS</p><h1>整合工具</h1><p>從同一入口查核及調整供應商模擬環境。模式以服務讀回狀態為準。</p></div><button class="button ghost" type="button" :disabled="loading[active] || busy[active]" @click="refreshActive">{{ loading[active] ? '讀取中…' : '重新讀取' }}</button></div>
  <div class="tabs" role="tablist" aria-label="整合工具" @keydown="onTabKeydown">
    <button id="tab-wire" type="button" role="tab" :aria-selected="active === 'wire'" aria-controls="panel-wire" :tabindex="active === 'wire' ? 0 : -1" @click="showTab('wire')">WireMock.Net</button>
    <button id="tab-microcks" type="button" role="tab" :aria-selected="active === 'microcks'" aria-controls="panel-microcks" :tabindex="active === 'microcks' ? 0 : -1" @click="showTab('microcks')">Microcks</button>
    <button id="tab-sandbox" type="button" role="tab" :aria-selected="active === 'sandbox'" aria-controls="panel-sandbox" :tabindex="active === 'sandbox' ? 0 : -1" @click="showTab('sandbox')">Supplier Sandbox</button>
  </div>

  <section v-show="active === 'wire'" id="panel-wire" class="tab-panel" role="tabpanel" aria-labelledby="tab-wire">
    <div v-if="errors.wire" class="notice error" role="alert">{{ errors.wire }}</div>
    <div v-if="feedback.wire" class="notice info" role="status">{{ feedback.wire }}</div>
    <div class="integration-grid">
      <div class="panel">
        <div class="panel-heading"><div><p class="eyebrow">ENGINE 01</p><h2>WireMock.Net</h2></div><span class="pill" :class="!busy.wire && !errors.wire && wire?.status === 'ready' ? 'ready' : 'attention'">{{ busy.wire ? '操作中' : errors.wire ? '需查核' : wire ? displayStatus(wire.status) : '尚未讀取' }}</span></div>
        <p v-if="busy.wire || errors.wire" class="field-help">下列為上次讀取的資料；重新讀取後再確認目前模式。</p>
        <div class="detail-list"><div><span>目前模式</span><strong>{{ wire ? displayMode(wire.mode) : '—' }}</strong></div><div><span>固定上游</span><strong class="breakable">{{ wire?.upstream || '—' }}</strong></div><div><span>保存方式</span><strong>{{ wire?.persistence || '—' }}</strong></div></div>
        <p class="field-help">Mock 只處理固定範例；Hybrid 以規則優先，未命中時轉送上游。切換或還原會清除規則與請求紀錄。</p>
        <div class="mode-actions"><button v-for="mode in modes" :key="mode" class="button" :class="wire?.mode === mode && wire.status === 'ready' ? 'selected' : 'ghost'" type="button" :disabled="busy.wire || loading.wire" @click="changeWire(mode)">套用 {{ modeLabel[mode] }}</button></div>
        <div class="sub-actions"><button class="text-button" type="button" :disabled="busy.wire || loading.wire" @click="restoreWire">還原啟動模式</button></div>
      </div>
      <div class="panel">
        <div class="panel-heading"><div><p class="eyebrow">NATIVE STATE</p><h2>規則與紀錄</h2></div></div>
        <div class="raw-head"><h3>映射規則 <span v-if="mappingCount !== null" class="heading-count">{{ mappingCount }}</span></h3></div>
        <div v-if="mappings === null" class="empty-state">尚無可顯示的規則資料。</div><pre v-else class="json-panel">{{ formatted(mappings) }}</pre>
        <div class="raw-head"><h3>請求紀錄 <span v-if="wireCount !== null" class="heading-count">{{ wireCount }}</span></h3><button class="text-button danger" type="button" :disabled="busy.wire || loading.wire || wireRequests === null" @click="clearLogs">清除紀錄</button></div>
        <div v-if="wireRequests === null" class="empty-state">尚無可顯示的請求資料。</div><pre v-else class="json-panel">{{ formatted(wireRequests) }}</pre>
      </div>
    </div>
  </section>

  <section v-show="active === 'microcks'" id="panel-microcks" class="tab-panel" role="tabpanel" aria-labelledby="tab-microcks">
    <div v-if="errors.microcks" class="notice error" role="alert">{{ errors.microcks }}</div>
    <div v-if="feedback.microcks" class="notice info" role="status">{{ feedback.microcks }}</div>
    <div class="integration-grid">
      <div class="panel">
        <div class="panel-heading"><div><p class="eyebrow">ENGINE 02</p><h2>Microcks</h2></div><span class="pill" :class="!busy.microcks && !errors.microcks && microcks?.status === 'ready' ? 'ready' : 'attention'">{{ busy.microcks ? '操作中' : errors.microcks ? '需查核' : microcks ? displayStatus(microcks.status) : '尚未讀取' }}</span></div>
        <p v-if="busy.microcks || errors.microcks" class="field-help">下列為上次讀取的資料；重新讀取原生狀態後再確認模式。</p>
        <div class="detail-list"><div><span>原生狀態</span><strong>{{ microcks ? displayStatus(microcks.status) : '—' }}</strong></div><div><span>辨識模式</span><strong>{{ microcks ? displayMode(microcks.mode) : '—' }}</strong></div><div><span>服務版本</span><strong>{{ microcks ? `${microcks.serviceName} ${microcks.serviceVersion}` : '—' }}</strong></div><div><span>服務 ID</span><strong class="breakable">{{ microcks?.serviceId || '—' }}</strong></div></div>
        <p v-if="microcks?.message" class="notice info" role="status">{{ microcks.message }}</p>
        <p class="field-help">模式由原生操作的完整規則讀回辨識。自訂、未設定或無法連線時，不會標示預設已就緒。套用會匯入內建固定預設。</p>
        <div class="mode-actions"><button v-for="mode in modes" :key="mode" class="button" :class="microcks?.mode === mode && microcks.status === 'ready' ? 'selected' : 'ghost'" type="button" :disabled="busy.microcks || loading.microcks" @click="changeMicrocks(mode)">套用 {{ modeLabel[mode] }}</button></div>
      </div>
      <div class="panel">
        <div class="panel-heading"><div><p class="eyebrow">NATIVE OPERATIONS</p><h2>服務操作</h2></div><span class="heading-count">{{ microcks?.operations.length ?? '—' }}</span></div>
        <div v-if="!microcks?.operations.length" class="empty-state">目前沒有可顯示的原生操作。</div>
        <div v-else class="operation-list"><article v-for="(operation, index) in microcks.operations" :key="index" class="operation"><div><span class="method">{{ operation.method }}</span><strong>{{ operation.name }}</strong></div><p>Dispatcher：{{ operation.dispatcher ?? '未設定' }}</p><pre class="json-panel">{{ formatted(operation.dispatcherRules) }}</pre></article></div>
      </div>
    </div>
  </section>

  <section v-show="active === 'sandbox'" id="panel-sandbox" class="tab-panel" role="tabpanel" aria-labelledby="tab-sandbox">
    <div v-if="errors.sandbox" class="notice error" role="alert">{{ errors.sandbox }}</div>
    <div v-if="feedback.sandbox" class="notice info" role="status">{{ feedback.sandbox }}</div>
    <div class="integration-grid">
      <div class="panel">
        <div class="panel-heading"><div><p class="eyebrow">UPSTREAM</p><h2>Supplier Sandbox</h2></div><span class="pill" :class="!busy.sandbox && !errors.sandbox && sandbox ? 'ready' : 'attention'">{{ busy.sandbox ? '操作中' : errors.sandbox ? '需查核' : sandbox ? '可讀取' : '尚未讀取' }}</span></div>
        <p v-if="busy.sandbox || errors.sandbox" class="field-help">下列為上次讀取的資料；重新讀取後再確認目前延遲。</p>
        <div class="detail-list"><div><span>實際延遲</span><strong>{{ sandbox ? `${sandbox.delayAfterCommitMs} 毫秒` : '—' }}</strong></div><div><span>保存方式</span><strong>{{ sandbox?.persistence || '—' }}</strong></div></div>
        <form @submit.prevent="saveDelay"><label for="delay-input">訂單提交後延遲（毫秒）</label><input id="delay-input" v-model.number="delayInput" type="number" min="0" max="10000" step="1" :disabled="busy.sandbox" /><p class="field-help">用於驗證「供應商已提交、呼叫端等待回應」的情境。設定只在服務程序期間有效；0 代表不延遲。</p><button class="button primary" type="submit" :disabled="busy.sandbox">{{ busy.sandbox ? '套用中…' : '套用延遲' }}</button></form>
        <div class="callout"><strong>代理差異</strong><p>WireMock 未命中規則時可轉送固定上游；Microcks 僅對已匯入的操作套用其設定的代理行為。上游失敗不等於規則未命中。</p></div>
      </div>
      <div class="panel">
        <div class="panel-heading"><div><p class="eyebrow">RECENT ACTIVITY</p><h2>沙盒紀錄</h2></div></div>
        <div class="raw-head"><h3>近期訂單 <span v-if="sandboxOrders" class="heading-count">{{ sandboxOrders.length }}</span></h3></div><div v-if="sandboxOrders === null" class="empty-state">尚無可顯示的訂單資料。</div><pre v-else class="json-panel">{{ formatted(sandboxOrders) }}</pre>
        <div class="raw-head"><h3>近期請求 <span v-if="sandboxRequests" class="heading-count">{{ sandboxRequests.length }}</span></h3></div><div v-if="sandboxRequests === null" class="empty-state">尚無可顯示的請求資料。</div><pre v-else class="json-panel">{{ formatted(sandboxRequests) }}</pre>
      </div>
    </div>
  </section>
</template>
