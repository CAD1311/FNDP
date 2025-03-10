<template>
  <div class="app-container">
    <!-- 新闻详情容器 -->
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
  </div>
</template>

<script setup name="News_data">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { getNews_info } from "@/api/news/news_info";
import { Link } from '@element-plus/icons-vue';

const route = useRoute();
const newsId = ref(route.query.newsId);
const newsDetail = ref({});

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

onMounted(() => {
  getNews_info(newsId.value).then(response => {
    newsDetail.value = response.data;
  });
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
</style>