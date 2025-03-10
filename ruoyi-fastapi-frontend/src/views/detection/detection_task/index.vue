<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="任务状态" prop="taskStatus">
        <el-select v-model="queryParams.taskStatus" placeholder="请选择任务状态" clearable>
          <el-option label="请选择字典生成" value="" />
        </el-select>
      </el-form-item>
      <el-form-item label="所属用户" prop="userId">
        <el-input
          v-model="queryParams.userId"
          placeholder="请输入所属用户"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="涉及新闻" prop="newsId">
        <el-input
          v-model="queryParams.newsId"
          placeholder="请输入涉及新闻"
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
          v-hasPermi="['detection:detection_task:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['detection:detection_task:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['detection:detection_task:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['detection:detection_task:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="detection_taskList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="任务id" align="center" prop="taskId" />
      <el-table-column label="任务状态" align="center" prop="taskStatus" />
      <el-table-column label="所属用户" align="center" prop="userId" />
      <el-table-column label="涉及新闻" align="center" prop="newsId" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['detection:detection_task:edit']">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['detection:detection_task:remove']">删除</el-button>
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

    <!-- 添加或修改新闻检测对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="detection_taskRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="任务状态" prop="taskStatus">
        <el-radio-group v-model="form.taskStatus">
          <el-radio label="请选择字典生成" value="" />
        </el-radio-group>
      </el-form-item>
      <el-form-item label="所属用户" prop="userId">
        <el-input v-model="form.userId" placeholder="请输入所属用户" />
      </el-form-item>
      <el-form-item label="涉及新闻" prop="newsId">
        <el-input v-model="form.newsId" placeholder="请输入涉及新闻" />
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

<script setup name="Detection_task">
import { listDetection_task, getDetection_task, delDetection_task, addDetection_task, updateDetection_task } from "@/api/detection/detection_task";

const { proxy } = getCurrentInstance();

const detection_taskList = ref([]);
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
    taskStatus: null,
    userId: null,
    newsId: null,
  },
  rules: {
    taskStatus: [
      { required: true, message: "任务状态不能为空", trigger: "change" }
    ],
    userId: [
      { required: true, message: "所属用户不能为空", trigger: "blur" }
    ],
    newsId: [
      { required: true, message: "涉及新闻不能为空", trigger: "blur" }
    ],
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询新闻检测列表 */
function getList() {
  loading.value = true;
  listDetection_task(queryParams.value).then(response => {
    detection_taskList.value = response.rows;
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
    taskId: null,
    updateBy: null,
    updateTime: null,
    createBy: null,
    createTime: null,
    taskStatus: null,
    userId: null,
    newsId: null,
  };
  proxy.resetForm("detection_taskRef");
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
  ids.value = selection.map(item => item.taskId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加新闻检测";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _taskId = row.taskId || ids.value;
  getDetection_task(_taskId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改新闻检测";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["detection_taskRef"].validate(valid => {
    if (valid) {
      if (form.value.taskId != null) {
        updateDetection_task(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addDetection_task(form.value).then(response => {
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
  const _taskIds = row.taskId || ids.value;
  proxy.$modal.confirm('是否确认删除新闻检测编号为"' + _taskIds + '"的数据项？').then(function() {
    return delDetection_task(_taskIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}


/** 导出按钮操作 */
function handleExport() {
  proxy.download('detection/detection_task/export', {
    ...queryParams.value
  }, `detection_task_${new Date().getTime()}.xlsx`);
}

getList();
</script>