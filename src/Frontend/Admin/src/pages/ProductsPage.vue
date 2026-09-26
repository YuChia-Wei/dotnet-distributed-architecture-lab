<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { createProduct, deleteProduct, listProducts, updateProduct, validateProduct, type Product, type ProductDraft } from '../lib/contracts'
import { ApiError, isAbort, messageOf } from '../lib/api'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const items = ref<Product[]>([])
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const feedback = ref('')
const filter = ref('')
const editing = ref<Product | null>(null)
const pendingDelete = ref<Product | null>(null)
const draft = reactive<ProductDraft>({ name: '', description: '', price: 0 })
let controller: AbortController | null = null
const filtered = computed(() => items.value.filter(item =>
  `${item.name} ${item.description} ${item.id}`.toLocaleLowerCase().includes(filter.value.trim().toLocaleLowerCase())))
const money = (value: number) => new Intl.NumberFormat('zh-TW', { maximumFractionDigits: 2 }).format(value)
const deleteDescription = computed(() => pendingDelete.value
  ? `確定刪除「${pendingDelete.value.name}」？此操作會移除商品主檔。` : '')

async function refresh() {
  controller?.abort()
  const current = new AbortController()
  controller = current
  loading.value = true
  error.value = ''
  try {
    const result = await listProducts(current.signal)
    if (!current.signal.aborted) items.value = result
  } catch (cause) {
    if (!current.signal.aborted && !isAbort(cause)) error.value = messageOf(cause)
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}

function resetForm() {
  editing.value = null
  draft.name = ''
  draft.description = ''
  draft.price = 0
}

function edit(item: Product) {
  editing.value = item
  draft.name = item.name
  draft.description = item.description
  draft.price = item.price
  feedback.value = ''
  document.getElementById('product-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function save() {
  if (busy.value) return
  feedback.value = ''
  const validation = validateProduct(draft)
  if (validation) { error.value = validation; return }
  error.value = ''
  busy.value = true
  controller?.abort()
  const payload = { name: draft.name.trim(), description: draft.description.trim(), price: draft.price }
  try {
    if (editing.value) {
      await updateProduct(editing.value.id, payload)
      feedback.value = '商品修改已提交；正在重新讀取主檔。'
    } else {
      const created = await createProduct(payload)
      feedback.value = `商品已建立：${created.id}；正在重新讀取主檔。`
    }
    await refresh()
    if (!error.value) {
      resetForm()
      feedback.value = feedback.value.replace('正在重新讀取主檔。', '主檔已重新讀取。')
    }
  } catch (cause) {
    const definiteRejection = cause instanceof ApiError && cause.status !== undefined &&
      cause.status >= 400 && cause.status < 500
    error.value = definiteRejection ? messageOf(cause) :
      `${messageOf(cause)} ${editing.value ? '請先重新讀取主檔確認修改結果。' : '建立結果尚未確認；請先重新讀取商品主檔，避免重複建立。'}`
  } finally { busy.value = false }
}

function askRemove(item: Product) {
  if (busy.value || pendingDelete.value) return
  pendingDelete.value = item
}

function confirmRemove() {
  const item = pendingDelete.value
  if (!item || busy.value) return
  pendingDelete.value = null
  void remove(item)
}

async function remove(item: Product) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  feedback.value = ''
  controller?.abort()
  try {
    await deleteProduct(item.id)
    feedback.value = `已提交刪除 ${item.id}；正在重新讀取主檔。`
    if (editing.value?.id === item.id) resetForm()
    await refresh()
    if (!error.value) feedback.value = '已刪除商品，主檔已重新讀取。'
  } catch (cause) {
    error.value = messageOf(cause)
  } finally { busy.value = false }
}

onMounted(() => { void refresh() })
onUnmounted(() => controller?.abort())
</script>

<template>
  <div class="page-head"><div><p class="eyebrow">MASTER DATA</p><h1>商品主檔</h1><p>管理商品名稱、描述與價格。庫存及採購作業請使用<a href="/web/">作業工作台</a>。</p></div><button class="button ghost" type="button" :disabled="loading || busy" @click="refresh">{{ loading ? '讀取中…' : '重新整理' }}</button></div>
  <div v-if="error" class="notice error" role="alert">{{ error }}</div>
  <div v-if="feedback" class="notice success" role="status">{{ feedback }}</div>
  <div class="product-layout">
    <section id="product-form" class="panel">
      <div class="panel-heading"><div><p class="eyebrow">PRODUCT EDITOR</p><h2>{{ editing ? '修改商品' : '新增商品' }}</h2></div><span v-if="editing" class="pill attention">編輯中</span></div>
      <p v-if="editing" class="muted id-line">商品 ID：{{ editing.id }}</p>
      <form @submit.prevent="save">
        <label for="product-name">商品名稱 <span class="required">*</span></label>
        <input id="product-name" v-model="draft.name" type="text" maxlength="200" autocomplete="off" required :disabled="busy" />
        <label for="product-description">描述</label>
        <textarea id="product-description" v-model="draft.description" rows="4" maxlength="2000" :disabled="busy"></textarea>
        <label for="product-price">價格（TWD，實驗顯示） <span class="required">*</span></label>
        <input id="product-price" v-model.number="draft.price" type="number" min="0" step="0.01" required :disabled="busy" />
        <p class="field-help">價格由現有商品 API 保存；TWD 為本工作台的顯示慣例。</p>
        <div class="form-actions"><button class="button primary" type="submit" :disabled="busy">{{ busy ? '提交中…' : editing ? '儲存修改' : '建立商品' }}</button><button class="button quiet" type="button" :disabled="busy" @click="resetForm">{{ editing ? '取消編輯' : '清空' }}</button></div>
      </form>
    </section>
    <section class="panel list-panel">
      <div class="panel-heading"><div><p class="eyebrow">PRODUCT LIST</p><h2>現有商品 <span class="heading-count">{{ items.length }}</span></h2></div></div>
      <label for="product-search">搜尋商品</label>
      <input id="product-search" v-model="filter" type="search" placeholder="名稱、描述或 ID" />
      <p class="field-help">顯示 {{ filtered.length }} / {{ items.length }} 筆已讀取商品。</p>
      <div v-if="loading && !items.length" class="empty-state" role="status">正在讀取商品…</div>
      <div v-else-if="!loading && !error && !items.length" class="empty-state">目前沒有商品。可使用左側表單建立第一筆。</div>
      <div v-else-if="!filtered.length" class="empty-state">沒有符合搜尋條件的商品。</div>
      <div v-else class="table-scroll">
        <table><thead><tr><th scope="col">商品</th><th scope="col">價格</th><th scope="col">操作</th></tr></thead>
          <tbody><tr v-for="item in filtered" :key="item.id"><td><strong>{{ item.name }}</strong><span class="table-detail">{{ item.description || '無描述' }}</span><span class="table-id">{{ item.id }}</span></td><td class="amount">NT$ {{ money(item.price) }}</td><td><div class="row-actions"><button class="text-button" type="button" :disabled="busy" :aria-label="`編輯 ${item.name}`" @click="edit(item)">編輯</button><button class="text-button danger" type="button" :disabled="busy" :aria-label="`刪除 ${item.name}`" @click="askRemove(item)">刪除</button></div></td></tr></tbody>
        </table>
      </div>
    </section>
  </div>
  <ConfirmDialog :open="pendingDelete !== null" title="刪除商品" :description="deleteDescription" confirm-text="確認刪除" @cancel="pendingDelete = null" @confirm="confirmRemove" />
</template>
