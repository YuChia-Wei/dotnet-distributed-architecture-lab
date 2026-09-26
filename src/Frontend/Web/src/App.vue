<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const menuOpen = ref(false)
watch(() => route.fullPath, () => { menuOpen.value = false })
const links = [
  { to: '/', label: '作業總覽', icon: 'grid' },
  { to: '/products', label: '商品查詢', icon: 'search' },
  { to: '/orders', label: '銷售訂單', icon: 'receipt' },
  { to: '/inventory', label: '庫存作業', icon: 'boxes' },
  { to: '/procurement', label: '採購與收貨', icon: 'truck' },
]
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ open: menuOpen }">
      <RouterLink to="/" class="brand" aria-label="Commerce Lab 作業總覽">
        <span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 32 32"><path d="M6 22V10l10-6 10 6v12l-10 6zM6 10l10 6 10-6M16 16v12"/></svg></span>
        <span><strong>Commerce Lab</strong><small>商務實驗室 · 營運工作台</small></span>
      </RouterLink>
      <div class="nav-caption">工作區</div>
      <nav aria-label="主要導覽"><RouterLink v-for="item in links" :key="item.to" :to="item.to" class="nav-link" :class="{ active: item.to === '/' ? route.path === '/' : route.path.startsWith(item.to) }">
        <svg v-if="item.icon === 'grid'" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        <svg v-else-if="item.icon === 'search'" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>
        <svg v-else-if="item.icon === 'receipt'" viewBox="0 0 24 24"><path d="M5 3h14v18l-3-2-4 2-4-2-3 2zM8 8h8M8 12h8"/></svg>
        <svg v-else-if="item.icon === 'boxes'" viewBox="0 0 24 24"><path d="M3 8 8 5l5 3v6l-5 3-5-3zM13 8l5-3 4 3v6l-4 3-5-3M8 11v6M18 11v6"/></svg>
        <svg v-else viewBox="0 0 24 24"><path d="M2 6h12v11H2zM14 10h4l4 4v3h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/></svg>
        <span>{{ item.label }}</span><span class="nav-arrow" aria-hidden="true">›</span>
      </RouterLink></nav>
      <div class="sidebar-bottom"><span class="nav-caption">管理工具</span><a href="/admin/" class="nav-link"><svg viewBox="0 0 24 24"><path d="M12 3 4 7v10l8 4 8-4V7zM4 7l8 4 8-4M12 11v10"/></svg><span>管理後台</span><span class="nav-arrow" aria-hidden="true">↗</span></a></div>
    </aside>
    <div v-if="menuOpen" class="scrim" @click="menuOpen = false"></div>
    <div class="main-column">
      <header class="topbar"><button class="menu-toggle" type="button" :aria-expanded="menuOpen" aria-label="切換選單" @click="menuOpen = !menuOpen"><svg viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button><div class="topbar-context"><span class="eyebrow">內部營運 / OPERATIONS</span><strong>{{ route.meta.title }}</strong></div><span class="topbar-tag">本機實驗環境</span></header>
      <main id="main-content"><RouterView /></main>
    </div>
  </div>
</template>
