<template>
  <div>
    <!--    gutter指定列组件之间的间距，其默认值为0-->
    <el-row :gutter="20">
      <!--      span栅格占据的列数-->
      <el-col :span="10">
        <el-card shadow="hover" class="mgb20" style="height: 240px">
          <div class="user-info">
            <el-avatar :size="100" :src="imgurl"/>
            <div class="user-info-cont">
              <div class="user-info-name">欢迎您！{{ name }}</div>
              <br>
              <div>{{ role }}</div>
            </div>
          </div>
          <div class="user-info-list">
            登录时间：
            <span>{{ login_time }}</span>
          </div>
          <div class="user-info-list">
            登录地址：
            <span>{{ login_ip }}</span>
          </div>
        </el-card>

      </el-col>
      <el-col :span="14">
        <div class="container">
          <el-tabs v-model="message">
            <el-tab-pane :label="`系统公告(${state.unread.length})`" name="first">
              <el-table :data="state.unread.slice(0,3)" :show-header="false" style="width: 100%">
                <el-table-column prop="title">
                  <template #default="scope">
                    <span class="message-title" @click="viewNotice(scope.row.title)">{{ scope.row.title }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="release_time" width="180">
                  <template #default="scope">
                    <span class="message-title">{{ formatDateTime(scope.row.release_time) }}</span>
                  </template>
                </el-table-column>
                <el-table-column width="120">
                  <template #default="scope">
                    <el-button size="small" @click="handleRead(scope.$index)">标为已读</el-button>
                  </template>
                </el-table-column>
              </el-table>

            </el-tab-pane>

          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>
  <div class="book-recommendation">
    <el-carousel trigger="click" height="800px" arrow="always" type="card" motion-blur="true">
      <el-carousel-item v-for="(book, index) in recommendedBooks" :key="index">
        <div class="book-card" @click="viewBookDetails(book.id)">
          <img :src="book.photo" alt="图书封面" class="book-cover">
          <div class="book-info">
            <p class="book-title">《{{ book.name }}》</p>
            <!--            <p class="book-author">{{ book.author }}</p>-->
            <!--            <p class="book-publisher">{{ book.publishing }}</p>-->
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
  </div>
</template>

<script setup lang="ts" name="tabs">
import {ref, reactive, onMounted, computed} from 'vue';
import imgurl from "../assets/img/admin.png";
import {postRequest} from "../api";
import {ElNotification} from 'element-plus';
import {formatDateTime} from '../utils/timehandle';
import {useRouter} from "vue-router";
import BookDetail from "./book-detail.vue"

const login_time = ref('');
const login_ip = ref('');
const user_num = ref(0);
const name = localStorage.getItem('ms_username');
const role: string = name === 'admin' ? '超级管理员' : name === 'audit' ? '审计员' : '读者';
const recommendedBooks = ref([]);
const message = ref('first');
const state = reactive({unread: []});
// 获取Vue Router实例
const router = useRouter();

// 创建一个计算属性来获取通知信息列表按id降序排序后的通知数组
const sortedNotices = computed(() => {
  return [...state.unread].sort((a, b) => b.id - a.id);
});

// 创建另一个计算属性来获取通知信息列表id最大的那条通知信息
const maxIdNotice = computed(() => {
  return sortedNotices.value[0];
});
onMounted(async () => {
  try {
    // 查询IP地址
    // const response = await axios.get('http://ip-api.com/json/', {});
    // const response =await axios.get('https://ip.useragentinfo.com/json',{})
    // 查询登录的用户信息
    const response1 = await postRequest('/user/query', {'name': name});
    login_time.value = formatDateTime(response1.data.infos[0].last_login_time);
    login_ip.value = response1.data.infos[0].ip;

    const response2 = await postRequest('/user/count', {});
    const response3 = await postRequest('/book/query', {rd_num: 10})
    const response4 = await postRequest('/notice/query', {})
    user_num.value = response2.data.count;
    recommendedBooks.value = response3.data.infos;
    state.unread = response4.data.infos;
    //主动弹出最后一条公告内容
    viewNotice(maxIdNotice.value.title);
  } catch (e) {
    console.log("网络请求错误", e);
    return;
  }
  ;
});


const handleRead = (index: number) => {
  const item = state.unread.splice(index, 1);
  state.read = item.concat(state.read);
};

// 查看图书详情的方法
const viewBookDetails =  (bookId) => {
  try {
    router.push({name: 'BookDetail', params: {bookId}});
  } catch (error) {
    console.error('Error fetching book details:', error);
  }
};

const viewNotice = (title: string) => {
  const noticeContent = state.unread.find((notice) => notice.title === title)?.content;
  if (noticeContent) {
    ElNotification({
      title,
      message: noticeContent,
      type: 'info',
      duration: 3000,
    });
  } else {
    console.error('查看公告内容失败');
  }

};
const handleRestore = (index: number) => {
  const item = state.recycle.splice(index, 1);
  state.read = item.concat(state.read);
};
</script>

<style>
.message-title {
  cursor: pointer;
}


.book-recommendation {
  width: 100%;
  height: 800px;
}

.book-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
  background-color: #787878;
}

.book-cover {
  width: 100%;
  height: 700px;
  object-fit: cover;
  margin-bottom: 10px;
}

.book-info {
  background-color: rgba(0, 0, 0, 0.5);
  padding: 10px;
}


.grid-con-1 .grid-con-icon {
  background: rgb(45, 140, 240);
}

.grid-con-1 .grid-num {
  color: rgb(45, 140, 240);
}

.grid-con-2 .grid-con-icon {
  background: rgb(100, 213, 114);
}

.grid-con-2 .grid-num {
  color: rgb(100, 213, 114);
}

.grid-con-3 .grid-con-icon {
  background: rgb(242, 94, 67);
}

.grid-con-3 .grid-num {
  color: rgb(242, 94, 67);
}

.user-info {
  display: flex;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 2px solid #ccc;
  margin-bottom: 20px;
}

.user-info-cont {
  padding-left: 50px;
  flex: 1;
  font-size: 14px;
  color: #999;
}

.user-info-cont div:first-child {
  font-size: 30px;
  color: #606266;
}

.user-info-list {
  font-size: 20px;
  color: #606266;
  line-height: 25px;
}

.user-info-list span {
  margin-left: 10px;
}

.mgb20 {
  margin-bottom: 10px;
}


</style>
