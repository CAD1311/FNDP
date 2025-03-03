<script setup lang="ts">
import { ref, computed } from 'vue';

defineOptions({
  name: 'Uploader'
});

interface UploadResponse {
  filename: string;
  detail?: string;
}

const isHover = ref(false);
const fileName = ref<string | null>(null);
const wordFile = ref<File | null>(null);
const uploadStatus = ref<string>('');

const statusClass = computed(() => ({
  success: uploadStatus.value.includes('成功'),
  error: uploadStatus.value.includes('失败') || uploadStatus.value.includes('错误'),
}));

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    fileName.value = file.name;
    wordFile.value = file;
    uploadStatus.value = '';
  }
};

const submitWordDocument = async () => {
  if (!wordFile.value) {
    uploadStatus.value = '请先选择文件';
    return;
  }

  const formData = new FormData();
  formData.append('file', wordFile.value);

  try {
    uploadStatus.value = '上传中...';
    const response = await fetch('http://192.168.95.226:8000/news/single', {
      method: 'POST',
      body: formData,
    });

    const result: UploadResponse = await response.json();
    if (response.ok) {
      uploadStatus.value = `上传成功！文件名：${result.filename}`;
    } else {
      uploadStatus.value = `上传失败：${result.detail}`;
    }
  } catch (error) {
    uploadStatus.value = '网络错误，请检查后端服务';
  }
};
</script>

<template>
  <div class="upload-container">
    <h1 class="uploadTitle">选择单个文件进行上传</h1>
    <!-- 自定义上传区域 -->
    <div
      class="custom-upload"
      :class="{ 'hover-effect': isHover }"
      @mouseover="isHover = true"
      @mouseout="isHover = false"
    >
      <input
        type="file"
        id="fileInput"
        class="native-input"
        @change="handleFileUpload"
        accept=".doc,.docx,.txt"
      />
      <label for="fileInput" class="upload-label">
        <div class="upload-content">
          <svg class="upload-icon" viewBox="0 0 24 24">
            <path
              d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"
            />
            <path d="M8 15.01l.55 2h6.89l.56-2H8zm1.62-5l-.6-2h5.76l-.6 2h-4.56z" />
          </svg>
          <span class="prompt-text">{{ fileName || '选择新闻文件' }}</span>
        </div>
      </label>
    </div>
    <br />
    <button @click="submitWordDocument" class="uploadButton">上传</button>

    <!-- 状态反馈 -->
    <transition name="fade">
      <div v-if="uploadStatus" class="status-feedback" :class="statusClass">
        {{ uploadStatus }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
.upload-container {
  width: 100%;
  margin: 0 auto; 
  display: flex;
  flex-direction: column;
  max-height: 80vh; /* 视口高度限制 */
  border: 2px solid #282845;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
  box-shadow: 10px 10px 10px rgba(212, 104, 21, 0.1);
  border-width: 3px;    /*边框宽度*/
}

.custom-upload {
  border: 2px dashed #e28c46;
  padding: 2rem;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.hover-effect {
  border-color: #e2a04a;
  background-color: rgba(74, 144, 226, 0.05);
}

.native-input {
  opacity: 0;
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.upload-label {
  display: block;
  cursor: pointer;
  text-align: center;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  width: 48px;
  height: 48px;
  fill: #e28c46;
  transition: transform 0.2s ease;
}

.upload-label:hover .upload-icon {
  transform: translateY(-3px);
}

.prompt-text {
  color: #e28c46;
  font-size: 1.1rem;
}

.status-feedback {
  margin-top: 1rem;
  padding: 0.75rem;
  text-align: center;
  transition: all 0.3s ease;
}

.success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.error {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.uploadButton {
  margin: 10px; 
  width: 30%;
  background-color: #282845 !important;
  color: #e28c46 !important;
  padding: 8px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.uploadTitle {
  margin: 10px auto; /* 水平居中 */
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #e28c46;
}
</style>
