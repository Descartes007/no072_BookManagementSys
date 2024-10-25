<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
    <el-form-item label="图书类别名称" prop="name">
      <el-input v-model="form.type_name"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="saveEdit(formRef,edit_type)">保 存</el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import {ElMessage, FormInstance, FormRules, UploadProps} from 'element-plus';
import {ref, reactive, getCurrentInstance} from 'vue';
import {useRoute} from "vue-router";
import {postRequest} from "../api";
import moment from "moment";


const route = useRoute();
const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  edit: {
    type: Boolean,
    required: false
  },
  update: {
    type: Function,
    required: true
  }
});

//定义数据格式
const defaultData = {
  id: 1,
  type_name: ''



};

const form = ref({...(props.edit ? props.data : defaultData)});
const edit_type = ref(props.edit ? true : false);
const rules: FormRules = {
  type_name: [{required: true, message: '类别名称不能为空', trigger: 'blur'}]
};
const formRef = ref<FormInstance>();

//编辑条目后点击保存的逻辑
const saveEdit = (formEl: FormInstance | undefined, op: Boolean) => {
  console.log(op);
  if (!formEl) return;
  formEl.validate(async valid => {
    if (!valid) return false;
    const url = ref('');
    const data = ref({});
    if (op) {
      url.value = '/update';
      data.value = {
        'id': form.value.id,
        'name': form.value.type_name

      };
    } else {
      url.value = '/add';
      data.value = {
        'name': form.value.type_name
      }
    };
    try {
      // 发起 HTTP 请求
      const response = await postRequest(route.fullPath + url.value, data.value);
      // 处理响应
      // console.log(response.data.status)
      if (response.data.status) {
        // 请求成功，处理成功逻辑，例如显示通知或跳转页面
        //  console.log('编辑成功', response.data);
        props.update(form.value);
        ElMessage.success(response.data.message);
        // const response1 = await postRequest(route.fullPath + '/query', {query_string:"",page:1,size:10});
        // props.update(response1.data)
      } else {
        // 请求失败，处理错误逻辑，例如显示错误信息
        //   console.error('编辑失败', response.data.message);
        ElMessage.error(response.data.message);
      }
    } catch (error) {
      // 处理请求错误
      // console.error('请求出错', error);
      ElMessage.error('请求错误！', error);
      return
    }
  });
};


</script>

<style>

</style>
