<template>
  <div class="container">
    <el-row :gutter="100">
      <el-col :span="18">
        <div class="form-box">
          <el-form ref="formRef" :rules="rules" :model="form" label-width="80px">
            <el-form-item label="公告标题" prop="title">
              <el-input v-model="form.title"></el-input>
            </el-form-item>
            <el-form-item label="公告内容" prop="content">
              <el-input type="textarea" rows="20" v-model="form.content"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="onSubmit(formRef)">提交</el-button>
              <el-button @click="onReset(formRef)">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      <el-col :span="6">
        <el-timeline style="max-width: 600px">
          <el-timeline-item
              v-for="(activity, index) in activities.slice(0,10)"
              :key="index"
              type="success"
              color="hex"
              hollow=true
              :timestamp="formatDateTime(activity.release_time)"
          >
            标题: {{ activity.title }}
          </el-timeline-item>
        </el-timeline>
      </el-col>
    </el-row>


  </div>
</template>

<script setup lang="ts" name="baseform">
import {onMounted, reactive, ref} from 'vue';
import {ElMessage} from 'element-plus';
import type {FormInstance, FormRules} from 'element-plus';
import {postRequest} from "../api";
import moment from "moment";
import {formatDateTime} from '../utils/timehandle';

const activities = ref([]);

onMounted(async () => {
  try {
    const response = await postRequest('/notice/query', {})
    activities.value = response.data.infos;
  } catch (e) {
    console.log("网络请求错误", e);
    return;
  }
  ;

});



const rules: FormRules = {
  title: [{required: true, message: '请输入公告标题', trigger: 'blur'}],
  content: [{required: true, message: '请输入公告内容', trigger: 'blur'}],
};
const formRef = ref<FormInstance>();
const form = reactive({
  title: '',
  content: '',
});
// 提交
const onSubmit = (formEl: FormInstance | undefined) => {
  // 表单校验
  if (!formEl) return;
  formEl.validate(async (valid) => {
    if (valid) {
      console.log(form);
      try {
        const response = await postRequest('/notice/add', {title: form.title, content: form.content})
        ElMessage.success('提交成功！');
        formEl.resetFields();
        try {
          const response1 = await postRequest('/notice/query', {})
          activities.value = response1.data.infos;
        } catch (e) {
          console.log("网络请求错误", e);
          return;
        }
        ;
      } catch (e) {
        console.log("网络错误", e);
      }
    } else {
      return false;
    }
  });
};
// 重置
const onReset = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.resetFields();
};
</script>
<style>
.form-box {
  width: 100%;
}
</style>
