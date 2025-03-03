<script setup lang="ts">
import { ref, computed } from 'vue';

defineOptions({
  name: 'URLInput'
});

let newUrl = ref('');

let feedBackMessage = ref('')

function uploadContents() {
  console.log(newUrl.value);
  feedBackMessage.value = '上传中'
}

const statusClass = computed(() => ({
  success: feedBackMessage.value.includes('成功'),
  error: feedBackMessage.value.includes('失败') || feedBackMessage.value.includes('错误'),
}));

</script>
<template>
  <div class="container">
    <h1 class="Title">上传新闻链接</h1>
    <input class="content-box" type="text" v-model="newUrl" placeholder="请输入新闻链接">
    <div class="upload-container">
      <button class="upload-btn" @click="uploadContents()">上传</button>
      <div class="feedback-wrapper">
        <h2 class="feed-back" :class="statusClass">{{ feedBackMessage }}</h2>
      </div>
    </div>
  </div>
</template>
  

<style scoped>
.container {
  width: 100%;
  margin: 0 auto; 
  display: flex;
  flex-direction: column;
  max-height: 80vh; /* 视口高度限制 */
  border: 2px solid #282845;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 10px 10px 10px rgba(212, 104, 21, 0.1);
  border-width: 3px;    /*边框宽度*/
}
.upload-container {
  display: flex;
  align-items: center;  /* 垂直居中 */
  gap: 20px;
  width: 100%;
  margin: 10px 0;
}

.feedback-wrapper {
  flex: 4;
  display: flex;
  justify-content: center;  /* 水平居中 */
  align-items: center;      /* 垂直居中 */
  height: 100%;
}

.feed-back {
  text-align: center;      /* 文字水平居中 */
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}


.content-box {
  min-height: 20px;
  flex: 1;
  overflow-y: auto; /* 内容溢出自动滚动 */
  padding: 10px;
  border: 1px dashed #e28c46;
}

.upload-btn {
  flex: 1;  /* 3/5 宽度 */
  min-width: 0; /* 防止内容溢出 */
  margin: 10px; 
  width: 30%;
  background-color: #282845 !important;
  color: #e28c46 !important;
  padding: 8px 5px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}



.Title {
  margin: auto auto; /* 水平居中 */
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #e28c46;
}



.success {
  font-size: 1.1rem;
  background-color: #d4edda;
  height:50%;
  color: #155724;

}

.error {
  font-size: 1.1rem;
  background-color: #f8d7da;
  height:50%;
  color: #721c24;
}
</style>
