<template>
  <div class="app-container">
    <!-- 这里根据newsId获取新闻详细信息进行展示 -->
    <h1>newsDetail{{ newsDetail }}</h1>
  </div>
</template>

<script setup name="News_data">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { listNews_info, getNews_info, delNews_info, addNews_info, updateNews_info } from "@/api/news/news_info";

const route = useRoute();
const newsId = ref(route.query.newsId);
const newsDetail = ref({});
console.log(newsId.value)


onMounted(() => {
  getNews_info(newsId.value).then(response => {
    newsDetail.value = response.data;
  });
});
</script>
