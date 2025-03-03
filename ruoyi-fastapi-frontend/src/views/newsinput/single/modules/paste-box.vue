<script setup lang="ts">
import { ref, computed } from 'vue';

defineOptions({
  name: 'PasteBox'
});

type ContentItem = {
  type: 'text' | 'image';
  value: string;
  id: number;
};

const uploadStatus = ref<string>('');
const statusClass = computed(() => ({
  success: uploadStatus.value.includes('成功'),
  error: uploadStatus.value.includes('失败') || uploadStatus.value.includes('错误'),
}));

const contents = ref<ContentItem[]>([]);
const selectedId = ref<number | null>(null);
let contentId = 0;

const handlePaste = async (event: ClipboardEvent) => {
  const items = event.clipboardData?.items;
  if (!items) return;
  event.preventDefault();

  const processItems = Array.from(items).map(async (item) => {
    if (item.kind === 'file' && item.type.startsWith('image/')) {
      const file = item.getAsFile();
      if (!file) return null;
      
      return new Promise<ContentItem>(resolve => {
        const reader = new FileReader();
        reader.onload = (e) => {
          resolve({
            type: 'image',
            value: e.target?.result as string,
            id: ++contentId
          });
        };
        reader.readAsDataURL(file);
      });
    } else if (item.type === 'text/plain') {
      return new Promise<ContentItem>(resolve => {
        item.getAsString((text: string) => {
          resolve({
            type: 'text',
            value: text,
            id: ++contentId
          });
        });
      });
    }
    return null;
  });

  const newItems = (await Promise.all(processItems)).filter(Boolean) as ContentItem[];
  contents.value = [...contents.value, ...newItems];
};

// 上传功能
const uploadContents = async () => {
  const formData = new FormData();
  
  contents.value.forEach((item, index) => {
    if (item.type === 'text') {
      formData.append(`content[${index}]`, item.value);
    } else {
      const blob = dataURLtoBlob(item.value);
      formData.append(`file[${index}]`, blob, `image_${index}.png`);
    }
  });
  if (!formData) {
    uploadStatus.value = '请先粘贴或输入内容';
    return;
  }
  try {
    uploadStatus.value = '上传中...';
    const response = await fetch('your-api-endpoint', {
      method: 'POST',
      body: formData
    });
    // 处理响应...
    if (response.ok) {
      uploadStatus.value = `上传成功！`;
    } else {
      uploadStatus.value = `上传失败`;
    }
  } catch (error) {
    console.error('上传失败:', error);
    uploadStatus.value = '网络错误，请检查后端服务';
  }
};

// 辅助函数
const dataURLtoBlob = (dataurl: string) => {
  const arr = dataurl.split(',');
  const mime = arr[0].match(/:(.*?);/)![1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) u8arr[n] = bstr.charCodeAt(n);
  return new Blob([u8arr], { type: mime });
};

// 交互功能
const handleDelete = () => {
  if (selectedId.value !== null) {
    contents.value = contents.value.filter(
      item => item.id !== selectedId.value
    );
    selectedId.value = null;
  }
};

const placeholder = computed(() => 
  contents.value.length === 0 ? '输入或粘贴内容...' : ''
);
</script>

<template>
  <div class="editor-container">
    <h1 class="pasteTitle">输入粘贴文本或图片进行上传</h1>
    <div 
      class="content-box"
      contenteditable
      @paste="handlePaste"
      @keydown.delete="handleDelete"
      :data-placeholder="placeholder"
    >
      <div 
        v-for="item in contents"
        :key="item.id"
        :class="{ 'selected': item.id === selectedId }"
        @click="selectedId = item.id"
        class="content-item"
      >
      <img 
      v-if="item.type === 'image'" 
      :src="item.value"
      class="pasted-image"
    />
        <div v-else>{{ item.value }}</div>
      </div>
    </div>
    <br>
    <button class="upload-btn" @click="uploadContents">
      上传
    </button>
        <!-- 状态反馈 -->
        <transition name="fade">
      <div v-if="uploadStatus" class="status-feedback" :class="statusClass">
        {{ uploadStatus }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
.editor-container {
  width: 1000px;
  margin: 20px auto; /* 水平居中 */
  display: flex;
  flex-direction: column;
  max-height: 80vh; /* 视口高度限制 */
  border: 2px solid #282845;
  border-radius: 8px;
  padding: 20px;
}

.scroll-wrapper {
  flex: 1;
  min-height: 200px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-box {
  min-height: 200px;
  flex: 1;
  overflow-y: auto; /* 内容溢出自动滚动 */
  padding: 10px;
  border: 1px dashed #e28c46;
}


.content-box:empty::before {
  content: attr(data-placeholder);
  color: #999;
}

.content-item {
  display: block; /* 改为块级布局 */
  margin: 10px 0;
}

.pasted-image {
  display: block; /* 修复行内间隙 */
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
.content-item.selected {
  outline: 0px solid #e28c46;
}

.upload-btn {
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

.upload-btn:hover {
  background-color: #d17b35;
}

img {
  max-width: 200px;
  max-height: 150px;
  object-fit: contain;
}
.pasteTitle {
  margin: auto auto; /* 水平居中 */
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #e28c46;
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
</style>

