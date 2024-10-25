<template>
  <div>
    <div class="container">
      <div class="search-box">
        <el-button type="primary" :icon="CirclePlusFilled" @click="visible = true" v-permiss="17">新增图书</el-button>
        <el-upload
            :action="uploadUrl"
            :limit="1"
            :file-list="fileList"
            accept=".xlsx, .xls"
            :show-file-list="false"
            :auto-upload="true"
            :before-upload="beforeUpload"
            :http-request="handleUploadExcel"
            :headers="uploadHeaders"
            v-permiss="21"
        >
          <el-tooltip
              effect="dark"
              placement="top"
              content="批量导入前请先下载模板，使用模板上传"
          >
            <el-button class="mr10" type="primary">批量导入</el-button>
          </el-tooltip>
        </el-upload>
        <el-button type="primary" @click="exportXlsx" v-permiss="21">导出数据为Excel</el-button>
        <!-- 删除选中行的按钮 -->
        <el-button type="danger" :icon="Delete" @click="deleteSelectedRows">删除选中行</el-button>
        <el-link href="/template.xlsx" target="_blank">下载模板</el-link>

      </div>

      <div class="search-box-1">
        <el-input v-model="selectDict.bookName" placeholder="请输入书名" class="muilt_search-input"
                  clearable></el-input>
        <el-select v-model="selectDict.publisher" placeholder="请选择出版社" class="muilt_search-input" filterable
                   clearable>
          <el-option v-for="(item, index) in publishers" :key="index" :value="item.id"
                     :label="item.name"></el-option>
        </el-select>
        <el-select v-model="selectDict.author" placeholder="请选择作者" class="muilt_search-input" filterable clearable>
          <el-option v-for="(item, index) in authors" :key="index" :value="item.id"
                     :label="item.name"></el-option>
        </el-select>
        <el-select v-model="selectDict.status" placeholder="请选择状态" class="muilt_search-input" clearable>
          <el-option v-for="(item, index) in statusDict" :key="index" :value="item.id"
                     :label="item.name"></el-option>
        </el-select>
        <!--        </el-input>-->
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button type="primary" :icon="Refresh" @click="handleReset">重置</el-button>
      </div>
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
		<el-table-column prop="score" label="推荐分" align="center" sortable></el-table-column>
        <el-table-column prop="isbn_number" label="ISBN条形码" align="center"></el-table-column>
        <el-table-column prop="publishing" label="出版社" align="center"></el-table-column>
        <el-table-column prop="author" label="作者" align="center"></el-table-column>
        <el-table-column prop="book_type" label="类别" align="center"></el-table-column>
        <el-table-column prop="book_price" label="价格" width="100" align="center">
          <template #default="scope">
            <span>￥ {{ scope.row.book_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="book_status" v-if="name=='admin'" label="状态" width="100" align="center">
          <template #default="scope">
            <span :style="{ color: getBookStatusColor(scope.row.book_status) }">{{
                scope.row.book_status == 0 ? '入库' : (scope.row.book_status == 1 ? '已借出' : '遗失')
              }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="publish_time" label="出版时间" align="center" v-if="false"></el-table-column>
        <el-table-column prop="inbound_time" label="入库时间" align="center" v-if="false"></el-table-column>
        <el-table-column prop="borrowers" label="借阅人" align="center" v-if="false"></el-table-column>
        <el-table-column prop="outbound_time" label="借阅时间" align="center" v-if="false"></el-table-column>
        <el-table-column prop="description" label="简介" align="center" v-if="false"></el-table-column>
        <el-table-column prop="borrow_history" label="借阅历史" align="center" v-if="false"></el-table-column>
        <el-table-column label="操作" width="280" align="center">
          <template #default="scope">
            <el-button type="warning" size="small" :icon="View" @click="handleView(scope.row)">
              详情
            </el-button>
            <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEdit(scope.$index, scope.row)"
                v-permiss="18"
            >
              编辑
            </el-button>
            <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(scope.row.id)"
                v-permiss="19"
            >
              删除
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
    <el-dialog
        :title="idEdit ? '编辑图书信息' : '添加图书信息'"
        v-model="visible"
        width="500px"
        destroy-on-close
        :close-on-click-modal="false"
        @close="closeDialog"
    >
      <TableEdit :data="rowData" :edit="idEdit" :update="updateData"/>
    </el-dialog>
    <el-dialog title="图书详细信息" v-model="visible1" width="1000px" destroy-on-close>
      <TableDetail :data="rowData"/>
    </el-dialog>
  </div>

</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, computed, onMounted, watch} from 'vue';
import {ElMessage, ElMessageBox, ElImageViewer, UploadProps} from 'element-plus';
import {Delete, Edit, Search, CirclePlusFilled, View, Refresh} from '@element-plus/icons-vue';
import {postRequest} from '../api/index';
import TableEdit from './entry-edit.vue';
import TableDetail from './entry-detail.vue';
import * as XLSX from 'xlsx';
import {formatDateTime} from '../utils/timehandle';
import {useRoute, useRouter} from "vue-router";
import webServerSrc from "../components/global.vue";
import axios from "axios";


//这个接口里的字段名必须要和后端返回的接口字段一直，否则无法显示
interface TableItem {
  id: number;
  name: string;
  isbn_number: string;
  publishing: string;
  author: string;
  book_type: string;
  publish_time: string;
  book_price: string;
  book_status: number;
  inbound_time: string;
  outbound_time: string;
  photo: string;
  borrowers: string;
  borrow_history: object;
  description: string;
};

const uploadUrl = ref(webServerSrc.webServerSrc).value + '/batch_upload';
const fileList = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const route = useRoute();
const router = useRouter();
const searchKey = ref('');
const publishers = ref([]);
const authors = ref([]);
const book_types = ref([]);
const tableData = ref<TableItem[]>([]);
const pageTotal = ref(0);
const name = localStorage.getItem('ms_username');
const viewer = ref({
  show: false,
  currentIndex: 0,
  urlList: [],
});

const uploadHeaders = reactive({
  'X-Access-Token': localStorage.getItem('token'),
  'Refresh-Token': localStorage.getItem('refresh_token'),
  'Content-Type': 'multipart/form-data'
});
const statusDict = ref([{name: '入库', id: 0},
  {name: '已借出', id: 1}, {name: '遗失', id: 2}]);
const selectDict = ref({
  bookName: '',
  publisher: '',
  author: '',
  status: '',
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
  getData({query_string: searchKey.value, page: currentPage.value, size: pageSize.value});
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
  ;
  try {
    const response3 = await postRequest('/classification/query', {});

    if (response3.data.status) {
      book_types.value = response3.data.infos;
    } else {
      console.log(response3.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }
  ;

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
    bookname: selectDict.value.bookName,
    publisher: selectDict.value.publisher,
    author: selectDict.value.author,
    status: selectDict.value.status
  });
};

//重置搜索条件
const handleReset = async () => {
  selectDict.value.bookName = '';
  selectDict.value.publisher = '';
  selectDict.value.author = '';
  selectDict.value.status = '';
  getData({query_string: "", page: currentPage.value, size: pageSize.value});
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

//删除多行数据
const deleteSelectedRows = async () => {
      if (selectedRows.value.length > 0) {
        const ids = selectedRows.value.map(item => item.id);
        try {
          const response = await postRequest(route.fullPath + '/delete', {id: ids});
          if (response.data.status) {
            // 请求成功，处理成功逻辑，例如显示通知或跳转页面
            //props.update(form.value);
            ElMessage.success(response.data.message);
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
        ;
        // 成功响应后，从前端数据和选中列表中移除这些项
        selectedRows.value.forEach(row => {
          const index = tableData.value.findIndex(item => item.id === row.id);
          if (index > -1) {
            tableData.value.splice(index, 1);
          }
        });
        selectedRows.value = [];
      } else {
        ElMessage.error('请先选择要删除的条目');
      }
    }
;

// 删除单条数据操作
const handleDelete = (id: number) => {
  // 二次确认删除
  ElMessageBox.confirm('确定要删除吗？', '提示', {
    type: 'warning'
  })
      .then(async () => {
        //向后端发起请求
        try {
          // 发起 HTTP 请求
          const response = await postRequest(route.fullPath + '/delete', {id: id});
          // 处理响应
          if (response.data.status) {
            // 请求成功，处理成功逻辑，例如显示通知或跳转页面
            //   console.log('编辑成功', response.data);

            // 删除成功后立刻更新表格数据，不用刷新整个网页
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

      })
      .catch(() => {
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


//把数据导出为excel
const list = [['id', '书名', 'ISBN条形码', '出版社', '所属类别', '作者', '价格', '状态', '出版时间', '入库时间', '借阅人', '借阅时间', '封面图片', '简介']];
const exportXlsx = () => {
  tableData.value.map((item: any, i: number) => {
    const arr: any[] = [i + 1];
    arr.push(...[item.name, item.isbn_number, item.publishing, item.type, item.author, item.book_price, item.book_status == 0 ? '入库' : (item.book_status == 1 ? '已借出' : '遗失'), formatDateTime(item.publish_time), formatDateTime(item.inbound_time), item.borrowers, formatDateTime(item.outbound_time), item.photo, item.description]);
    list.push(arr);
  });
  let WorkSheet = XLSX.utils.aoa_to_sheet(list);
  let new_workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(new_workbook, WorkSheet, 'index-1');
  XLSX.writeFile(new_workbook, `图书数据.xlsx`);
};


const importList = ref<any>([]);
//文件实际上传之前被调用,接收一个参数 rawFile，即用户选择的原始文件对象
const beforeUpload: UploadProps['beforeUpload'] = async (rawFile) => {
  // 验证文件类型
  const isExcel = rawFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
      rawFile.type === 'application/vnd.ms-excel';
  if (!isExcel) {
    ElMessage.error('请上传Excel文件！');
    return false;
  }

  // 验证文件大小（例如，限制最大为5MB）
  const maxSize = 5 * 1024 * 1024; // 5MB
  if (rawFile.size > maxSize) {
    ElMessage.error('文件大小超过5MB限制！');
    return false;
  }

  // 文件通过验证，进行解析
  handleUploadExcel(rawFile);
  return false; // 阻止默认的上传行为，因为自己处理了文件发送
};
const analysisExcel = (file: any) => {
  return new Promise(function (resolve, reject) {
    const reader = new FileReader();
    reader.onload = function (e: any) {
      const data = e.target.result;
      let datajson = XLSX.read(data, {
        type: 'binary',
      });

      const sheetName = datajson.SheetNames[0];
      const result = XLSX.utils.sheet_to_json(datajson.Sheets[sheetName]);
      resolve(result);
    };
    reader.readAsBinaryString(file);
  });
};

const handleUploadExcel = async (file: File) => {
  //这里写批量上传逻辑，向后端发送请求最后更新数据
  try {
    // 创建一个FormData实例
    const formData = new FormData();

    // 将文件添加到formData中，这里假设后端接收文件的字段名为'file'
    formData.append('file', file);

    // 发送POST请求到Flask后端，确保这里的URL与你的Flask路由匹配
    const response = await axios.post(uploadUrl, formData, {
      headers: uploadHeaders,
      // 可以根据需要添加认证信息等其他自定义请求头
    });

    if (response.data.status) {
      ElMessage.success(response.data.message);
      getData({query_string: searchKey.value, page: currentPage.value, size: pageSize.value});
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    console.error('文件上传错误:', error);
    ElMessage.error('文件上传发生错误，请稍后重试。');
  }
};
</script>

<style scoped>
.search-box {
  display: flex;
  align-items: center; /* 保持垂直居中 */
  margin-bottom: 20px;
  gap: 20px; /* 在Flex子元素之间添加间距 */
  flex-wrap: wrap; /* 允许换行，如果需要的话 */
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

