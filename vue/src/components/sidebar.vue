<!-- 侧边栏模块 -->
<template>
  <div class="sidebar">
    <el-menu
        class="sidebar-el-menu"
        :default-active="onRoutes"
        :collapse="sidebar.collapse"
        :background-color="sharedValue"
        text-color="#bfcbd9"
        active-text-color="#20a0ff"
        unique-opened
        router
    >
      <template v-for="item in items">
        <template v-if="item.subs">
          <el-sub-menu :index="item.index" :key="item.index" v-permiss="item.permiss">
            <template #title>
              <el-icon>
                <component :is="item.icon"></component>
              </el-icon>
              <span>{{ item.title }}</span>
            </template>
            <template v-for="subItem in item.subs">
              <el-sub-menu
                  v-if="subItem.subs"
                  :index="subItem.index"
                  :key="subItem.index"
                  v-permiss="item.permiss"
              >
                <template #title>{{ subItem.title }}</template>
                <el-menu-item v-for="(threeItem, i) in subItem.subs" :key="i" :index="threeItem.index">
                  {{ threeItem.title }}
                </el-menu-item>
              </el-sub-menu>
              <el-menu-item v-else :index="subItem.index" v-permiss="item.permiss">
                {{ subItem.title }}
              </el-menu-item>
            </template>
          </el-sub-menu>
        </template>
        <template v-else>
          <el-menu-item :index="item.index" :key="item.index" v-permiss="item.permiss">
            <el-icon>
              <component :is="item.icon"></component>
            </el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">

import {computed, inject, onMounted, ref} from 'vue';
import {useSidebarStore} from '../store/sidebar';
import {useRoute} from 'vue-router';
import {DataBoard, Files, HomeFilled, Mic} from "@element-plus/icons-vue/components";


const items = [
  {
    icon: 'HomeFilled',
    index: '/index',
    title: '用户首页',
    permiss: '1',
  },
  {
    icon: 'DataBoard',
    index: '/dashboard',
    title: '数据大屏',            //左侧菜单栏显示的文字
    permiss: '0',   //permiss表示权限编号，用户的权限控制就是基于这个编号来的
  },

  {
    icon: 'OfficeBuilding',
    index: '/publishing',
    title: '出版社管理',
    permiss: '2',
  },
  {
    icon: 'Notebook',
    index: '/author',
    title: '作者管理',
    permiss: '3',
  },
  {
    icon: 'Mic',
    index: '/classification',
    title: '分类管理',
    permiss: '3',
  },
  {
    icon: 'Files',
    index: '/entry',
    title: '图书管理',
    permiss: '4',
  },
  {
    icon: 'School',
    index: '/bookManage',
    title: '图书借阅',
    permiss: '5',
    subs: [
      {
        index: '/book',
        title: '图书查询',
        permiss: 6
      },
      {
        index: '/borrow',
        title: '借阅管理',
        permiss: 6
      },
      {
        index: '/collection',
        title: '我的收藏',
        permiss: 6
      },
    ]
  },
  {
    icon: 'Setting',
    index: '/role',
    title: '角色管理',
    permiss: '7',
  },
  {
    icon: 'User',
    index: '/user',
    title: '用户管理',
    permiss: '8',
  },
  {
    icon: 'Checked',
    index: '/audit',
    title: '审计管理',
    permiss: '9',
  },
  {
    icon: 'Message',
    index: '/notice',
    title: '公告管理',
    permiss: '10',
  },
  {
    icon: 'CoffeeCup',
    index: '/donate',
    title: '联系作者',
    permiss: '11',
  },
];
const globalColor = ref(localStorage.getItem('--primary-color') ? localStorage.getItem('--primary-color') : '#242f42');
const route = useRoute();
const onRoutes = computed(() => {
  return route.path;
});
const sidebar = useSidebarStore();
onMounted(() => {
  // 设置初始值
  document.documentElement.style.setProperty('--primary-color', globalColor.value);

});

const sharedValue = inject('sharedValue', ref('default value')) // 如果父级未提供，使用默认值


</script>

<style scoped>
.sidebar {
  display: block;
  position: absolute;
  left: 0;
  top: 70px;
  bottom: 0;
  overflow-y: scroll;
  background-color: var(--primary-color);

}

.sidebar::-webkit-scrollbar {
  width: 0;
}


.sidebar-el-menu:not(.el-menu--collapse) {
  width: 250px;

}

.sidebar > ul {
  height: 100%;
}
</style>
