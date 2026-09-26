<template>
  <div class="page home-page">
    <div class="hero"><div><span class="eyebrow hero-eyebrow">COMMERCE LAB / DAILY OPERATIONS</span><h1>把今天的作業，<br><em>處理得更清楚。</em></h1><p>從商品查詢、銷售訂單到庫存、採購與實際收貨，依照手上的工作開始。</p><RouterLink to="/products" class="button button-light">開始查詢商品 <span aria-hidden="true">↗</span></RouterLink></div><div class="hero-graphic" aria-hidden="true"><div class="graphic-grid"></div><div class="graphic-card graphic-a"><span>01</span><i></i><i></i></div><div class="graphic-card graphic-b"><span>02</span><i></i><i></i></div><div class="graphic-orbit"></div></div></div>
    <div class="section-heading"><div><span class="eyebrow accent">QUICK ACCESS</span><h2>常用作業</h2></div><p>選擇任務並讀取目前服務資料</p></div>
    <div class="shortcut-grid">
      <RouterLink to="/products" class="shortcut"><span class="shortcut-icon">01</span><span><strong>商品查詢</strong><small>搜尋現有商品並查看明細</small></span><b aria-hidden="true">↗</b></RouterLink>
      <RouterLink to="/orders" class="shortcut"><span class="shortcut-icon">02</span><span><strong>銷售訂單</strong><small>用訂單 ID 查詢實際行項</small></span><b aria-hidden="true">↗</b></RouterLink>
      <RouterLink to="/inventory" class="shortcut"><span class="shortcut-icon">03</span><span><strong>庫存作業</strong><small>查詢、初始化與調整數量</small></span><b aria-hidden="true">↗</b></RouterLink>
      <RouterLink to="/procurement" class="shortcut"><span class="shortcut-icon">04</span><span><strong>採購與收貨</strong><small>查價、建單與登錄實際收貨</small></span><b aria-hidden="true">↗</b></RouterLink>
    </div>
    <div class="home-note"><span class="note-dot"></span><div><strong>資料以服務讀回為準</strong><p>送出作業後若連線中斷，請先查詢目前狀態；畫面不會自動重送變更。</p></div></div>
  </div>
</template>
