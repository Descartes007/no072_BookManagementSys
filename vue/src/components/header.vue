<template>
  <div class="header">
    <!-- 折叠按钮 -->

    <div class="logo">图书管理系统</div>
    <div class="collapse-btn" @click="collapseChage">
      <el-icon v-if="sidebar.collapse">
        <Expand/>
      </el-icon>
      <el-icon v-else>
        <Fold/>
      </el-icon>
    </div>
    <el-drawer v-model="visible" title="个性化配置" size="20%">
      <!--      <template #header="{ close, titleId, titleClass }">-->
      <!--        <h3 :id="titleId" :class="titleClass">项目配置</h3>-->
      <!--      </template>-->
      <div class="color-picker-container">
        <span class="text1">修改颜色方案</span>
        <!-- 颜色选择器 -->
        <el-color-picker
            v-model="selectedColor1"
            :popper-class="'color-picker-dropdown'"
            @change="handleColorChange1"
        ></el-color-picker>
        <br>
        <br>
        <span class="text1">修改表头颜色</span>
        <!-- 颜色选择器 -->
        <el-color-picker
            v-model="selectedColor2"
            :popper-class="'color-picker-dropdown'"
            @change="handleColorChange2"
            style="margin-top: 10px"
        ></el-color-picker>
        <br>
        <br>
        <span class="text1">修改活动标签页颜色</span>
        <!-- 颜色选择器 -->
        <el-color-picker
            v-model="selectedColor3"
            :popper-class="'color-picker-dropdown'"
            @change="handleColorChange3"
            style="margin-top: 10px"
        ></el-color-picker>
      </div>
      <el-divider/>

    </el-drawer>

    <div class="header-setting">
      <el-icon @click="handleSetting">
        <Setting/>
      </el-icon>
    </div>
    <div class="header-right">
      <div class="header-user-con">
        <!-- 用户头像 -->
        <el-avatar class="user-avator" :size="30" :src="imgurl"/>
        <!-- 用户名下拉菜单 -->
        <el-dropdown class="user-name" trigger="click" @command="handleCommand">
					<span class="el-dropdown-link">
						{{ username }}
						<el-icon class="el-icon--right">
							<arrow-down/>
						</el-icon>
					</span>
          <template #dropdown>
            <el-dropdown-menu>
              <a href="https://www.baidu.com" target="_blank">
                <el-dropdown-item>访问百度</el-dropdown-item>
              </a>
              <el-dropdown-item command="user-center">个人中心</el-dropdown-item>
               </el-dropdown-menu>
          </template>
        </el-dropdown>
        <div>
          <el-link type="primary" @click="handleCommand('loginout')" style="margin-left: 20px;">退出登录</el-link>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import {onMounted, provide, ref} from 'vue';
import {useSidebarStore} from '../store/sidebar';
import {useRouter} from 'vue-router';
import imgurl from '../assets/img/admin.png';
import {postRequest} from "../api";
import {ElMessage} from "element-plus";


const selectedColor1 = ref(localStorage.getItem('--primary-color') ? localStorage.getItem('--primary-color') : '#242f42');
const selectedColor2 = ref(localStorage.getItem('--table-th-color') ? localStorage.getItem('--table-th-color') : '#409eff');
const selectedColor3 = ref(localStorage.getItem('--el-color-primary') ? localStorage.getItem('--el-color-primary') : '#409eff');

const username: string | null = localStorage.getItem('ms_username');
const message: number = 0;
const visible = ref(false);
const sidebar = useSidebarStore();

// 侧边栏折叠
const collapseChage = () => {
  sidebar.handleCollapse();
};

const handleSetting = () => {
  visible.value = true;
}

onMounted(() => {
  //从本地localStorage读取color样式，没有就用默认值
  document.documentElement.style.setProperty('--primary-color', localStorage.getItem('--primary-color') ? localStorage.getItem('--primary-color') : '#242f42');
  document.documentElement.style.setProperty('--table-th-color', localStorage.getItem('--table-th-color') ? localStorage.getItem('--table-th-color') : '#409eff');
  document.documentElement.style.setProperty('---el-color-primary', localStorage.getItem('---el-color-primary') ? localStorage.getItem('---el-color-primary') : '#409eff');

  if (document.body.clientWidth < 1500) {
    collapseChage();
  }
});

//修改全局颜色样式并保存在本地localStorage
const handleColorChange1 = () => {
  document.documentElement.style.setProperty('--primary-color', selectedColor1.value);
  localStorage.setItem('--primary-color', selectedColor1.value);
  // 提供值给子组件
  provide('sharedValue', selectedColor1.value)
}

const handleColorChange2 = () => {
  document.documentElement.style.setProperty('--table-th-color', selectedColor2.value);
  localStorage.setItem('--table-th-color', selectedColor2.value);

}

const handleColorChange3 = () => {
  document.documentElement.style.setProperty('--el-color-primary', selectedColor3.value);
  localStorage.setItem('--el-color-primary', selectedColor3.value);

}


// 用户名下拉菜单选择事件
const router = useRouter();
const handleCommand = async (command: string) => {
  if (command == 'loginout') {
    try {
      const response = await postRequest('/logout', {'username': username})
      if (response.data.status) {
        // 请求成功，处理成功逻辑，例如显示通知或跳转页面
        ElMessage.success(response.data.message);
        localStorage.removeItem('token');
        localStorage.removeItem('ms_keys');
        localStorage.removeItem('ms_username');
        router.push('/login');


      } else {
        // 请求失败，处理错误逻辑，例如显示错误信息
        //   console.error('编辑失败', response.data.message);
        ElMessage.error(response.data.message);
      }
    } catch (error) {
      // 处理请求错误
      // console.error('请求出错', error);
      ElMessage.error('请求错误！', error);
    }

  } else if (command == 'user-center') {
    router.push('/user-center');
  }
};
</script>
<style scoped>
.header {
  position: relative;
  box-sizing: border-box;
  width: 100%;
  height: 70px;
  font-size: 22px;
  color: #fff;
  background-color: var(--primary-color); /* 使用变量来控制 */
}

.collapse-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  float: left;
  padding: 0 21px;
  cursor: pointer;
}

.header .logo {
  float: left;
  text-align: center;
  width: 200px;
  line-height: 70px;
}


.text1 {
  color: #606266;
  font-size: 15px;
  padding-right: 30px;
  padding-top: 20px;
}

.titleClass {
  display: flex;
}

.header-right {
  float: right;
  padding-right: 20px;
}


.header-user-con {
  display: flex;
  height: 70px;
  align-items: center;
}

.header-setting {
  float: right;
  display: flex;
  height: 70px;
  padding-right: 20px;
  align-items: center;
}

.btn-fullscreen {
  transform: rotate(45deg);
  margin-right: 5px;
  font-size: 24px;
}

.btn-bell,
.btn-fullscreen {
  position: relative;
  width: 30px;
  height: 30px;
  text-align: center;
  border-radius: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-bell-badge {
  position: absolute;
  right: 4px;
  top: 0px;
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background: #f56c6c;
  color: #fff;
}

.btn-bell .el-icon-lx-notice {
  color: #fff;
}

.user-name {
  margin-left: 10px;
}

.user-avator {
  margin-left: 20px;
}

.el-dropdown-link {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-dropdown-menu__item {
  text-align: center;
}
</style>
