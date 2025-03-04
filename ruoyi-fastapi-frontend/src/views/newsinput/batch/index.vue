<script setup lang="ts">
import { ref, computed } from 'vue';

defineOptions({
  name: 'DirectoryUploader'
});

interface UploadResponse {
  message: string;
  detail?: string;
}

const isHover = ref(false);
const directoryName = ref<string | null>(null);
const directoryFiles = ref<File[]>([]);
const uploadStatus = ref<string>('');

const statusClass = computed(() => ({
  success: uploadStatus.value.includes('成功'),
  error: uploadStatus.value.includes('失败') || uploadStatus.value.includes('错误'),
}));

const handleDirectoryUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  
  if (files && files.length > 0) {
    directoryName.value = files[0].webkitRelativePath.split('/')[0];
    directoryFiles.value = Array.from(files);
    uploadStatus.value = `已选择目录：${directoryName.value}（包含 ${files.length} 个文件）`;
  }
};

const submitDirectory = async () => {
  if (!directoryFiles.value.length) {
    uploadStatus.value = '请先选择目录';
    return;
  }

  const formData = new FormData();
  directoryFiles.value.forEach((file, index) => {
    formData.append(`files_${index}`, file);
  });
  formData.append('directory', directoryName.value || '');

  try {
    uploadStatus.value = '上传中...';
    const response = await fetch('http://192.168.95.226:8000/news/directory', {
      method: 'POST',
      body: formData,
    });

    const result: UploadResponse = await response.json();
    if (response.ok) {
      uploadStatus.value = `上传成功！${result.message}`;
      directoryFiles.value = [];
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
    <h1 class="uploadTitle">选择目录进行上传</h1>
    <div
      class="custom-upload"
      :class="{ 'hover-effect': isHover }"
      @mouseover="isHover = true"
      @mouseout="isHover = false"
    >
      <input
        type="file"
        id="directoryInput"
        class="native-input"
        @change="handleDirectoryUpload"
        webkitdirectory
        multiple
      />
      <label for="directoryInput" class="upload-label">
        <div class="upload-content">
          <svg class="upload-icon" viewBox="0 0 24 24">
            <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
            <path d="M20 8h-8l-2-2H4v12h16V8zm-2 6h-2v2h2v2h-4v-4h2v-2h-2v-2h4z"/>
          </svg>
          <span class="prompt-text">{{ directoryName || '选择新闻目录' }}</span>
        </div>
      </label>
    </div>
    <br />
    <button @click="submitDirectory" class="uploadButton">上传目录</button>

    <transition name="fade">
      <div v-if="uploadStatus" class="status-feedback" :class="statusClass">
        {{ uploadStatus }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* 在原有样式基础上调整图标和提示文字 */
.upload-container {
  width: 80%;
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
  height: 48px;
  fill: #e28c46;
}

.uploadTitle {
  margin: 10px auto; /* 水平居中 */
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #e28c46;
}




.prompt-text {
  font-size: 1.1rem;
  color: #e28c46;
}

/* 新增目录提示样式 */
.status-feedback::before {
  content: "📁";
  margin-right: 8px;
}
</style>