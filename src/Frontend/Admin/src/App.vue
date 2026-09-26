<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const menuOpen = ref(false)
watch(() => route.fullPath, () => { menuOpen.value = false })
</script>

<template>
  <div class="shell">
    <a class="skip-link" href="#main">跳至主要內容</a>
    <aside id="mobile-nav" class="sidebar" :class="{ open: menuOpen }" aria-label="管理導覽">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">C</div>
        <div><strong>Commerce Lab</strong><span>商務實驗室 · 管理</span></div>
      </div>
      <div class="nav-caption">工作空間</div>
      <nav aria-label="主要導覽">
        <RouterLink to="/" exact-active-class="active"><span class="nav-icon icon-grid" aria-hidden="true"></span>總覽</RouterLink>
        <RouterLink to="/products" active-class="active"><span class="nav-icon icon-box" aria-hidden="true"></span>商品主檔</RouterLink>
        <RouterLink to="/integrations" active-class="active"><span class="nav-icon icon-link" aria-hidden="true"></span>整合工具</RouterLink>
      </nav>
      <div class="sidebar-foot">
        <span>日常作業</span>
        <a href="/web/">開啟業務／倉管工作台 <span aria-hidden="true">↗</span></a>
      </div>
    </aside>
    <div class="workspace">
      <header class="topbar">
        <button class="menu-toggle" type="button" :aria-expanded="menuOpen" aria-controls="mobile-nav" aria-label="切換選單" @click="menuOpen = !menuOpen">
          <span></span><span></span><span></span>
        </button>
        <div class="breadcrumb"><span>商務實驗室</span><span aria-hidden="true">/</span><strong>{{ route.meta.title }}</strong></div>
        <a class="top-switch" href="/web/">前往作業工作台 <span aria-hidden="true">↗</span></a>
      </header>
      <main id="main" class="content">
        <RouterView />
      </main>
      <footer class="footer">本機實驗環境 · 狀態與資料均以服務回應為準</footer>
    </div>
    <button v-if="menuOpen" class="nav-scrim" type="button" aria-label="關閉選單" @click="menuOpen = false"></button>
  </div>
</template>
