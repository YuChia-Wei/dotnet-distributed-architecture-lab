import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import OverviewPage from './pages/OverviewPage.vue'
import ProductsPage from './pages/ProductsPage.vue'
import IntegrationsPage from './pages/IntegrationsPage.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    { path: '/', component: OverviewPage, meta: { title: '總覽' } },
    { path: '/products', component: ProductsPage, meta: { title: '商品主檔' } },
    { path: '/integrations', component: IntegrationsPage, meta: { title: '整合工具' } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

createApp(App).use(router).mount('#app')
