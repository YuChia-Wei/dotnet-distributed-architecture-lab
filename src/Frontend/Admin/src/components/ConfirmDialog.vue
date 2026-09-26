<script setup lang="ts">
import { nextTick, ref, useId, watch } from 'vue'

const props = withDefaults(defineProps<{
  open: boolean
  title: string
  description: string
  confirmText?: string
}>(), { confirmText: '確認' })
const emit = defineEmits<{ cancel: []; confirm: [] }>()
const titleId = useId()
const descriptionId = useId()
const cancelButton = ref<HTMLButtonElement | null>(null)
const confirmButton = ref<HTMLButtonElement | null>(null)
let returnFocus: HTMLElement | null = null

watch(() => props.open, async (open) => {
  if (open) {
    returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    await nextTick()
    cancelButton.value?.focus()
  } else {
    await nextTick()
    if (returnFocus?.isConnected && !returnFocus.matches(':disabled')) returnFocus.focus()
    else document.getElementById('main')?.focus()
    returnFocus = null
  }
}, { flush: 'post' })

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault()
    emit('cancel')
  }
  if (event.key !== 'Tab') return
  const first = cancelButton.value
  const last = confirmButton.value
  if (!first || !last) return
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}
</script>

<template>
  <div v-if="open" class="dialog-backdrop">
    <div class="confirm-dialog" role="alertdialog" aria-modal="true" :aria-labelledby="titleId" :aria-describedby="descriptionId" @keydown="handleKeydown">
      <div class="dialog-symbol" aria-hidden="true">!</div>
      <h2 :id="titleId">{{ title }}</h2>
      <p :id="descriptionId">{{ description }}</p>
      <div class="dialog-actions">
        <button ref="cancelButton" class="button quiet" data-testid="confirm-cancel" type="button" @click="emit('cancel')">取消</button>
        <button ref="confirmButton" class="button danger-fill" data-testid="confirm-accept" type="button" @click="emit('confirm')">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>
