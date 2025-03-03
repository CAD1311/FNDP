<script setup>
import { getJSON } from "@/api/newsinput/single";
import { ref } from "vue";

let news = ref({});
let test = ref(0)






function getNew() {
  console.log("get new");
  getJSON().then(res => {
    news.value = res.data;
    console.log(res);
  });
  console.log('finished',news.value);
}

function add(){
  test.value += 1;
  console.log(test.value);
}

</script>

<template>
    <div>点击获取new: {{ news }} , {{ test }}</div>
    <button @click="getNew">获取新闻</button>
    <button @click="add">add</button>
</template>