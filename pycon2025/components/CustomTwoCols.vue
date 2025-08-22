<template>
  <div class="grid gap-4 h-full" :class="gridClass">
    <div :class="leftColClass" class="flex flex-col justify-start items-start">
      <slot name="left" />
    </div>
    
    <div :class="rightColClass">
      <img 
        v-if="imageSrc" 
        :src="imageSrc" 
        :alt="imageAlt || 'Image'"
        :class="imageClass || 'w-48 h-64 object-contain'"
      />
      <slot name="right" v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  leftRatio?: number // 左側の割合（0-100）
  imageSrc?: string
  imageAlt?: string
  imageClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  leftRatio: 75
})

// グリッドのカラム数を計算（最小公倍数的なアプローチ）
const gridClass = computed(() => {
  const ratio = props.leftRatio
  if (ratio === 20) return 'grid-cols-5'
  if (ratio === 30) return 'grid-cols-10'
  if (ratio === 75) return 'grid-cols-4'
  if (ratio === 80) return 'grid-cols-5'
  if (ratio === 70) return 'grid-cols-10'
  if (ratio === 60) return 'grid-cols-5'
  if (ratio === 66) return 'grid-cols-3'
  return 'grid-cols-4' // デフォルト
})

const leftColClass = computed(() => {
  const ratio = props.leftRatio
  if (ratio === 20) return 'col-span-1'
  if (ratio === 30) return 'col-span-3'
  if (ratio === 75) return 'col-span-3'
  if (ratio === 80) return 'col-span-4'
  if (ratio === 70) return 'col-span-7'
  if (ratio === 60) return 'col-span-3'
  if (ratio === 66) return 'col-span-2'
  return 'col-span-3' // デフォルト
})

const rightColClass = computed(() => {
  const ratio = props.leftRatio
  if (ratio === 20) return 'col-span-4'
  if (ratio === 30) return 'col-span-7'
  if (ratio === 75) return 'col-span-1'
  if (ratio === 80) return 'col-span-1'
  if (ratio === 70) return 'col-span-3'
  if (ratio === 60) return 'col-span-2'
  if (ratio === 66) return 'col-span-1'
  return 'col-span-1' // デフォルト
})
</script>

<style scoped>
/* Additional custom styles if needed */
</style>