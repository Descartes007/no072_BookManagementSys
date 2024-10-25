<template>
  <div>
    <div class="container">
      <el-table :data="filteredData" border class="table" ref="multipleTable" header-cell-class-name="table-header"
                @selection-change="handleSelectionChange">
        <!-- prop用于父组件向子组件传递数据，允许父组件将数据作为一个属性传递给子组件，子组件通过props选项中声明接收哪些属性，父组件则可以通过模板语法将数据绑定到子组件的 prop 上。-->
        <!--prop 数据流向是从父组件到子组件，通常是单向的。-->
        <el-table-column prop="id" label="ID" width="55" align="center" type="selection"></el-table-column>
        <el-table-column prop="id" label="ID" width="100" align="center" sortable></el-table-column>
        <!-- 使用了 Vue 的插槽 #default 自定义单元格的渲染方式。{ scope } 参数表示当前行的数据对象。-->
        <el-table-column prop="photo" label="图片" width="200" align="center">
          <template #default="scope">
            <el-image
                style="width: 100px; height: 100px"
                :src="scope.row.photo"
                fit="cover"
                @click="showImageViewer(scope.row.photo)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="书名" width="200" align="center"></el-table-column>
        <el-table-column prop="publishing" label="出版社" align="center"></el-table-column>
        <el-table-column prop="author" label="作者" align="center"></el-table-column>
        <el-table-column prop="description" label="简介" align="center"></el-table-column>
        <el-table-column label="操作" align="center">
          <template #default="scope">
              <el-button
                  type="success"
                  size="small"
                  class="el-icon-lx-back"
                  @click="handleCancell(scope.row.id)"
              >
                取消收藏
              </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-image-viewer
          v-if="viewer.show"
          :on-close="closeImageViewer"
          :initial-index="viewer.currentIndex"
          :url-list="viewer.urlList"
          :z-index="2000"
          @close="closeImageViewer"
      />

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
import {ref, reactive, computed, onMounted, watch} from 'vue';
import {ElMessage, ElMessageBox, ElImageViewer} from 'element-plus';
import {Delete, Edit, Search, CirclePlusFilled, View, Refresh} from '@element-plus/icons-vue';
import {postRequest} from '../api/index';
import TableEdit from './entry-edit.vue';
import TableDetail from './entry-detail.vue';
import {useRoute, useRouter} from "vue-router";
import moment from 'moment';
import * as XLSX from 'xlsx';
import {formatDateTime} from '../utils/timehandle';

//这个接口里的字段名必须要和后端返回的接口字段一直，否则无法显示
interface TableItem {
  id: number;
  name: string;
  isbn_number: string;
  publishing: string;
  author: string;
  publish_time: string;
  book_price: string;
  book_status: number;
  inbound_time: string;
  outbound_time: string;
  photo: string;
  borrowers: string;
  description: string;
  expire_time: string;
};

const currentPage = ref(1);
const pageSize = ref(10);
const route = useRoute();
const router = useRouter();
const searchKey = ref('');
const publishers = ref([]);
const authors = ref([]);

const tableData = ref<TableItem[]>([]);
const pageTotal = ref(0);
const name = localStorage.getItem('ms_username');

const viewer = ref({
  show: false,
  currentIndex: 0,
  urlList: [],
});


const selectDict = ref({
  bookName: '',
  publisher: '',
  author: ''
});

// 放大图片展示
const showImageViewer = (photo) => {
  viewer.value.urlList = [photo];
  viewer.value.currentIndex = 0;
  viewer.value.show = true;
};


// 关闭图片展示
const closeImageViewer = () => {
  viewer.value.show = false;
  viewer.value.urlList = [];
};


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

//onMounted 钩子函数在组件挂载后发起 AJAX 请求。这是一个生命周期钩子，会在组件 DOM 渲染完成后执行
onMounted(async () => {
  // 初始化加载第一页数据
  getData({query_string: searchKey.value, page: currentPage.value, size: pageSize.value,username:name});
  try {
    const response1 = await postRequest('/publishing/query', {});
    if (response1.data.status) {
      publishers.value = response1.data.infos;
    } else {
      console.log(response1.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }
  try {
    const response2 = await postRequest('/author/query', {});

    if (response2.data.status) {
      authors.value = response2.data.infos;
    } else {
      console.log(response2.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }

});


// 查询操作
// 搜索框模糊查询操作,不会向后端发起请求，只是对当前table数据过滤显示
// 计算属性，用于过滤数据
const filteredData = computed(() => {
  const keyword = searchKey.value.toLowerCase();
  return tableData.value.filter(item => {
    return (
        //希望对哪些字段进行模糊查询就在这里添加
        item.name.toString().includes(keyword)
    );
  });
});

//根据查询条件检索后端数据
const handleSearch = () => {
  getData({
    username: name,
    bookname: selectDict.value.bookName,
    publisher: selectDict.value.publisher,
    author: selectDict.value.author,
  });
};


//切换每一页的条目数量
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


//取消收藏图书
const handleCancell = async (id: number) => {
  ElMessageBox.confirm('确定取消收藏该图书吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const response = await postRequest('/collect/cancel', {id: id, "username": name});
      if (response.data.status) {
        // 归还成功后立刻更新表格数据，不用刷新整个网页
        const newData = tableData.value.filter(item => item.id !== id);
        tableData.value = newData;
        ElMessage.success(response.data.message);

      } else {
        // 请求失败，处理错误逻辑，例如显示错误信息
        //   console.error('编辑失败', response.data.message);
        ElMessage.error(response.data.message);
      }
    } catch (error) {
      // 处理请求错误
      console.error('请求出错', error);
      ElMessage.error('请求错误！');
    }
  }).catch(() => {
  });
};

const visible = ref(false);
let idx: number = -1;
const idEdit = ref(false);
const rowData = ref({});
const handleEdit = (index: number, row: TableItem) => {
  idx = index;
  rowData.value = row;
  idEdit.value = true;
  visible.value = true;

};


const updateData = (row: TableItem) => {
  idEdit.value ? (tableData.value[idx] = row) : tableData.value.unshift(row);
  closeDialog();
};

const closeDialog = () => {
  visible.value = false;
  idEdit.value = false;
};

const visible1 = ref(false);
const handleView = (row: TableItem) => {
  rowData.value = row;
  visible1.value = true;
};


// 获取当前系统10位时间戳

function getCurrentTime() {
  return Math.round(Date.now() / 1000);
}

//根据不同的值显示颜色
function getBookStatusColor(status: number) {
  switch (status) {
    case 0:
      return 'green'; // 入库状态为绿色
    case 1:
      return 'blue'; // 已借阅状态为蓝色
    default:
      return 'red'; // 其他状态（如遗失）为红色
  }
};

function getBookExpireStatusColor(status: boolean) {
  switch (status) {
    case true:
      return 'green'; // 未到期状态为绿色
    case false:
      return 'red'; // 到期状态为蓝色
    default:
      return 'green'; // 其他状态
  }
};

</script>

<style scoped>
.search-box {
  margin-bottom: 20px;
}

.search-input {
  width: 200px;
}

.mr10 {
  margin-right: 10px;
}

.search-box-1 {
  display: flex; /* 启用 Flexbox 布局 */
  align-items: center; /* 垂直居中 */
  margin-bottom: 20px; /* 你可以根据需要调整这个值 */
}

.muilt_search-input {
  margin-right: 10px; /* 设置元素之间的间隔 */
}

/* 最后一个元素不需要右边距 */
.muilt_search-input:last-child {
  margin-right: 0;
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


/* scrollbar横向滚动条 */
.scrollbar-flex-content {
  display: flex;
}

.scrollbar-demo-item {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 50px;
  margin: 10px;
  text-align: center;
  border-radius: 4px;
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}
</style>

