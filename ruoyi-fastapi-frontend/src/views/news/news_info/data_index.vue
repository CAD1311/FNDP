<template>
  <div class="app-container">
    <div v-if="showParsePanel" class="parse-panel">
      <el-alert type="info" show-icon :closable="false">
        <template #title>
          <div class="alert-content">
            <el-button 
              type="primary" 
              size="small"
              :loading="isParsing"
              @click="handleParse"
            >
              {{ isParsing ? '正在解析中...' : '立即解析网页内容' }}
            </el-button>
            <span class="tip">检测到该新闻尚无内容</span>
          </div>
        </template>
      </el-alert>
    </div>
    <!-- 新闻详情容器 -->
    <div class="news-wrapper">

      <div class="news-detail">
        <!-- 标题区 -->
        <div class="news-header">
          <h1 class="news-title">{{ newsDetail.newsTitle }}</h1>
          <div class="meta-info">
            <span class="publish-time">{{ formatTime(newsDetail.publishTime) }}</span>
            <span class="source">来源：{{ newsDetail.platform }}</span>
            <span class="hashtag">#{{ newsDetail.hashTag }}</span>
          </div>
        </div>

        <!-- 内容区 -->
        <article class="news-content" v-html="processedContent"></article>

        <!-- 原文链接 -->
        <div class="original-link">
          <a :href="newsDetail.url" target="_blank" class="link-button">
            <el-icon><Link /></el-icon>
            查看原文报道
          </a>
        </div>

      </div>
      <!-- 右侧检测结果 -->
      <div class="detection-result" v-if="detectionData">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span class="result-title">可信度分析结果</span>
              <el-tag :type="detectionData.isReal ? 'success' : 'danger'" effect="dark">
                {{ detectionData.isReal ? '真实信息' : '可疑信息' }}
              </el-tag>
            </div>
          </template>

          <div class="reason-list">
            <div v-for="(reason, index) in detectionData.reasons" :key="index" class="reason-item">
              <el-icon class="check-icon"><Select /></el-icon>
              <span>{{ reason }}</span>
            </div>
          </div>

          <el-divider />

          <div class="suggestion">
            <el-icon class="advice-icon"><Warning /></el-icon>
            <div class="suggestion-text">{{ detectionData.suggestion }}</div>
          </div>
        </el-card>
      </div>

    </div>
  </div>
</template>

<script setup name="News_data">
import { ref, onMounted, computed } from 'vue';
import { Link, Select, Warning } from '@element-plus/icons-vue';
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getNews_info, updateNews_info } from "@/api/news/news_info"
import {getDetection_task , listDetection_task} from "@/api/detection/detection_task"
import useUserStore from '@/store/modules/user'

const route = useRoute();
const newsId = ref(route.query.newsId);
const newsDetail = ref({});

const router = useRouter()
const isParsing = ref(false)
const userStore = useUserStore()

// 显示解析面板的条件
const showParsePanel = computed(() => {
  return (!newsDetail.value.newsContent || newsDetail.value.newsContent === "") 
    && newsDetail.value.url
})

// 核心解析逻辑
const handleParse = async () => {
  try {
    isParsing.value = true
    const url = newsDetail.value.url
    
    // 使用代理绕过CORS（需自建或使用公共代理）
    const proxyUrl = 'https://thingproxy.freeboard.io/fetch/'
    const response = await fetch(proxyUrl + url)
    if (!response.ok) throw new Error('网络请求失败')
    
    // 获取并解析HTML
    const html = await response.text()
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // 提取关键信息（需根据目标网站结构调整）
    const parsedData = {
      newsTitle: doc.querySelector('h1')?.textContent || doc.title,
      newsContent: extractMainContent(doc),
      userId:userStore.id,
      //publishTime: findPublishTime(doc),
      //platform: extractPlatform(url),
      //hashTag: findHashtags(doc)
    }

    // 更新数据库
    await updateNews_info({
      newsId: newsDetail.value.newsId,
      ...parsedData
    })

    await fetchData(); // 重新获取最新数据
    newsDetail.value = { ...newsDetail.value }; // 触发响应式更新
    
  } catch (error) {
    ElMessage.error(`解析失败: ${error.message}`)
  } finally {
    isParsing.value = false
  }
}

const extractMainContent = (doc) => {
  // 优先查找内容容器
  const container = findContentContainer(doc);
  if (!container) return '内容解析失败';

  // 创建临时容器克隆节点
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = container.innerHTML;

  // 移除所有非文本/图片的标签
  removeNonEssentialElements(tempDiv);

  // 安全处理并返回内容
  return sanitizeContent(tempDiv.innerHTML);
};

// 修复后的内容容器查找函数
const findContentContainer = (doc) => {
  const candidates = ['article', '.post-content', '#content', 'main'];
  
  // 遍历所有候选选择器
  for (const sel of candidates) {
    const element = doc.querySelector(sel);
    if (element) return element;
  }
  
  return null; // 未找到任何容器
};


// 递归移除非必要元素
const removeNonEssentialElements = (node) => {
  const elements = node.querySelectorAll('*');
  elements.forEach(el => {
    // 保留img标签
    if (el.tagName.toLowerCase() === 'img') {
      // 清理img属性
      Array.from(el.attributes).forEach(attr => {
        if (!['src', 'alt', 'title'].includes(attr.name)) {
          el.removeAttribute(attr.name);
        }
      });
      return;
    }
    
    // 处理文本容器
    if (['p', 'div', 'span'].includes(el.tagName.toLowerCase())) {
      // 只保留文本内容
      const text = el.textContent.trim();
      if (text) {
        const textNode = document.createTextNode(text);
        el.parentNode.replaceChild(textNode, el);
      } else {
        el.remove();
      }
    } else {
      // 移除其他元素
      el.parentNode.removeChild(el);
    }
  });
};

// 内容消毒处理
const sanitizeContent = (html) => {
  return html
    .replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gm, '')
    .replace(/ on\w+="[^"]*"/g, '')
    .replace(/<p><br><\/p>/g, '')
    .replace(/\n{3,}/g, '\n\n');
};

// 辅助方法 - 提取发布时间
const findPublishTime = (doc) => {
  // 常见发布时间选择器
  const timeSelectors = [
    'time[datetime]',
    '.publish-time',
    '.date',
    'meta[property="article:published_time"]'
  ]
  const timeElement = timeSelectors.find(sel => doc.querySelector(sel))
  return timeElement?.getAttribute('datetime') || new Date().toISOString()
}

// 初始化获取数据
const fetchData = async () => {
  const res = await getNews_info(route.query.newsId)
  newsDetail.value = res.data
}

fetchData()

// 处理图片样式
const processedContent = computed(() => {
  return newsDetail.value.newsContent
    ?.replace(/<img/g, '<img class="content-image"')
    ?.replace(/<p><br><\/p>/g, '') // 移除空段落
});

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '';
  const date = new Date(timeString);
  return date.toLocaleString('zh-HK', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};


// 新增响应式数据
let detectionData = ref(null);

// 解析任务结果的正则表达式
const parseTaskResult = (result) => {
  const isReal = /是否真实：(\d)/.exec(result)?.[1] === '1';
  const reasonsMatch = /原因：\[(.*?)\]/.exec(result);
  const suggestionMatch = /建议：(.*)/.exec(result);
  
  return {
    isReal,
    reasons: reasonsMatch?.[1].replace(/'/g, '').split(', ') || [],
    suggestion: suggestionMatch?.[1] || ''
  };
};


// 获取新闻检测结果信息
function fetchDetectionData() {
  //获取检测任务表
  listDetection_task({pageSize: 10000}).then(response => {
    
    let res = response.rows;
    //console.log("获取检测任务表：",res);
    //获取该newsId的新闻检测结果信息
    for(let i=res.length - 1;i>=0;i--){
      if(res[i].newsId == newsId.value){
        detectionData.value = parseTaskResult(res[i].taskResult);
        //detectionData.value = res[i].taskResult;
        break;
      }
    }
    console.log("获取该newsId的新闻检测结果信息：",detectionData.value);

  });
}


// 在onMounted中调用
onMounted(() => {
  getNews_info(newsId.value).then(response => {
    newsDetail.value = response.data;
  });
  fetchDetectionData(); // 新增调用
});

</script>

<style scoped>
.news-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.news-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.news-title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.meta-info {
  display: flex;
  gap: 1.5rem;
  color: #666;
  font-size: 0.9rem;
}

.news-content {
  line-height: 1.8;
  color: #444;
}

.news-content :deep(p) {
  margin: 1.5rem 0;
}

.news-content :deep(.content-image) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 2rem auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.original-link {
  margin-top: 3rem;
  text-align: center;
}

.link-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.8rem 1.5rem;
  background: #409eff;
  color: white !important;
  border-radius: 4px;
  text-decoration: none;
  transition: background 0.3s;
}

.link-button:hover {
  background: #66b1ff;
}

@media (max-width: 768px) {
  .news-detail {
    padding: 1rem;
  }
  
  .news-title {
    font-size: 1.5rem;
  }
  
  .meta-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}

.parse-panel {
  max-width: 800px;
  margin: 2rem auto;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.tip {
  color: #666;
  font-size: 14px;
}

.news-wrapper {
  display: flex;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.news-detail {
  flex: 1;
  max-width: 800px;
}

.detection-result {
  width: 350px;
  position: sticky;
  top: 20px;
  height: fit-content;
}

/* 检测结果卡片样式 */
.result-card {
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-title {
  font-weight: 600;
  font-size: 16px;
}

.reason-item {
  display: flex;
  gap: 8px;
  align-items: start;
  padding: 8px 0;
  line-height: 1.5;
}

.check-icon {
  color: #67C23A;
  margin-top: 4px;
}

.suggestion {
  background: #f0faff;
  padding: 12px;
  border-radius: 4px;
  display: flex;
  gap: 8px;
}

.advice-icon {
  color: #409EFF;
  flex-shrink: 0;
}

.suggestion-text {
  font-size: 14px;
  color: #666;
}

@media (max-width: 992px) {
  .news-wrapper {
    flex-direction: column;
  }
  
  .detection-result {
    width: 100%;
    position: static;
    order: -1;
  }
}
</style>