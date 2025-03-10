<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="用户编号" prop="userId">
        <el-input
          v-model="queryParams.userId"
          placeholder="请输入用户编号"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['news:news_info:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['news:news_info:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['news:news_info:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['news:news_info:export']"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="Check"
          :disabled="multiple"
          @click="handleCheck"
          v-hasPermi="['news:news_info:check']"
        >检测</el-button>
      </el-col>

      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="news_infoList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="新闻编号" align="center" prop="newsId" />
      <el-table-column label="新闻标题" align="center" prop="newsTitle" />
      <el-table-column label="新闻内容" align="center" prop="newsContent">
        <template #default="scope">
          <span>{{ scope.row.newsContent.slice(0, 50) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="发布时间" align="center" prop="publishTime">
        <template #default="scope">
          <span>{{ parseTime(scope.row.publishTime, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="平台" align="center" prop="platform" />
      <el-table-column label="链接" align="center" prop="url">
        <template #default="scope">
          <a :href="scope.row.url" target="_blank" style="color: blue; text-decoration: underline;">
            {{ scope.row.url }}
          </a>
        </template>
      </el-table-column>

      <el-table-column label="上传者" align="center" prop="createBy" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['news:news_info:edit']">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['news:news_info:remove']">删除</el-button>
          <el-button link type="primary" icon="View" @click="handleDetail(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改新闻信息对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="news_infoRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="新闻标题" prop="newsTitle">
        <el-input v-model="form.newsTitle" type="textarea" placeholder="请输入内容" />
      </el-form-item>
      <el-form-item label="新闻内容" prop="newsContent">
        <editor v-model="form.newsContent" :min-height="192"/>
      </el-form-item>
      <el-form-item label="发布时间" prop="publishTime">
        <el-date-picker clearable
          v-model="form.publishTime"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="请选择发布时间">
        </el-date-picker>
      </el-form-item>
      <el-form-item label="平台" prop="platform">
        <el-input v-model="form.platform" placeholder="请输入平台" />
      </el-form-item>
      <el-form-item label="类别" prop="hashTag">
        <el-input v-model="form.hashTag" placeholder="请输入类别" />
      </el-form-item>
      <el-form-item label="链接" prop="url">
        <el-input v-model="form.url" placeholder="请输入链接" />
      </el-form-item>

      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="News_info">
import { listNews_info, getNews_info, delNews_info, addNews_info, updateNews_info,checkNews_info } from "@/api/news/news_info";
import useUserStore from '@/store/modules/user'
import { useRouter } from 'vue-router';
const userStore = useUserStore()

const { proxy } = getCurrentInstance();

const news_infoList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    newsContent: null,
    userId: null,
    newsTitle: null,
  },
  rules: {
  userId: [
    { required: true, message: "用户编号不能为空", trigger: "blur" }
  ],
  url: [
    { type: 'url', message: "链接格式不正确", trigger: "blur" }
  ],
},

});

const { queryParams, form, rules } = toRefs(data);

/** 查询新闻信息列表 */
function getList() {
  loading.value = true;
  listNews_info(queryParams.value).then(response => {
    news_infoList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 表单重置 */
function reset() {
  form.value = {
    newsId: null,
    newsContent: null,
    userId: null,
    newsTitle: null,
    updateBy: null,
    updateTime: null,
    createBy: null,
    createTime: null,
    publishTime: null,
    platform: null,
    hashTag: null,
    url: null,
  };
  proxy.resetForm("news_infoRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 多选框选中数据  */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.newsId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加新闻信息";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _newsId = row.newsId || ids.value;
  getNews_info(_newsId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改新闻信息";
  });
}

/** 提交按钮 */
function submitForm() {
  form.value.userId = userStore.id;
  proxy.$refs["news_infoRef"].validate(valid => {
    if (valid) {
      if (form.value.newsId != null) {
        updateNews_info(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addNews_info(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _newsIds = row.newsId || ids.value;
  proxy.$modal.confirm('是否确认删除新闻信息编号为"' + _newsIds + '"的数据项？').then(function() {
    return delNews_info(_newsIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}


/** 导出按钮操作 */
function handleExport() {
  proxy.download('news/news_info/export', {
    ...queryParams.value
  }, `news_info_${new Date().getTime()}.xlsx`);
}

/** 检测按钮操作 */
function handleCheck(row) {
  console.log(row.newsId,"\n",ids.value);
  const _newsIds = row.newsId || ids.value;
  // 调用检测 API，这里假设有一个叫 checkNews_info 的 API
  proxy.$modal.confirm('是否检测新闻信息编号为"' + _newsIds + '"的数据项？').then(function() {
    return checkNews_info(_newsIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("正在检测");
  }).catch(() => {});

}



const router = useRouter();
function handleDetail(row) {
  console.log(row.newsId);
  router.push({
    path: 'data_index',
    query: {newsId: row.newsId}
  });
}

getList();
</script>