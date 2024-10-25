<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
    <el-form-item label="用户名" prop="name">
      <!--      readonly不可编辑但可见，disabled不可编辑且灰显-->
      <el-input v-model="form.name" :disabled="edit_type"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password">
      <el-input v-model="form.password"></el-input>
    </el-form-item>
    <el-form-item label="邮箱" prop="email">
      <el-input v-model="form.email"></el-input>
    </el-form-item>
    <el-form-item label="角色" prop="role">
      <el-select v-model="form.role_id"  placeholder="请选择">
        <el-option v-for="(item, index) in roles" :key="index" :value="item.id"
                   :label="item.name"></el-option>
      </el-select>
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input v-model="form.description"></el-input>
    </el-form-item>


    <!--    <el-form-item label="是否启用" prop="status">-->
    <!--      <el-switch-->
    <!--          v-model="form.status"-->
    <!--          :active-value="1"-->
    <!--          :inactive-value="0"-->
    <!--          active-text="启用"-->
    <!--          inactive-text="禁用"-->
    <!--      ></el-switch>-->
    <!--    </el-form-item>-->
    <!--    <el-form-item label="开始日期" prop="create_time">-->
    <!--      <el-date-picker type="date" v-model="form.create_time" value-format="YYYY-MM-DD HH:mm:ss"></el-date-picker>-->
    <!--    </el-form-item>-->
    <!--    <el-form-item label="上传头像" prop="thumb">-->
    <!--      <el-upload-->
    <!--          class="avatar-uploader"-->
    <!--          action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"-->
    <!--          :show-file-list="false"-->
    <!--          :on-success="handleAvatarSuccess"-->
    <!--          :before-upload="beforeAvatarUpload"-->
    <!--      >-->
    <!--        <img v-if="form.thumb" :src="form.thumb" class="avatar"/>-->
    <!--        <el-icon v-else class="avatar-uploader-icon">-->
    <!--          <Plus/>-->
    <!--        </el-icon>-->
    <!--      </el-upload>-->
    <!--    </el-form-item>-->
    <el-form-item>
      <el-button type="primary" @click="saveEdit(formRef,edit_type)">保 存</el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import {ElMessage, FormInstance, FormRules, UploadProps} from 'element-plus';
import {ref, reactive, onMounted, onBeforeUnmount} from 'vue';
import {useRoute} from "vue-router";
import {useRouter} from 'vue-router';
import {postRequest} from "../api";
import moment from "moment";
import {checkEmail, checkPassword} from "../utils/validations";


const route = useRoute();
const router = useRouter();
const roles = ref([]);
const props = defineProps({
  data: {
    type: Object,  //type接受的数据类型
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
  name: '',
  password: '',
  email: '',
  role_id: '',
  description:'',
  register_time: new Date(),
  last_login_time: new Date()
};

const form = ref({...(props.edit ? props.data : defaultData)});
const edit_type = ref(props.edit ? true : false);

//在 Vue3 中，特别是在涉及表单验证的场景中，trigger 通常指的是表单验证的触发时机或条件。在一些第三方 UI 库如 Element Plus、Vant 等的表单组件（如 el-form、van-form 等）中，trigger 属性用于定义表单域（如 el-form-item、van-field 等）中验证规则的触发时机，比如：
//'blur'：在表单字段失去焦点时触发验证。
//'change'：在表单字段值发生改变时触发验证。
//'input'：在表单字段每次输入时都触发验证（实时验证）。
//'manual'：手动触发验证，通常配合自定义验证方法使用，需要开发者自己调用 validate 方法进行验证
const rules: FormRules = {
  name: [{required: true, message: '用户名不能为空', trigger: 'blur'}],
  password: [{required: true, message: '密码不能为空', trigger: 'blur'},{ validator: checkPassword, trigger: 'blur' },],
  email: [{required: true, message: '邮箱不能为空', trigger: 'blur'},{ validator: checkEmail, trigger: 'blur' },]
};
const formRef = ref<FormInstance>();

function findRoleName(roleId:number){
  return roles.value.find(role => role.id === roleId)?.name || '未知';
}

//onMounted 钩子函数在组件挂载后发起 AJAX 请求。这是一个生命周期钩子，会在组件 DOM 渲染完成后执行
onMounted(async () => {
  try {
    const response1 = await postRequest('/role/query', {});
    if (response1.data.status) {
      roles.value = response1.data.infos.map(item => ({id:item.id, name: item.name}));
    } else {
      console.log(response1.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }
})





//编辑条目后点击保存的逻辑
const saveEdit = (formEl: FormInstance | undefined, op: Boolean) => {
  //表单验证
  if (!formEl) return;
  formEl.validate(async valid => {
    if (!valid) return false;
    const url = ref('');
    const data = ref({});
    if (op) {
      url.value = '/update';
      data.value = {
        'id': form.value.id,
        'name': form.value.name,
        'password': form.value.password,
        'email': form.value.email,
        'role_id': form.value.role_id,
        'description': form.value.description
      };
    } else {
      url.value = '/add';
      data.value = {
        'name': form.value.name,
        'password': form.value.password,
        'email': form.value.email,
        'role_id': form.value.role_id,
        'register_time':new Date(),
        'description': form.value.description
      }
    }
    ;
    try {
      const response = await postRequest(route.fullPath + url.value, data.value);
      if (response.data.status) {
        const userRoleName = roles.value.find(i => i.id === form.value.role)?.name;
        //props.update(form.value);
        // 更新表格数据
        props.update({
          'id': response.data.id ? response.data.id:form.value.id,
          'name': form.value.name,
          'email': form.value.email,
          'role_id': form.value.role_id,
          'register_time': form.value.register_time,
          'last_login_time': form.value.last_login_time,
          'description': form.value.description,
        });
        ElMessage.success(response.data.message);

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
