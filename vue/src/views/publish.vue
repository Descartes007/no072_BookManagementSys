<template>
  <div>
    <div class="container">
      <div class="search-box">
        <el-input v-model="searchKey" placeholder="请输入搜索内容" class="search-input mr10" clearable  @clear="handleClear"></el-input>
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button type="primary" :icon="CirclePlusFilled" @click="visible = true" v-permiss="11">新增</el-button>
        <!-- 删除选中行的按钮 -->
        <el-button type="danger" :icon="Delete" @click="deleteSelectedRows">删除选中行</el-button>

      </div>
      <el-table :data="filteredData" border class="table" ref="multipleTable" header-cell-class-name="table-header"
                @selection-change="handleSelectionChange" @sort-change="handleTableSort">
        <el-table-column prop="id" label="ID" width="55" align="center" type="selection"></el-table-column>
        <el-table-column prop="id" label="ID" width="70" align="center" sortable="true"></el-table-column>
        <el-table-column prop="name" label="出版社名称" align="center"></el-table-column>
        <el-table-column label="操作" width="280" align="center">
          <template #default="scope">
            <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEdit(scope.$index, scope.row)"
                v-permiss="12"
            >
              编辑
            </el-button>
            <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(scope.row.id)"
                v-permiss="13"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
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
    <el-dialog
        :title="idEdit ? '编辑出版社' : '添加出版社'"
        v-model="visible"
        width="500px"
        destroy-on-close
        :close-on-click-modal="false"
        @close="closeDialog"
    >
      <TableEdit :data="rowData" :edit="idEdit" :update="updateData"/>
    </el-dialog>

  </div>
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, computed, onMounted} from 'vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {Delete, Edit, Search, CirclePlusFilled, View} from '@element-plus/icons-vue';
import {postRequest} from '../api/index';
import TableEdit from './publish-edit.vue';
import {useRoute} from "vue-router";
import moment from 'moment';
import * as XLSX from 'xlsx';

//这个接口里的字段名必须要和后端返回的接口字段一直，否则前端无法显示
interface TableItem {
  id: number;
  name: string;
};

const currentPage = ref(1);
const pageSize = ref(10);
const route = useRoute();
const searchKey = ref('');


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

//根据ID对表格数据进行本地排序
function handleTableSort(sort) {
  const {prop, order} = sort;

  if (prop === 'id') {
    tableData.value = tableData.value.sort((a, b) => {
      let compareValue = a[prop] - b[prop];
      // 升序排列
      if (order === 'ascending') {
        return compareValue;
      }
      // 降序排列
      else if (order === 'descending') {
        return -compareValue;
      }
      // 其他情况（如无排序或排序字段不是 'id'）不做处理，返回原数据顺序
      return 0;
    });
  }
}

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
        item.name.toString().includes(keyword)
    );
  });
});


const handleSearch = () => {
  getData({'query_string': searchKey.value});
};

const handleClear = () => {
  searchKey.value = '';
  getData({'query_string': searchKey.value,page: currentPage.value, size: pageSize.value});
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
          console.log(response.data.status)
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

