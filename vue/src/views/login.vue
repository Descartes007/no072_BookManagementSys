<template>
  <div class="login-wrap">
    <div class="ms-login">
      <div class="ms-title">图书管理系统</div>
      <el-form :model="param" :rules="rules" ref="login" label-width="0px" class="ms-content">
        <el-form-item prop="username">
          <el-input v-model="param.username" placeholder="请输入用户名">
            <template #prepend>
              <el-button :icon="User"></el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
              type="password"
              placeholder="请输入密码"
              v-model="param.password"
              show-password
              @keyup.enter="submitForm(login)"
          >
            <template #prepend>
              <el-button :icon="Lock"></el-button>
            </template>
          </el-input>
        </el-form-item>
        <div class="login-btn">
          <el-button type="primary" round @click="submitForm(login)" :loading="loading">登录</el-button>
        </div>
        <div class="login-tips-container">
          <el-checkbox class="login-tips" v-model="checked" label="记住密码" size="large"/>
          <el-link type="primary" href="/register" :underline="false">去注册</el-link>
          <el-link type="primary" href="/forget_password" :underline="false">忘记密码？</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive, onMounted} from 'vue';
import {useTagsStore} from '../store/tags';
import {usePermissStore} from '../store/permiss';
import {useRouter} from 'vue-router';
import {ElMessage} from 'element-plus';
import type {FormInstance, FormRules} from 'element-plus';
import {Lock, User} from '@element-plus/icons-vue';
import {postRequest} from '../api/index';
import webServerSrc from "../components/global.vue";
import axios from "axios";
import {checkPassword} from "../utils/validations";


interface LoginInfo {
  username: string;
  password: string;
}

const loading = ref(false);
const lgStr = localStorage.getItem('login-param');
const defParam = lgStr ? JSON.parse(lgStr) : null;
const checked = ref(lgStr ? true : false);
const permiss = ref(usePermissStore());
const router = useRouter();
const param = reactive<LoginInfo>({
  username: defParam ? defParam.username : '',
  password: defParam ? defParam.password : '',
});

const rules: FormRules = {
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: 'blur',
    },
  ],
  password: [{required: true, message: '请输入密码', trigger: 'blur'}],
};

const login = ref<FormInstance>();
const permisson_ids = ref('');
const submitForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return;

  formEl.validate(async (valid: boolean) => {
    if (valid) {

      loading.value = true;
      try {
        //const encryptedPassword = md5(param.password);
        const response = await axios.post(webServerSrc.webServerSrc + '/login', {
          username: param.username,
          password: param.password,
        });
        if (response.data.status) {
          // 请求成功，处理成功逻辑，例如显示通知或跳转页面
          ElMessage.success(response.data.message);
          permisson_ids.value = response.data.permisson;
          // 把返回的token存储在本地
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('refresh_token', response.data.refresh_token);
        } else {
          // 请求失败，处理错误逻辑，例如显示错误信息
          ElMessage.error(response.data.message);
          return
        }
      } catch (error) {
        // 处理请求错误
        console.error('请求出错,错误原因是', error);
        ElMessage.error('后端服务错误');
        return
      } finally {
        loading.value = false;
      }

      localStorage.setItem('ms_username', param.username);
      const keys = permiss.value.defaultList[param.username];
      permiss.value.handleSet(keys);
      localStorage.setItem('ms_keys', JSON.stringify(keys));
      router.push('/index');
      if (checked.value) {
        localStorage.setItem('login-param', JSON.stringify(param));
      } else {
        localStorage.removeItem('login-param');
      }
    } else {
      // 检查用户名和密码是否为空
      if (!param.username.trim() || !param.password.trim()) {
        ElMessage.error('用户名或密码不能为空');
        return;
      }
    }
  })
};


//获取所有用户的权限列表
onMounted(async () => {
  await permiss.value.initDefaultList();
});


const tags = useTagsStore();
tags.clearTags();
</script>

<style scoped>
.login-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-image: url(../assets/img/background.jpg);
  background-size: cover;
  background-repeat: no-repeat;
}

.ms-title {
  line-height: 50px;
  text-align: center;
  font-size: 20px;
  color: #333;
  font-weight: bold;
  padding-top: 10px;
  padding-bottom: 10px;
}

.ms-login {
  width: 400px;
  height: 350px;
  border: 10px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.8);
    /* 使用backdrop-filter创建模糊效果，模拟玻璃质感。
     blur()用于设置模糊程度，这里设置为5px作为示例。
     可以根据需要调整其它滤镜效果，如brightness(), contrast(), etc.*/
  backdrop-filter: blur(10px);

  /* 设置元素的边框阴影，增强立体感 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.ms-content {
  padding: 10px 30px 30px;
}

.login-btn {
  text-align: center;
}

.login-btn button {
  width: 100%;
  height: 45px;
  margin-bottom: 30px;
}

.login-tips-container {
  display: flex;
  align-items: center; /* 使子元素垂直居中对齐 */
  gap: 50px; /* 在子元素之间创建100px间距 */
  /* 如果需要确保整个容器是水平方向上的，则可以添加以下属性： */
  flex-direction: row; /* 默认值，一般情况下不需要写这个 */
}

.login-tips {
  font-size: 12px;
  line-height: 30px;
  color: #333;
}

.el-input {
  height: 45px;
  margin-bottom: 10px;
}

.el-link .el-icon--right.el-icon {
  margin-top: 1px;
}
</style>
