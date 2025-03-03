<script setup lang="ts">
import { computed } from 'vue';
import URLInput from './modules/url-input.vue';
import Uploader from './modules/uploader.vue';
import PasteBox from './modules/paste-box.vue';
</script>

<template>
  <div>
    <div class="input-container">
      <URLInput class="url-input" />
      <Uploader class="uploader" />
    </div>
    <PasteBox />
  </div>
</template>

<style scoped>
.input-container {
  display: flex;
  gap: 20px;
  width: 1000px;
  margin: 20px auto;
}

.url-input {
  flex: 3;  /* 3/5 宽度 */
  min-width: 0; /* 防止内容溢出 */
}

.uploader {
  flex: 2;  /* 2/5 宽度 */
  min-width: 0;
}

/* 调整子组件内部容器宽度 */
:deep(.container),
:deep(.upload-container) {
  width: 100% !important;
  margin: 0 !important;
}
</style>