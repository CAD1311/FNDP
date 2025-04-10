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
          type="primary"
          plain
          icon="Plus"
          @click="handleAddBatch"
          v-hasPermi="['news:news_info:add']"
        >批量上传</el-button>
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
          v-hasPermi="['detection:detection_task:add']"
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
          <span>{{ scope.row.newsContent ? scope.row.newsContent.slice(0, 50) : '' }}</span>
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

      <el-table-column label="状态" align="center" prop="newsStatus">
        <template #default="scope">
          <!-- 新增：根据statusList数组中该id新闻的状态值显示不同的颜色-->
          <span :style="{ color: getStatusColor(getNewsStatus(scope.row.newsId)) }">
            {{ getNewsStatus(scope.row.newsId) }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="上传者" align="center" prop="createBy" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['news:news_info:edit']">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['news:news_info:remove']">删除</el-button>
          <el-button link type="primary" icon="View" @click="handleDetail(scope.row)">详情</el-button>
          <el-button link type="primary" icon="" @click="handleRefute(scope.row)">举报</el-button>
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

    <!-- 修改后的el-dialog部分 -->
<el-dialog title="批量上传新闻" v-model="batchUploadOpen" width="800px" append-to-body>
  <el-upload
    class="upload-demo"
    drag
    :auto-upload="false"
    :accept="'.csv'"
    :show-file-list="false"
    :on-change="handleFileChange"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      将CSV文件拖到此处或<em>点击上传</em>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        要求：CSV文件必须包含以下列（可空）：news_content, news_title, publish_time, platform, hash_tag, url
      </div>
      <div v-if="csvFile" class="file-info">
        已选文件：{{ csvFile.name }}
        <el-button type="primary" size="small" @click="handleUpload">开始上传</el-button>
      </div>
      <div v-if="uploadProgress.visible" class="progress-container">
        <el-progress 
          :percentage="uploadProgress.percent" 
          :status="uploadProgress.status"
          :stroke-width="18"
          striped
        />
        <div class="progress-text">
          已处理 {{ uploadProgress.processed }} / {{ uploadProgress.total }} 条
          <span v-if="uploadProgress.errors.length">（{{ uploadProgress.errors.length }} 条失败）</span>
        </div>
      </div>
    </template>
  </el-upload>
</el-dialog>

    <!-- 添加或修改新闻信息对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="news_infoRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="新闻标题" prop="newsTitle">
        <el-input v-model="form.newsTitle" type="textarea" placeholder="请输入内容" />
      </el-form-item>
      <el-form-item label="新闻内容" prop="newsContent">
        <editor v-model="form.newsContent" 
        :min-height="192"
        :upload-images="handleEditorImageUpload" />
        
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
import { listNews_info, getNews_info, delNews_info, addNews_info, updateNews_info,checkNews_info,refuteNews_info} from "@/api/news/news_info";
import {listDetection_task,getDetection_task,addDetection_task,updateDetection_task} from "@/api/detection/detection_task";
//import { addNews_images } from "@/api/news/news_images";
import useUserStore from '@/store/modules/user'
import { useRouter } from 'vue-router';
import { ref, toRaw, reactive, getCurrentInstance } from 'vue'
import { ElMessage } from 'element-plus'
import { read, utils } from 'xlsx'
import UploadFile from '@/components/FileUpload/index.vue'

const userStore = useUserStore()

const { proxy } = getCurrentInstance();

const news_infoList = ref([]);
const detection_taskList = ref([]) ;``
let statusList = ref([]); // 新增：用于存储新闻的检测结果信息
const open = ref(false);
const batchUploadOpen = ref(false);
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
  newsStatusList: {},  // 新增：用于存储新闻的状态信息
});

const { queryParams, form, rules ,newsStatusList} = toRefs(data);

/** 查询新闻信息列表 */
function getList() {
  loading.value = true;
  listNews_info(queryParams.value).then(response => {
    news_infoList.value = response.rows;
    total.value = response.total;
    loading.value = false;

  });
  console.log("查询新闻信息列表：",queryParams.value);
  getStatusList();
}

// 获取新闻检测结果信息
function getStatusList() {
  
  //获取检测任务表
  listDetection_task({pageSize: 10000}).then(response => {
    detection_taskList.value = response.rows;
    console.log("获取检测任务表：",detection_taskList.value);
    //从检测任务表中获取新闻id对应的状态信息
    let newsIdList = news_infoList.value.map(item => item.newsId);
    statusList.value = detection_taskList.value.filter(item => newsIdList.includes(item.newsId));
    //打印日志 查询结果
    console.log("查询结果：",statusList.value);
    mapStatusToNews();
  });
}

// 映射新闻的状态
function mapStatusToNews() {
  news_infoList.value.forEach(newsItem => {
    const statusItem = statusList.value.find(status => status.newsId === newsItem.newsId);
    if (statusItem) {
      newsItem.newsStatus = statusItem.isTrue === 1 ? '真实' : '谣言';
    } else {
      newsItem.newsStatus = '尚无定论';
    }
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

function handleAddBatch(){
  console.log("弹窗批量上传");
  batchUploadOpen.value = true;
}

function handleUploadSuccess() {
  batchUploadOpen.value = false;
  getList(); // 刷新列表
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
    const { textContent, images } = parseNewsContent(form.value.newsContent);

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
  let _newsIds = row.newsId || ids.value;
  _newsIds = toRaw(_newsIds);
  proxy.$modal.confirm('是否检测新闻信息编号为"' + _newsIds + '"的数据项？').then(function() {
    console.log("准备检测");
    checkNews_info(_newsIds).then(response => {
        console.log(response);
        getList();
    });
  }).then(() => {
    proxy.$modal.msgSuccess("正在检测");
  }).catch(() => {});
}

// 根据newsId获取新闻状态
function getNewsStatus(newsId) {
  const statusItem = statusList.value.find(item => item.newsId === newsId);
  if (statusItem) {
    return statusItem.isTrue === 1 ? '真实' : '谣言';
  }
  return '尚无定论';
}

//为新闻检测结果显示增加颜色区别
function getStatusColor(status) {
  switch (status) {
    case '谣言':
      return 'red';
    case '尚无定论':
      return 'gray';
    case '真实':
      return 'green';
    default:
      return 'black'; // 默认颜色或其他颜色
  }
}

function handleRefute(row){
  let _newsIds = row.newsId || ids.value;
  _newsIds = toRaw(_newsIds);
  refuteNews_info(_newsIds).then(response => {
    console.log(response);
  });
}

// 解析HTML内容
const parseNewsContent = (html) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  // 提取纯文本内容
  const textContent = doc.body.textContent;
  // 提取Base64图片
  const images = Array.from(doc.querySelectorAll('img'))
    .map(img => img.src)
    .filter(src => src.startsWith('data:image'));

  return { textContent, images };
};

// 新增编辑器图片处理
const handleEditorImageUpload = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
};

const router = useRouter();
function handleDetail(row) {
  router.push({
    path: 'data_index',
    query: { 
      newsId: row.newsId,
      t: Date.now() // 强制刷新
    }
  })
}



// 新增响应式数据
const csvFile = ref(null)
const uploadProgress = reactive({
  visible: false,
  percent: 0,
  processed: 0,
  total: 0,
  errors: [],
  status: ''
})

// 处理文件选择
const handleFileChange = (file) => {
  if (file.raw.type !== 'text/csv' && !file.name.endsWith('.csv')) {
    ElMessage.error('只能上传CSV文件')
    return false
  }
  csvFile.value = file.raw
}

// CSV列验证
const validateCSVColumns = (headers) => {
  //const requiredColumns = [
  //  'news_content',
  //  'news_title', 
  //  'publish_time',
  //  'platform',
  //  'hash_tag',
  //  'url'
  //]
  //return requiredColumns.every(col => headers.includes(col))
  return true;
}

// 转换字段名格式（蛇形转驼峰）
const transformFieldNames = (item) => {
  return {
    newsContent: item.news_content || '',
    newsTitle: item.news_title || '',
    publishTime: item.publish_time || null,
    platform: item.platform || '',
    hashTag: item.hash_tag || '',
    url: item.url || '',
    userId: userStore.id
  }
}

// 处理上传
const handleUpload = async () => {
  if (!csvFile.value) {
    ElMessage.warning('请先选择CSV文件')
    return
  }

  // 初始化进度
  Object.assign(uploadProgress, {
    visible: true,
    percent: 0,
    processed: 0,
    total: 0,
    errors: [],
    status: ''
  })

  try {
    // 读取CSV文件
    const reader = new FileReader()
    reader.onload = async (e) => {
      const data = new Uint8Array(e.target.result)
      const workbook = read(data, { type: 'array' })
      const worksheet = workbook.Sheets[workbook.SheetNames[0]]
      const jsonData = utils.sheet_to_json(worksheet)
      
      // 验证列头
      const headers = Object.keys(jsonData[0] || {})
      if (!validateCSVColumns(headers)) {
        ElMessage.error('CSV文件列头不符合要求')
        return
      }

      uploadProgress.total = jsonData.length

      // 逐条处理
      for (const [index, item] of jsonData.entries()) {
        try {
          const params = transformFieldNames(item)
          await addNews_info(params)
          uploadProgress.processed = index + 1
          uploadProgress.percent = Math.round(((index + 1) / jsonData.length) * 100)
        } catch (error) {
          console.error(`第 ${index + 1} 行数据上传失败:`, error)
          uploadProgress.errors.push({
            line: index + 1,
            error: error.message || '未知错误'
          })
        }
      }

      // 处理完成
      if (uploadProgress.errors.length === 0) {
        uploadProgress.status = 'success'
        ElMessage.success(`成功上传 ${jsonData.length} 条数据`)
        handleUploadSuccess()
      } else {
        uploadProgress.status = 'exception'
        ElMessage.warning(`上传完成，成功 ${jsonData.length - uploadProgress.errors.length} 条，失败 ${uploadProgress.errors.length} 条`)
      }
    }
    reader.readAsArrayBuffer(csvFile.value)
  } catch (error) {
    console.error('文件解析失败:', error)
    ElMessage.error('文件解析失败，请检查文件格式')
    uploadProgress.status = 'exception'
  }
}

getList();
</script>

<style scoped>
.file-info {
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.progress-container {
  margin-top: 20px;
}

.progress-text {
  margin-top: 10px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}
</style>
