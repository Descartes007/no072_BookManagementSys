<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
    <el-form-item label="出版社名称" prop="name">
      <el-input v-model="form.name"></el-input>
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
  name: ''



};

const form = ref({...(props.edit ? props.data : defaultData)});
const edit_type = ref(props.edit ? true : false);
const rules: FormRules = {
  name: [{required: true, message: '名称不能为空', trigger: 'blur'}]
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
        'name': form.value.name

      };
    } else {
      url.value = '/add';
      data.value = {
        'name': form.value.name
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

//图片上传成功处理
const handleAvatarSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
  form.value.thumb = URL.createObjectURL(uploadFile.raw!);
};

//图片上传前校验
const beforeAvatarUpload: UploadProps['beforeUpload'] = rawFile => {
  if (rawFile.type !== 'image/jpeg') {
    ElMessage.error('图片必须是JPG格式!');
    return false;
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过2MB!');
    return false;
  }
  return true;
};


</script>

<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>
