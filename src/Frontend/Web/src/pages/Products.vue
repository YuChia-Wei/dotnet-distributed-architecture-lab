<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { products, money, type Product } from '../api'
const rows = ref<Product[]>([]), query = ref(''), loading = ref(false), error = ref('')
let controller: AbortController | undefined
async function load() { controller?.abort(); const current = controller = new AbortController(); loading.value = true; error.value = ''; try { const result = await products(current.signal); if (!current.signal.aborted) rows.value = result } catch (e) { if (!current.signal.aborted) error.value = (e as Error).message } finally { if (controller === current) loading.value = false } }
const filtered = computed(() => rows.value.filter(p => `${p.name} ${p.description} ${p.id}`.toLocaleLowerCase().includes(query.value.trim().toLocaleLowerCase())))
onMounted(load); onUnmounted(() => controller?.abort())
</script>
<template><div class="page"><div class="page-heading"><div><span class="eyebrow accent">PRODUCT LOOKUP</span><h1>商品查詢</h1><p>從目前商品清單挑選作業項目，價格為服務回傳的單價快照。</p></div><button class="button button-secondary" type="button" :disabled="loading" @click="load">重新整理</button></div>
  <div class="panel"><div class="panel-toolbar"><label class="search-field"><span class="sr-only">搜尋商品名稱、描述或 ID</span><svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></svg><input v-model="query" type="search" placeholder="搜尋名稱、描述或商品 ID" /></label><span class="result-count" aria-live="polite">{{ loading ? '讀取中…' : error ? '尚未取得清單' : `顯示 ${filtered.length} / ${rows.length} 項` }}</span></div>
    <p v-if="error" class="notice error" role="alert">{{ error }} <button type="button" @click="load">重試</button></p><p v-else-if="loading" class="empty-state" role="status">正在讀取商品…</p><p v-else-if="!filtered.length" class="empty-state">{{ rows.length ? '找不到符合搜尋的商品。' : '目前沒有商品。請到管理後台新增商品。' }}</p>
    <div v-else class="table-wrap"><table><thead><tr><th>商品</th><th>描述</th><th>單價</th><th><span class="sr-only">查看</span></th></tr></thead><tbody><tr v-for="p in filtered" :key="p.id"><td><span class="item-name">{{ p.name }}</span><span class="item-id">{{ p.id }}</span></td><td>{{ p.description || '—' }}</td><td class="money-cell">{{ money(p.price) }}</td><td><RouterLink :to="`/products/${p.id}`" class="text-link">查看與下單 →</RouterLink></td></tr></tbody></table></div>
  </div></div></template>
