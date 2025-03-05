<template>
  <div>
    <h1>{{form}}</h1>
    <button @click="submit">提交</button>
  </div>

</template>

<script setup name="News">

import {addNews} from "@/api/news/news";

import { ref } from "vue";

let form = ref({})


form.value = {
    newsId: 0,
    newsContent: "测试我了个去",
    userId: 2,
    imgId: 1,
 }

function submit() {
    console.log("提交",form.value);
    addNews(form.value).then(response => {
        console.log(response);
    });
}
</script>