<template>
  <div>
    <!--    gutter指定列组件之间的间距，其默认值为0-->
    <el-row :gutter="20">
      <!--      span栅格占据的列数-->
      <el-col :span="24">
        <el-row :gutter="20" class="mgb20">
          <el-col :span="5">
            <router-link :to="{ name: 'publishing'}">
              <el-card shadow="hover" :body-style="{padding: '0px'}">
                <div class="grid-content grid-con-1">
                  <el-icon class="grid-con-icon">
                    <OfficeBuilding/>
                  </el-icon>
                  <div class="grid-cont-right">
                    <div class="grid-num">{{ publishing_num }}</div>
                    <div>出版社数量</div>
                  </div>
                </div>
              </el-card>
            </router-link>
          </el-col>
          <el-col :span="5">
            <router-link :to="{ name: 'author'}">
              <el-card shadow="hover" :body-style="{ padding: '0px' }">
                <div class="grid-content grid-con-2">
                  <el-icon class="grid-con-icon">
                    <Files/>
                  </el-icon>
                  <div class="grid-cont-right">
                    <div class="grid-num">{{ author_num }}</div>
                    <div>作者数量</div>
                  </div>
                </div>
              </el-card>
            </router-link>
          </el-col>
          <el-col :span="5">
            <router-link :to="{ name: 'classification'}">
              <el-card shadow="hover" :body-style="{padding: '0px'}">
                <div class="grid-content grid-con-1">
                  <el-icon class="grid-con-icon">
                    <Mic/>
                  </el-icon>
                  <div class="grid-cont-right">
                    <div class="grid-num">{{ bookType_num }}</div>
                    <div>图书类别种类</div>
                  </div>
                </div>
              </el-card>
            </router-link>
          </el-col>
          <el-col :span="5">
            <router-link :to="{ name: 'book'}">
              <el-card shadow="hover" :body-style="{ padding: '0px' }">
                <div class="grid-content grid-con-3">
                  <el-icon class="grid-con-icon">
                    <Notebook/>
                  </el-icon>
                  <div class="grid-cont-right">
                    <div class="grid-num">{{ book_num }}</div>
                    <div>图书总数</div>
                  </div>
                </div>
              </el-card>
            </router-link>
          </el-col>
          <el-col :span="4">
            <router-link :to="{ name: 'user'}">
              <el-card shadow="hover" :body-style="{padding: '0px'}">
                <div class="grid-content grid-con-1">
                  <el-icon class="grid-con-icon">
                    <User/>
                  </el-icon>
                  <div class="grid-cont-right">
                    <div class="grid-num">{{ user_num }}</div>
                    <div>已注册用户数</div>
                  </div>
                </div>
              </el-card>
            </router-link>
          </el-col>
        </el-row>
        <el-row>

        </el-row>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <div id="publishBookChart" style="height: 400px;width: 100%"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <div id="bookStatusChart" style="height: 400px;width: 100%"></div>
        </el-card>
      </el-col>


    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <div id="classificationBookChart" style="height: 400px;width: 100%"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div id="scoreBookChart" style="height: 400px;width: 100%"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="dashboard">
import * as echarts from 'echarts';
import {reactive, ref, onMounted} from 'vue';
import imgurl from '../assets/img/admin.png';
import {postRequest} from "../api";
import axios from "axios";
import moment from "moment";
import {Notebook} from "@element-plus/icons-vue";
import {useCookies} from "@vueuse/integrations/useCookies";
import {formatDateTime} from '../utils/timehandle';

const login_time = ref('');
const login_ip = ref('');
const login_site = ref('');
const publishing_num = ref(0);
const author_num = ref(0);
const book_num = ref(0);
const bookType_num = ref(0);
const user_num = ref(0);
const name = localStorage.getItem('ms_username');
const role: string = name === 'admin' ? '超级管理员' : '普通用户';
const namesList = ref<string[]>([]);


const options1 = ref({
  title: {
    text: '出版社图书数量',
    subtext: '单位: 本/册',
    // 可选：标题样式（如字体大小、颜色、对齐方式等）
    textStyle: {
      fontSize: 20,
      color: '#333',
      fontWeight: 'bold',
      align: 'center'
    },
    // 可选：标题位置
    left: 'center',

  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow',
    },
  },
  xAxis: {
    type: 'category',
    data: [],
    show: true,
    axisLabel: {
      rotate: 30, // 或者 270，取决于您希望X轴文字标签向上还是向下旋转

    },
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      type: 'bar',
      data: [],
      barGap: 300, // 使用百分比字符串
      label: {
        show: true,
        position: 'top',
        formatter: params => params.value,
      },
      emphasis: {
        itemStyle: {
          color: 'green',
        },
      },
    },
  ]
});


const options2 = ref({
  title: {
    text: '图书状态比例图',
    subtext: '单位: 本/册',
    left: 'center',
    textStyle: {
      fontSize: 20,
      color: '#333',
      fontWeight: 'bold',
      align: 'center'
    },
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '图书数量',
      type: 'pie',
      radius: '50%',
      data: [],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
});


const options3 = ref({
  title: {
    text: '各分类图书数量',
    subtext: '单位: 本/册',
    // 可选：标题样式（如字体大小、颜色、对齐方式等）
    textStyle: {
      fontSize: 20,
      color: '#333',
      fontWeight: 'bold',
      align: 'center'
    },
    // 可选：标题位置
    left: 'center',

  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow',
    },
  },
  xAxis: {
    type: 'category',
    data: [],
    show: true,
    axisLabel: {
      rotate: 30, // 或者 270，取决于您希望X轴文字标签向上还是向下旋转
    },
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      type: 'bar',
      data: [],
      barGap: 300, // 使用百分比字符串
      label: {
        show: true,
        position: 'top',
        formatter: params => params.value,
      },
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#337ecc' }
        ])
      },
      emphasis: {
        itemStyle: {
          color: 'green',
        },
      },
    },
  ]
});

const options4 = ref({
  title: {
    text: '图书评分Top10',
    subtext: '单位: 分',
    // 可选：标题样式（如字体大小、颜色、对齐方式等）
    textStyle: {
      fontSize: 20,
      color: '#333',
      fontWeight: 'bold',
      align: 'center'
    },
    // 可选：标题位置
    left: 'center',

  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    boundaryGap: [0, 0.01]
  },
  yAxis: {
    type: 'category',
    data: []
  },
  series: [
    {
      type: 'bar',
      itemStyle: {
        // 设置默认颜色
        color: new echarts.graphic.LinearGradient(
            0, 0, 1, 0,
            [
              {offset: 0, color: '#F9FB81'},
              {offset: 1, color: '#F20404'}
            ], false),
      },
      data: []
    }
  ]
});

//定义数据接口，需要和后端返回的数据字段一致
interface TableInfo {
  name: string;
  number: number;
  statistics: object,
  // 根据实际情况补充其他属性
}

const tableInfos = ref<TableInfo[]>([]);
const tableInfos1 = ref<TableInfo[]>([]);
//在组件挂载后发起请求获取相关信息用于更新dashboard上的变量信息
onMounted(async () => {
  try {
    // 查询IP地址
    // const response = await axios.get('http://ip-api.com/json/', {});
    // const response =await axios.get('https://ip.useragentinfo.com/json',{})
    // 查询登录的用户信息
    const response1 = await postRequest('/user/query', {'name': name});
    login_time.value = formatDateTime(response1.data.infos[0].last_login_time);
    login_ip.value = response1.data.infos[0].ip;

    // 统计学院、专业、学生数量
    const response2 = await postRequest('/publishing/count', {});
    const response3 = await postRequest('/author/count', {});
    const response4 = await postRequest('/book/count', {});
    const response5 = await postRequest('/book/count_by_publishing', {});
    const response6 = await postRequest('/user/count', {});
    const response7 = await postRequest('/classification/count', {});
    const response8 = await postRequest('/book/count_by_score', {});
    user_num.value = response6.data.count;
    // 查询用户登录地址


    //数据库中表的数量
    publishing_num.value = response2.data.count
    author_num.value = response3.data.count
    book_num.value = response4.data.count
    bookType_num.value = response7.data.count
    //数据库中所有表的表名列表更新到视图上
    tableInfos.value = response5.data.infos
    namesList.value = tableInfos.value.map(info => info.name);

    options1.value.xAxis.data = tableInfos.value.filter(item => item.number !== 0).map(item => item.name);
    const filteredData = tableInfos.value.filter(item => item.number !== 0);
    options1.value.series[0].data = filteredData.map(item => item.number);

    tableInfos1.value = response5.data.classification_infos
    options3.value.xAxis.data = tableInfos1.value.filter(item => item.number !== 0).map(item => item.name);
    const filteredData1 = tableInfos1.value.filter(item => item.number !== 0);
    options3.value.series[0].data = filteredData1.map(item => item.number);
    // const inboundPercent = parseFloat(((response5.data.statistics.inbound_number / book_num.value) * 100).toFixed(2));
    // const outboundPercent = parseFloat(((response5.data.statistics.outbound_number / book_num.value) * 100).toFixed(2));
    // const missPercent = parseFloat(((response5.data.statistics.miss_number / book_num.value) * 100).toFixed(2));
    // const expired_number = parseFloat(((response5.data.statistics.expired_number / book_num.value) * 100).toFixed(2));
    const inboundPercent = response5.data.statistics.inbound_number;
    const outboundPercent = response5.data.statistics.outbound_number;
    const missPercent = response5.data.statistics.miss_number;
    const expired_number = response5.data.statistics.expired_number;

    options2.value.series[0].data = [{name: '未借出', value: inboundPercent}, {
      name: '已借出',
      value: outboundPercent
    }, {name: '挂失', value: missPercent}, {name: '逾期', value: expired_number}];

    options4.value.yAxis.data = response8.data.infos.map(info => info.name).reverse();
    options4.value.series[0].data = response8.data.infos.map(info => info.score).reverse();
    const myChart1 = echarts.init(document.getElementById('publishBookChart'));
    myChart1.setOption(options1.value);
    const myChart2 = echarts.init(document.getElementById('bookStatusChart'));
    myChart2.setOption(options2.value);

    const myChart3 = echarts.init(document.getElementById('classificationBookChart'));
    myChart3.setOption(options3.value);

    const myChart4 = echarts.init(document.getElementById('scoreBookChart'));
    myChart4.setOption(options4.value);
  } catch (error) {
    console.error('网络错误:', error);
    return;
  }
})


</script>

<style scoped>
.el-row {
  margin-bottom: 20px;
}

.grid-content {
  display: flex;
  align-items: center;
  height: 100px;
}

.grid-cont-right {
  flex: 1;
  text-align: center;
  font-size: 14px;
  color: #999;
}

.grid-num {
  font-size: 30px;
  font-weight: bold;
}

.grid-con-icon {
  font-size: 50px;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
  color: #fff;
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
  margin-bottom: 1px;
}

.todo-item {
  font-size: 14px;
}

.todo-item-del {
  text-decoration: line-through;
  color: #999;
}

.schart {
  width: 100%;
  height: 400px;
}
</style>
