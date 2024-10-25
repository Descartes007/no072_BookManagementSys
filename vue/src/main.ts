import {createApp, ref} from 'vue';
import {createPinia} from 'pinia';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import App from './App.vue';
import router from './router';
import {usePermissStore} from './store/permiss';
import 'element-plus/dist/index.css';
import './assets/css/icon.css';
import webServerSrc from './components/global.vue';
import axios from 'axios';
import * as echarts from 'echarts';

import {useCookies} from '@vueuse/integrations/useCookies';
import {initGlobalAxios} from "./api";
import {ElMessage} from "element-plus";

const cookies = useCookies();


// 创建axios实例并配置请求拦截器用于在请求头中加上token字段
const $axios = axios.create({
    baseURL: webServerSrc.webServerSrc,
    withCredentials: true,
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    }
});
$axios.interceptors.request.use(
    (config) => {
        //从localStorage或者任何其他存储机制中（例如cookie中）获取token
        const token = localStorage.getItem('token');
        const refreshToken = localStorage.getItem('refresh_token');
        if (token) {
            config.headers['X-Access-Token'] = `${token}`;
        }
        if (refreshToken) {
            config.headers['Refresh-Token'] = `${refreshToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);


// 响应拦截器
$axios.interceptors.response.use(
    // 处理成功响应
    response => {
        // 如果状态码是200，直接返回响应对象
        if (response.status === 200 && response.data.token) {
            localStorage.setItem('token', response.data.token);
            return response;
        }
        if (response.status === 200 && !response.data.token) {
            return response;
        }
    },
    async error => {
        const {status, data} = error.response;
        if (status === 401) {
            // // 对于401 Unauthorized，这里的逻辑是先判断是token过期还是refresh token过期
            // 如果是token过期就用refresh token重新请求一次更新token，获取失败则清除用户信息并重定向到登录页
            // 如果是refresh token过期就清除用户信息并重定向到登录页
            // token过期
            if (data.flag === 'token') {
                const token = localStorage.getItem('token');
                const refreshToken = localStorage.getItem('refresh_token');
                try {
                    // 发送刷新token请求
                    const refreshResponse = await $axios.post('/token/refresh', {refreshToken: refreshToken});
                    if (refreshResponse.data.Token) {// 更新tokens
                        localStorage.setItem('token', refreshResponse.data.token);
                        // 重新发起被拒绝的请求
                        const originalRequest = error.config;
                        originalRequest.headers['X-Access-Token'] = `${token}`;
                        return await $axios(originalRequest);
                    } else {
                        ElMessage.error(refreshResponse.data.message);
                        router.push('/login');
                    }

                } catch (refreshError) {
                    // 刷新token失败，清空tokens并跳转到登录页面
                    localStorage.removeItem('token');
                    localStorage.removeItem('refreshToken');
                    router.push('/login');
                }
            } else if (data.flag === 'refresh token') {
                localStorage.removeItem('token');
                localStorage.removeItem('refreshToken');
                ElMessage.error(error.response.data);
                router.push('/login');
            }
            // 其他错误情况，继续抛出错误给调用方
            return Promise.reject(error);
        }
    }
)
;


// 创建并挂载根实例
const app = createApp(App);
// vue3 给原型上挂载属性
app.config.globalProperties.$echarts = echarts;
// app.config.globalProperties.$cookies = cookies;
// 将axios设置为全局属性$http
app.config.globalProperties.$axios = $axios;
initGlobalAxios(app.config.globalProperties.$axios);
// 设置全局的 axios 默认配置
axios.defaults.withCredentials = true;    //为true表示允许跨域携带cookies,保持session的一致性
axios.defaults.baseURL = webServerSrc.webServerSrc; // 设置基础 URL
axios.defaults.timeout = 5000; // 设置默认请求超时时间
// axios.defaults.headers.common['Authorization'] = 'Bearer your-token-here'; // 设置默认的请求头，例如授权信息
axios.defaults.headers.post['Content-Type'] = 'application/json'; // 设置 POST 请求的 Content-Type

app.use(createPinia());
// 整个应用支持路由
app.use(router);

// 从 @element-plus/icons-vue 中导入所有图标并进行全局注册。
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}
// 自定义权限指令
const permiss = usePermissStore();
app.directive('permiss', {
    mounted(el, binding) {
        if (!permiss.key.includes(String(binding.value))) {
            el['hidden'] = true;
        }
    },
});

app.mount('#app');
