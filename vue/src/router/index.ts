import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router';
import {usePermissStore} from '../store/permiss';
import Home from '../views/home.vue';
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import {ElMessage} from "element-plus";

// 定义一些路由
// 每个路由都需要映射到一个组件。
const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/index',
    },
    {
        path: '/register',
        name: 'register', // 可选，为路由命名，方便通过name跳转
        component: () => import('../views/register.vue'),
    },
    {
        path: '/forget_password',
        name: 'forget_password', // 可选，为路由命名，方便通过name跳转
        component: () => import('../views/forget-password.vue'),
    },
    {
        path: '/',
        name: 'Home',
        component: Home,
        children: [
            {
                path: '/index',
                name: 'index',         //name一定要是唯一的，会根据这个name来进行路由。如果出现相同name就会出现访问报错[Vue Router warn]: No match found for location with path "/xx/xx/xxx"
                meta: {
                    title: '用户首页',   //这是点击页面导航栏的模块后，标签页的title,不是左侧导航栏的标题哈
                    permiss: '1',      //权限ID，这里的ID一定要和
                },
                component: () => import(/* webpackChunkName: "dashboard" */ '../views/index.vue'),
            },
            {
                path: '/dashboard',
                name: 'dashboard',         //name一定要是唯一的，会根据这个name来进行路由。如果出现相同name就会出现访问报错[Vue Router warn]: No match found for location with path "/xx/xx/xxx"
                meta: {
                    title: '数据统计',   //这是点击页面导航栏的模块后，标签页的title,不是左侧导航栏的标题哈
                    permiss: '0',      //权限ID，这里的ID一定要和
                },
                component: () => import(/* webpackChunkName: "dashboard" */ '../views/dashboard.vue'),
            },

            {
                path: '/publishing',
                name: 'publishing',
                meta: {
                    title: '出版社管理',
                    permiss: '2',
                },
                component: () => import(/* webpackChunkName: "publish" */ '../views/publish.vue'),
            },
            {
                path: '/author',
                name: 'author',
                meta: {
                    title: '作者管理',
                    permiss: '3',
                },
                component: () => import(/* webpackChunkName: "author" */ '../views/author.vue'),
            },
            {
                path: '/classification',
                name: 'classification',
                meta: {
                    title: '分类管理',
                    permiss: '3',
                },
                component: () => import(/* webpackChunkName: "author" */ '../views/classification.vue'),
            },
            {
                path: '/entry',
                name: 'entry',
                meta: {
                    title: '图书管理',
                    permiss: '4',
                },
                component: () => import(/* webpackChunkName: "book" */ '../views/entry.vue'),
            },
            {
                path: '/book/detail/:bookId',
                name: 'BookDetail',
                props: true,
                meta: {
                    title: '图书详情',
                    permiss: '6',
                },
                component: () => import('../views/book-detail.vue')
            },
            {
                path: '/book',
                name: 'book',
                meta: {
                    title: '图书查询',
                    permiss: '6',
                },
                component: () => import(/* webpackChunkName: "book" */ '../views/book.vue'),
            },
            {
                path: '/borrow',
                name: 'borrow',
                meta: {
                    title: '借阅管理',
                    permiss: '6',
                },
                component: () => import(/* webpackChunkName: "book" */ '../views/borrow.vue'),
            },
            {
                path: '/collection',
                name: 'collection',
                meta: {
                    title: '我的收藏',
                    permiss: '6',
                },
                component: () => import(/* webpackChunkName: "book" */ '../views/my-collection.vue'),
            },
            {
                path: '/role',
                name: 'role',
                meta: {
                    title: '角色管理',
                    permiss: '7',
                },
                component: () => import(/* webpackChunkName: "role" */ '../views/role.vue'),
            },
            {
                path: '/user',
                name: 'user',
                meta: {
                    title: '用户管理',
                    permiss: '8',
                },
                component: () => import(/* webpackChunkName: "user" */ '../views/user.vue'),
            },
            {
                path: '/audit',
                name: 'audit',
                meta: {
                    title: '审计管理',
                    permiss: '9',
                },
                component: () => import(/* webpackChunkName: "user" */ '../views/audit.vue'),
            },
            {
                path: '/user-center',
                name: 'user-center',
                meta: {
                    title: '个人中心',
                },
                component: () => import(/* webpackChunkName: "user" */ '../views/user-center.vue'),
            },
            {
                path: '/notice',
                name: 'notice',
                meta: {
                    title: '公告配置',
                },
                component: () => import(/* webpackChunkName: "user" */ '../views/notice.vue'),
            },
            {
                path: '/donate',
                name: 'donate',
                meta: {
                    title: '联系作者',
                    permiss: '11',
                },
                component: () => import(/* webpackChunkName: "donate" */ '../views/donate.vue'),
            }
        ],
    },
    {
        path: '/login',
        name: 'Login',
        meta: {
            title: '登录',
        },
        component: () => import(/* webpackChunkName: "login" */ '../views/login.vue'),
    },
    {
        path: '/403',
        name: '403',
        meta: {
            title: '没有权限',
        },
        component: () => import(/* webpackChunkName: "403" */ '../views/403.vue'),
    },
    {
        path: '/:pathMatch(.*)*',   //是一个特殊的路由配置，它可以用于捕获任意路径并进行路由重定向，:pathMatch(.*)*是一个动态片段，它使用了路由参数（以冒号:开头），其中pathMatch是参数的名称，而(.*)*是参数的正则表达式模式，所以,/:pathMatch(.*)* 可以匹配任意路径,包括根路径和子路径。
        name: '404',
        meta: {
            title: '页面不存在',
        },
        component: () => import(/* webpackChunkName: "404" */ '../views/404.vue'),
    },
];

//创建路由实例并传递 `routes` 配置
const router = createRouter({
    history: createWebHistory(),
    routes, //routes: routes的简写
});


// 注册一个全局前置路由守卫查看用户是否有权限，第三个参数next是可选项，如果使用了next这个参数，则必须要使用next()
router.beforeEach((to, from, next) => {
    NProgress.start();
    const role = localStorage.getItem('ms_username');
    const token = localStorage.getItem('token');
    const permiss = usePermissStore();
    if (!role && !token && (to.path !== '/login' && to.path !== '/forget_password' && to.path !== '/register')) {
        next('/login');
    } else if (to.meta.permiss && !permiss.key.includes(to.meta.permiss)) {
        // 如果没有权限，则进入403
        next('/403');
    } else if (role && token && to.path == '/login') {             //防止重复登陆
        ElMessage.warning("请勿重复登陆");
        return next({path: from.path ? from.path : '/index'});
    } else {
        next();
    }
});

router.afterEach(() => {
    NProgress.done()
})

export default router;
