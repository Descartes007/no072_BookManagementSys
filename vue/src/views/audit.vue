<template>
  <div>
    <div class="container">
      <div class="search-box">
        <el-input v-model="searchKey" placeholder="请输入搜索关键字" class="search-input mr10" clearable></el-input>
        <el-date-picker
            v-model="timeSelect"
            type="datetimerange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD HH:mm:ss"
            date-format="YYYY-MM-DD"
            time-format="HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择日期范围"
            class="mr10"
        ></el-date-picker>
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button type="primary" :icon="Refresh" @click="handleReset">重置</el-button>
      </div>
      <el-table :data="filteredData" border class="table" ref="multipleTable" header-cell-class-name="table-header"
                @selection-change="handleSelectionChange">
        <el-table-column prop="id" label="ID" width="55" align="center" type="selection"></el-table-column>
        <el-table-column prop="id" label="ID" width="55" align="center"></el-table-column>
        <el-table-column prop="model" label="事件类型" align="center"></el-table-column>
        <el-table-column prop="time" label="操作时间" align="center">
          <template #default="scope">{{ formatDateTime(scope.row.time) }}</template>
        </el-table-column>
        <el-table-column prop="user" label="操作人" align="center"></el-table-column>
        <el-table-column prop="ip" label="用户IP" align="center"></el-table-column>
        <el-table-column prop="event" label="事件信息" align="center"></el-table-column>
      </el-table>
      <!--      分页组件-->
      <div class="pagination">
        <el-pagination
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="pageTotal"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50]"
            :page-size="pageSize"
            @current-change="handlePageChange"
            @size-change="handleSizeChange"
        ></el-pagination>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, computed, onMounted} from 'vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {Delete, Edit, Search, CirclePlusFilled, View, Refresh} from '@element-plus/icons-vue';
import {postRequest} from '../api/index';
import {useRoute} from "vue-router";
import moment from 'moment';
import {formatDateTime} from '../utils/timehandle';

//这个接口里的字段名必须要和后端返回的接口字段一直，否则前端无法显示
interface TableItem {
  id: number;
  time: number;
  user: string;
  ip: string;
  model: string;
  event: string;
};

const currentPage = ref(1);
const pageSize = ref(10);
const route = useRoute();
const searchKey = ref('');

const timeSelect = ref('')
const tableData = ref<TableItem[]>([]);
const pageTotal = ref(0);

// 创建一个计算属性来截断字符串
const truncateText = (text: string, maxLength: number = 20) => {
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
};

// 存储选中的行
const selectedRows = ref<TableItem[]>([]);
const handleSelectionChange = (rows: TableItem[]) => {
  selectedRows.value = rows;
};


// 获取表格数据
const getData = async (queryString) => {
  const res = await postRequest(route.fullPath + '/query', queryString);
  tableData.value = res.data.infos;
  pageTotal.value = res.data.pageTotal || 50;
};


// 初始化加载第一页数据
onMounted(() => {
  getData({query_string: searchKey.value, page: currentPage.value, size: pageSize.value});
});

// 查询操作
// 搜索框模糊查询操作,不会向后端发起请求，只是对当前table数据过滤显示
// 计算属性，用于过滤数据
const filteredData = computed(() => {
  const keyword = searchKey.value.toLowerCase();
  return tableData.value.filter(item => {
    return (
        //希望对哪些字段进行模糊查询就在这里添加
        item.user.toString().includes(keyword) ||
        item.ip.toString().includes(keyword) ||
        item.model.toString().includes(keyword) ||
        item.event.toString().includes(keyword)
    );
  });
});


const handleSearch = () => {
  console.log(timeSelect.value[0], timeSelect.value[1]);
  if (searchKey.value.length > 0 || timeSelect.value.length === 0) {
    getData({'query_string': searchKey.value, page: currentPage.value, size: pageSize.value});
  } else {
    getData({start_time: timeSelect.value[0], end_time: timeSelect.value[1]});
  }

};


//重置搜索条件
const handleReset = async () => {
  timeSelect.value = '';
  searchKey.value = '';
  getData({query_string: "", page: currentPage.value, size: pageSize.value});
};

function handleSizeChange(size: number) {
  pageSize.value = size;
  currentPage.value = 1; // 切换每页大小时通常回到第一页
  getData({query_string: searchKey.value, page: currentPage.value, size: pageSize.value});
}

// 分页查询
const handlePageChange = async (newPage: number) => {
  currentPage.value = newPage;   //这里必须要同步更新前端数据，否则前端页面不切换到新的页面上
  try {
    const response = await postRequest(route.fullPath + '/query', {
      query_string: searchKey.value,
      page: currentPage.value,
      size: pageSize.value
    });
    console.log("分页查询");
    if (response.data.status) {
      // 请求成功，处理成功逻辑，例如显示通知或跳转页面
      ElMessage.success(response.data.message);
      tableData.value = response.data.infos;
      pageTotal.value = response.data.pageTotal;
    } else {
      // 请求失败，处理错误逻辑，例如显示错误信息
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    // 处理请求错误
    // console.error('请求出错', error);
    ElMessage.error('请求错误！', error);
    return
  }
};


const visible = ref(false);
let idx: number = -1;
const idEdit = ref(false);
const rowData = ref({});


const closeDialog = () => {
  visible.value = false;
  idEdit.value = false;
};

const visible1 = ref(false);
const handleView = (row: TableItem) => {
  rowData.value = row;
  visible1.value = true;
};




</script>

<style scoped>
.search-box {
  margin-bottom: 20px;
}

.search-input {
  width: 200px;
}

.search-box el-button {
  margin-left: 20px;
}

.mr10 {
  margin-right: 10px;
}

/* 为所有表头单元格设置背景颜色 */
.table.table-header {
  background-color: red; /* 你想要的颜色 */
}

.table-td-thumb {
  display: block;
  margin: auto;
  width: 40px;
  height: 40px;
}

/* 使用CSS实现单行文本溢出省略 */
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

