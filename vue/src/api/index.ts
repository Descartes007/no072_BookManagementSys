import request from '../utils/request';
import webServerSrc from '../components/global.vue';

import { AxiosInstance } from 'axios';

// 假设可以从Vue应用全局属性中获取axios实例
let axiosInstance: AxiosInstance;

// 初始化axios实例
export function initGlobalAxios(appAxios: AxiosInstance) {
  axiosInstance = appAxios;
}

// 在你的库首次被导入到Vue组件中时，调用initGlobalAxios方法
export function useMyLibInVueComponent(app: any) {
  initGlobalAxios(app.config.globalProperties.$axios);
}
// 定义post请求方法
export const postRequest = (url: string, data: any) => {
  return axiosInstance?.post(webServerSrc.webServerSrc+url, data);
};


// export const postRequest = (url,data) => {
//     return request({
//         // url: 'http://127.0.0.1:8888',
//         url: webServerSrc.webServerSrc+url,
//         data: data,
//         method: 'post',
//         withCredentials: true, //为true表示允许跨域携带cookies
//     });
// };

