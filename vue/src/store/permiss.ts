import {defineStore} from 'pinia';
import {postRequest} from "../api";
import {ref} from "vue";
import axios from "axios";

interface ObjectList {
    [key: string]: string[];
}


//从后端获取每个用户名对应的permission权限列表
async function fetchData(): Promise<ObjectList> {
    const result: ObjectList = {};
    try {
        const response = await axios.post('/user/permission/query', {});
        // 将后端返回的数据转换为ObjectList格式
        response.data.infos.forEach((info) => {
            result[info.name] = info.permissions.split(',');
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
    return result;
};


//在Vue 3中，defineStore用于创建一个Vuex store。在usePermissStore的state函数中，不能直接使用异步函数fetchData的返回值，因为state函数必须是同步的
export const usePermissStore = defineStore('permiss', {
    state: () => {
        {
            const keys = localStorage.getItem('ms_keys');
            return {
                key: keys ? JSON.parse(keys) : <string[]>[],
                defaultList: ref<ObjectList>({}), // 初始化为空的对象  ,
                // defaultList: <ObjectList>{
                //     admin: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25'],
                //     user: ['1', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25']
                // }
            };
        }
    },

    actions: {
        async initDefaultList() {
            this.defaultList = await fetchData();
        },
        handleSet(val: string[]) {
            this.key = val;
        }
    }
});

