<template>
  <div class="bg-blue-100 rounded-full px-5 py-4 shadow-lg border-2 border-blue-300 relative">
    <div class="text-xl font-bold text-center" v-html="text"></div>
    <!-- 吹き出しの尻尾（外側の枠線） -->
    <div
      class="absolute -bottom-[12px] w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-t-[12px] border-t-blue-300"
      :class="tailPosition"
    ></div>
    <!-- 吹き出しの尻尾（内側の塗りつぶし） -->
    <div
      class="absolute -bottom-[10px] w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-t-[12px] border-t-blue-100"
      :class="tailPosition"
    ></div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  text: string
  tailPosition?: string
}

const props = withDefaults(defineProps<Props>(), {
  tailPosition: 'left-10'
})
</script>