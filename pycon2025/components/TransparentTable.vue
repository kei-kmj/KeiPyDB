<template>
  <div>
    <table 
      :class="{
        'with-outer-border': showOuterBorder,
        'with-row-lines': showRowLines
      }"
    >
      <thead>
        <tr>
          <th>項目</th>
          <th>内容</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in items" :key="index">
          <td>{{ item.label }}</td>
          <td v-html="item.value"></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface TableItem {
  label: string
  value: string
}

interface Props {
  items: TableItem[]
  showOuterBorder?: boolean
  showRowLines?: boolean
}

withDefaults(defineProps<Props>(), {
  showOuterBorder: false,
  showRowLines: false
})
</script>

<style scoped>
/* 基本スタイル */
table {
  border-collapse: collapse !important;
  width: 100%;
  margin: 0;
  border: none !important;
}

table th, table td {
  background: transparent !important;
  font-size: 1.6rem !important;
  padding: 0.5rem 1rem !important;
  border: none !important;
}

table th {
  display: none;
}

table thead {
  display: none;
}

table tr {
  border: none !important;
}

table tr:nth-child(even) {
  background: transparent !important;
}

table tr:nth-child(odd) {
  background: transparent !important;
}

/* 外周ボーダーあり */
table.with-outer-border {
  border: 1px solid #ddd !important;
}

/* 行間ラインあり */
table.with-row-lines tbody tr {
  border-bottom: 1px solid #ddd !important;
}

table.with-row-lines tbody tr:last-child {
  border-bottom: none !important;
}

/* 枠線ありの場合、セルにも縦線を追加 */
table.with-outer-border td,
table.with-outer-border th {
  border: 1px solid #ddd !important;
}
</style>