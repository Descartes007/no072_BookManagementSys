<!-- 图书详情页的模板 -->
<template>
  <el-descriptions title="" :column="1" class="description-container" border>
    <!--		<el-descriptions-item>-->
    <!--			<template #label> ID </template>-->
    <!--			{{ data.id }}-->
    <!--		</el-descriptions-item>-->
    <el-descriptions-item>
      <template #label> 照片</template>
      <img :src="data.photo" alt=""/>
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 书名</template>
      {{ data.name }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 条形码</template>
      {{ data.isbn_number }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 出版社</template>
      {{ data.publishing }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 作者</template>
      {{ data.author }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 类别</template>
      {{ data.book_type }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 价格</template>
      ￥ {{ data.book_price }}
    </el-descriptions-item>
    <el-descriptions-item v-if="name=='admin'">
      <template #label> 状态</template>
      {{ data.book_status == 0 ? '入库' : (data.book_status == 1 ? '已借出' : '遗失') }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 出版时间</template>
      {{ formatDateTime(data.publish_time) }}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 入库时间</template>
      {{ formatDateTime(data.inbound_time) }}
    </el-descriptions-item>
    <el-descriptions-item v-if="data.borrowers">
      <template #label> 借阅人</template>
      {{ data.borrowers }}
    </el-descriptions-item>
    <el-descriptions-item v-if="data.outbound_time">
      <template #label> 借阅时间</template>
      {{ formatDateTime(data.outbound_time) }}
    </el-descriptions-item>
	<el-descriptions-item>
      <template #label> 评分</template>
      {{ data.score == 0 ? '还没有人对它评分哟！' : data.score}}
    </el-descriptions-item>
    <el-descriptions-item>
      <template #label> 简介</template>
      {{ data.description }}
    </el-descriptions-item>
    <el-descriptions-item v-if="data.borrow_history">
       <template #label> 借阅归还记录</template>
      <el-timeline style="max-width: 600px">
        <el-timeline-item
            v-for="(historyItem, index) in formattedHistory"
            :key="index"
            :timestamp="historyItem.time"
        >
          用户: {{ historyItem.user }}  {{historyItem.event}}
        </el-timeline-item>
      </el-timeline>
    </el-descriptions-item>

  </el-descriptions>
</template>

<script lang="ts" setup>
import moment from "moment/moment";
import {formatDateTime} from '../utils/timehandle';
import {computed} from "vue";

const name = localStorage.getItem('ms_username');
const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const formattedHistory = computed(() => {
  // 首先，按照时间戳排序原始数据
  const sortedHistory = props.data.borrow_history.sort((a, b) =>b.time- a.time);

  // 然后，将排序后的数据映射为所需格式
  return sortedHistory.map(item => ({
    time: formatDateTime(item.time), // 转换时间戳为日期字符串
    user: item.user,
    event: item.event,
  }));
});

</script>

<style>
.description-container img {
  max-width: 100%;
  height: 300px;
}

</style>