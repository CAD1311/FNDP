<template>
    <div>
      <div class="pageHeaderContent">
        <div class="avatar">
          <a-avatar size="large" :src="currentUser.avatar" />
        </div>
        <div class="content">
          <div class="contentTitle">
            你好，
            {{ currentUser.name }}
            ，欢迎使用伪造新闻检测平台！
          </div>
          <div>从下方快速开始吧</div>
        </div>
      </div>
  
      <!-- 新增的三个路由模块 -->
      <div class="router-modules">
        <a-row :gutter="16" style="margin-bottom: 16px">
          <a-col :span="12">
            <a-card 
              hoverable
              @click="goToModule1"
              style="cursor: pointer; margin-bottom: 16px"
            >
              <template #title>新闻检测管理</template>
              <template #extra>点击进入</template>
              <p>管理新闻数据, 进行新闻检测, 举报不实新闻</p>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card 
              hoverable
              @click="goToModule2"
              style="cursor: pointer; margin-bottom: 16px"
            >
              <template #title>新闻图片管理</template>
              <template #extra>点击进入</template>
              <p>管理新闻图片,上传或删除新闻对应的图片,以供多模态模型进行预测</p>
            </a-card>
          </a-col>
        </a-row>
        
        <a-row>
          <a-col :span="24">
            <a-card 
              hoverable
              @click="goToModule3"
              style="cursor: pointer"
            >
              <template #title>新闻举报</template>
              <template #extra>点击进入</template>
              <p>进入中国互联网联合辟谣平台,举报不实新闻</p>
            </a-card>
          </a-col>
        </a-row>
      </div>
  
    </div>
  </template>
  
  <script>
  import {
    Statistic,
    Row,
    Col,
    Card,
    CardGrid,
    CardMeta,
    List,
    ListItem,
    ListItemMeta,
    Avatar,
  } from "ant-design-vue";
  import 'ant-design-vue/dist/reset.css';
  
  export default {
    components: {
      AStatistic: Statistic,
      ARow: Row,
      ACol: Col,
      ACard: Card,
      ACardGrid: CardGrid,
      ACardMeta: CardMeta,
      AList: List,
      AListItem: ListItem,
      AListItemMeta: ListItemMeta,
      AAvatar: Avatar,
    },
  };
  </script>
  
  
  <script setup>

  import useUserStore from '@/store/modules/user'
  import { useRouter } from 'vue-router'
  
  //defineOptions({
  //  name: "DashBoard",
  //});
  const userStore = useUserStore()
  const router = useRouter()
  
  // 路由跳转方法
  const goToModule1 = () => {
    router.push('input') // 替换为你的实际路由路径
  }
  const goToModule2 = () => {
    router.push('tool/img') // 替换为你的实际路由路径
  }
  const goToModule3 = () => {
    router.push('report') // 替换为你的实际路由路径
  }
  
  const currentUser = {
    avatar: "https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png",
    name: userStore.name,
    userid: userStore.id,
    email: "antdesign@alipay.com",
    signature: "海纳百川，有容乃大",
    title: "交互专家",
    group: "蚂蚁金服－某某某事业群－某某平台部－某某技术部－UED",
  };
  
  </script>
  
  <style scoped lang="less">
  .textOverflow() {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    word-break: break-all;
  }
  
  // mixins for clearfix
  // ------------------------
  .clearfix() {
    zoom: 1;
    &::before,
    &::after {
      display: table;
      content: " ";
    }
    &::after {
      clear: both;
      height: 0;
      font-size: 0;
      visibility: hidden;
    }
  }
  
  .activitiesList {
    padding: 0 24px 8px 24px;
    .username {
      color: rgba(0, 0, 0, 0.65);
    }
    .event {
      font-weight: normal;
    }
  }
  
  .pageHeaderContent {
    display: flex;
    padding: 12px;
    margin-bottom: 24px;
    box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
    .avatar {
      flex: 0 1 72px;
      & > span {
        display: block;
        width: 72px;
        height: 72px;
        border-radius: 72px;
      }
    }
    .content {
      position: relative;
      top: 4px;
      flex: 1 1 auto;
      margin-left: 24px;
      color: rgba(0, 0, 0, 0.45);
      line-height: 22px;
      .contentTitle {
        margin-bottom: 12px;
        color: rgba(0, 0, 0, 0.85);
        font-weight: 500;
        font-size: 20px;
        line-height: 28px;
      }
    }
  }
  
  .router-modules {
    padding: 0 12px;
  
    .ant-card {
      transition: all 0.3s;
      &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
      }
    }
  }
  
  /* 保留原有其他样式 */
  .extraContent {
    .clearfix();
  
    float: right;
    white-space: nowrap;
    .statItem {
      position: relative;
      display: inline-block;
      padding: 0 32px;
      > p:first-child {
        margin-bottom: 4px;
        color: rgba(0, 0, 0, 0.45);
        font-size: 14px;
        line-height: 22px;
      }
      > p {
        margin: 0;
        color: rgba(0, 0, 0, 0.85);
        font-size: 30px;
        line-height: 38px;
        > span {
          color: rgba(0, 0, 0, 0.45);
          font-size: 20px;
        }
      }
      &::after {
        position: absolute;
        top: 8px;
        right: 0;
        width: 1px;
        height: 40px;
        background-color: #e8e8e8;
        content: "";
      }
      &:last-child {
        padding-right: 0;
        &::after {
          display: none;
        }
      }
    }
  }
  
  .members {
    a {
      display: block;
      height: 24px;
      margin: 12px 0;
      color: rgba(0, 0, 0, 0.65);
      transition: all 0.3s;
      .textOverflow();
      .member {
        margin-left: 12px;
        font-size: 14px;
        line-height: 24px;
        vertical-align: top;
      }
      &:hover {
        color: #1890ff;
      }
    }
  }
  
  .projectList {
    :deep(.ant-card-meta-description) {
      height: 44px;
      overflow: hidden;
      color: rgba(0, 0, 0, 0.45);
      line-height: 22px;
    }
    .cardTitle {
      font-size: 0;
      a {
        display: inline-block;
        height: 24px;
        margin-left: 12px;
        color: rgba(0, 0, 0, 0.85);
        font-size: 14px;
        line-height: 24px;
        vertical-align: top;
        &:hover {
          color: #1890ff;
        }
      }
    }
    .projectGrid {
      width: 33.33%;
    }
    .projectItemContent {
      display: flex;
      flex-basis: 100%;
      height: 20px;
      margin-top: 8px;
      overflow: hidden;
      font-size: 12px;
      line-height: 20px;
      .textOverflow();
      a {
        display: inline-block;
        flex: 1 1 0;
        color: rgba(0, 0, 0, 0.45);
        .textOverflow();
        &:hover {
          color: #1890ff;
        }
      }
      .datetime {
        flex: 0 0 auto;
        float: right;
        color: rgba(0, 0, 0, 0.25);
      }
    }
  }
  
  .datetime {
    color: rgba(0, 0, 0, 0.25);
  }
  
  @media screen and (max-width: 1200px) and (min-width: 992px) {
    .activeCard {
      margin-bottom: 24px;
    }
    .members {
      margin-bottom: 0;
    }
    .extraContent {
      margin-left: -44px;
      .statItem {
        padding: 0 16px;
      }
    }
  }
  
  @media screen and (max-width: 992px) {
    .activeCard {
      margin-bottom: 24px;
    }
    .members {
      margin-bottom: 0;
    }
    .extraContent {
      float: none;
      margin-right: 0;
      .statItem {
        padding: 0 16px;
        text-align: left;
        &::after {
          display: none;
        }
      }
    }
  }
  
  @media screen and (max-width: 768px) {
    .extraContent {
      margin-left: -16px;
    }
    .projectList {
      .projectGrid {
        width: 50%;
      }
    }
  }
  
  @media screen and (max-width: 576px) {
    .pageHeaderContent {
      display: block;
      .content {
        margin-left: 0;
      }
    }
    .extraContent {
      .statItem {
        float: none;
      }
    }
  }
  
  @media screen and (max-width: 480px) {
    .projectList {
      .projectGrid {
        width: 100%;
      }
    }
  }
  </style>