import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './pages/Home.vue'
import Products from './pages/Products.vue'
import ProductDetail from './pages/ProductDetail.vue'
import Orders from './pages/Orders.vue'
import Inventory from './pages/Inventory.vue'
import Procurement from './pages/Procurement.vue'
import PurchaseDetail from './pages/PurchaseDetail.vue'
import './style.css'

const router = createRouter({ history: createWebHistory('/web/'), routes: [
  { path: '/', component: Home, meta: { title: '作業總覽' } },
  { path: '/products', component: Products, meta: { title: '商品查詢' } },
  { path: '/products/:id', component: ProductDetail, meta: { title: '商品明細' } },
  { path: '/orders/:id?', component: Orders, meta: { title: '銷售訂單' } },
  { path: '/inventory', component: Inventory, meta: { title: '庫存作業' } },
  { path: '/procurement', component: Procurement, meta: { title: '採購與收貨' } },
  { path: '/procurement/:id', component: PurchaseDetail, meta: { title: '採購單明細' } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
] })

createApp(App).use(router).mount('#app')
