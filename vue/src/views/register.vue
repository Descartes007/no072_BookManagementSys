<template>
  <div class="login-wrap">
    <div class="ms-login">
      <div class="ms-title">用户注册</div>
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
        <el-form-item prop="email">
          <el-input v-model="param.email" placeholder="请输入邮箱地址">
            <template #prepend>
              <el-button :icon="Iphone"></el-button>
            </template>
          </el-input>
        </el-form-item>
        <div class="login-btn">
          <el-button type="primary" round @click="submitForm(login)">注册</el-button>
        </div>
        <div class="login-tips-container">
          <el-link type="primary" href="/login" :underline="false">返回登录</el-link>
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
import {Lock, User, Iphone} from '@element-plus/icons-vue';
import {postRequest} from '../api/index';
import { isRequired, checkEmail ,checkPassword} from '../utils/validations';

interface LoginInfo {
  username: string;
  password: string;
  email: string;
}

const lgStr = localStorage.getItem('login-param');
const defParam = lgStr ? JSON.parse(lgStr) : null;
const checked = ref(lgStr ? true : false);
const permiss = ref(usePermissStore());
const router = useRouter();
const param = reactive<LoginInfo>({
  username: defParam ? defParam.username : '',
  password: defParam ? defParam.password : '',
  email: defParam ? defParam.password : '',
});

const rules: FormRules = {
  username: [{required: true, message: '请输入用户名', trigger: 'blur'}],
  password: [{required: true, message: '请输入密码', trigger: 'blur'},{ validator: checkPassword, trigger: 'blur' },],
  email: [{required: true, message: '请输入邮箱地址', trigger: 'blur'},{ validator: checkEmail, trigger: 'blur' },],
};

const login = ref<FormInstance>();

const submitForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.validate(async (valid: boolean) => {
    if (valid) {
      try {
        //const encryptedPassword = md5(param.password);
        const response = await postRequest('/register', {
          username: param.username,
          password: param.password,
          email: param.email,
        });
        if (response.data.status) {
          // 请求成功，处理成功逻辑，例如显示通知或跳转页面
          ElMessage.success(response.data.message);
        } else {
          // 请求失败，处理错误逻辑，例如显示错误信息
          ElMessage.error(response.data.message);
          return
        }
      } catch (error) {
        // 处理请求错误
        console.error('请求出错,错误原因是', error);
        ElMessage.error('请求错误！');
        return
      }

      router.push('/login');

    } else {
      ElMessage.error('注册失败');
      return
    }
  });
};




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
  background-size: 100%;
}

.ms-title {
  line-height: 50px;
  text-align: center;
  font-size: 20px;
  color: #333;
  font-weight: bold;
  padding-top: 10px;
}

.ms-login {
  width: 500px;
  height: 400px;
  border: 10px;
  border-radius: 10px;
  background: #fff;
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
  gap: 100px; /* 在子元素之间创建100px间距 */
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
