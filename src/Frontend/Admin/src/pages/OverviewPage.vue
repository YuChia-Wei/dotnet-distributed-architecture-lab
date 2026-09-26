<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { getMicrocks, getSandboxControl, getWire, listProducts } from '../lib/contracts'
import { isAbort, messageOf } from '../lib/api'

type Probe = { label: string; state: 'loading' | 'ready' | 'attention' | 'error'; detail: string }
const probes = reactive<Probe[]>([
  { label: '商品服務', state: 'loading', detail: '讀取中' },
  { label: 'WireMock', state: 'loading', detail: '讀取中' },
  { label: 'Microcks', state: 'loading', detail: '讀取中' },
  { label: '供應商沙盒', state: 'loading', detail: '讀取中' },
])
const controller = ref<AbortController | null>(null)
const loading = ref(false)

async function refresh() {
  controller.value?.abort()
  const current = new AbortController()
  controller.value = current
  loading.value = true
  probes.forEach(probe => { probe.state = 'loading'; probe.detail = '讀取中' })
  const checks = [
    listProducts(current.signal).then(items => ({ state: 'ready' as const, detail: `取得 ${items.length} 筆商品` })),
    getWire(current.signal).then(item => ({ state: item.status === 'ready' ? 'ready' as const : 'attention' as const, detail: `${item.status} · ${item.mode ?? '未知模式'}` })),
    getMicrocks(current.signal).then(item => ({ state: item.status === 'ready' ? 'ready' as const : 'attention' as const, detail: `${item.status} · ${item.mode ?? '未辨識模式'}` })),
    getSandboxControl(current.signal).then(item => ({ state: 'ready' as const, detail: `提交後延遲 ${item.delayAfterCommitMs} 毫秒` })),
  ]
  await Promise.all(checks.map(async (check, index) => {
    try {
      const result = await check
      if (!current.signal.aborted) Object.assign(probes[index], result)
    } catch (error) {
      if (!current.signal.aborted && !isAbort(error)) Object.assign(probes[index], { state: 'error', detail: messageOf(error) })
    }
  }))
  if (!current.signal.aborted) loading.value = false
}

onMounted(() => { void refresh() })
onUnmounted(() => controller.value?.abort())
</script>

<template>
  <div class="page-head"><div><p class="eyebrow">ADMIN WORKSPACE</p><h1>管理總覽</h1><p>維護商品主檔，並查看兩個模擬引擎與沙盒的實際狀態。</p></div><button class="button ghost" type="button" :disabled="loading" @click="refresh">{{ loading ? '讀取中…' : '重新讀取狀態' }}</button></div>
  <section class="section">
    <div class="section-title"><h2>服務狀態</h2><p>每次由同源 API 讀取；「可用」只代表該次狀態查詢成功。</p></div>
    <div class="status-grid">
      <div v-for="probe in probes" :key="probe.label" class="status-card">
        <div class="status-card-top"><strong>{{ probe.label }}</strong><span class="pill" :class="probe.state">{{ probe.state === 'ready' ? '可讀取' : probe.state === 'loading' ? '讀取中' : probe.state === 'attention' ? '需檢查' : '無法讀取' }}</span></div>
        <p :role="probe.state === 'error' ? 'alert' : 'status'">{{ probe.detail }}</p>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="section-title"><h2>常用入口</h2><p>依工作責任前往維護或日常作業。</p></div>
    <div class="shortcut-grid">
      <RouterLink class="shortcut" to="/products"><span class="shortcut-index">01</span><strong>商品主檔</strong><span>新增、修改及刪除商品資料</span><span class="shortcut-arrow" aria-hidden="true">↗</span></RouterLink>
      <RouterLink class="shortcut" to="/integrations"><span class="shortcut-index">02</span><strong>整合工具</strong><span>管理 WireMock、Microcks 與沙盒</span><span class="shortcut-arrow" aria-hidden="true">↗</span></RouterLink>
      <a class="shortcut" href="/web/inventory"><span class="shortcut-index">03</span><strong>庫存作業</strong><span>前往日常業務／倉管工作台</span><span class="shortcut-arrow" aria-hidden="true">↗</span></a>
      <a class="shortcut" href="/web/procurement"><span class="shortcut-index">04</span><strong>採購與收貨</strong><span>前往採購訂單及收貨作業</span><span class="shortcut-arrow" aria-hidden="true">↗</span></a>
    </div>
  </section>
</template>
