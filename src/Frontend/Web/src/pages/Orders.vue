<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { order, uuidValid, type OrderDetail } from '../api'
const route = useRoute(), router = useRouter(), id = ref(''), detail = ref<OrderDetail | null>(null), loading = ref(false), error = ref('')
let controller: AbortController | undefined
function search() { if (!uuidValid(id.value.trim())) { error.value = '請輸入有效的訂單 UUID。'; return } router.push(`/orders/${id.value.trim()}`) }
async function load() { controller?.abort(); detail.value = null; error.value = ''; id.value = typeof route.params.id === 'string' ? route.params.id : ''; if (!id.value) return; if (!uuidValid(id.value)) { error.value = '訂單 ID 格式不正確。'; return } const current = controller = new AbortController(); loading.value = true; try { const result = await order(id.value, current.signal); if (!current.signal.aborted) detail.value = result } catch (e) { if (!current.signal.aborted) error.value = (e as Error).message } finally { if (controller === current) loading.value = false } }
watch(() => route.params.id, load, { immediate: true }); onUnmounted(() => controller?.abort())
</script>
<template><div class="page"><div class="page-heading"><div><span class="eyebrow accent">SALES ORDERS</span><h1>銷售訂單</h1><p>依訂單 ID 查詢目前已提供的行項資料。服務未提供訂單清單或狀態。</p></div><RouterLink to="/products" class="button button-primary">從商品建立訂單</RouterLink></div>
  <section class="panel form-panel"><h2>查詢訂單</h2><form class="inline-form" @submit.prevent="search"><div class="field grow"><label for="order-id">訂單 ID</label><input id="order-id" v-model="id" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" autocomplete="off" /></div><button class="button button-primary" type="submit" :disabled="loading">查詢</button></form></section>
  <p v-if="error" class="notice error" role="alert">{{ error }} <button v-if="route.params.id" type="button" @click="load">重試</button></p><p v-else-if="loading" class="panel empty-state" role="status">正在查詢訂單…</p><section v-else-if="detail" class="panel"><div class="panel-heading"><div><span class="eyebrow accent">ORDER RECORD</span><h2>訂單行項</h2><code>{{ detail.orderId }}</code></div></div><p v-if="!detail.lineItems.length" class="empty-state">此訂單沒有可顯示的行項。</p><div v-else class="table-wrap"><table><thead><tr><th>商品 ID</th><th>數量</th><th>商品查詢</th></tr></thead><tbody><tr v-for="(line, index) in detail.lineItems" :key="`${line.productId}-${index}`"><td><code>{{ line.productId }}</code></td><td>{{ line.quantity }}</td><td><RouterLink :to="`/products/${line.productId}`" class="text-link">查看商品 →</RouterLink></td></tr></tbody></table></div></section>
</div></template>
