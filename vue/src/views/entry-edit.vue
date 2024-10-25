<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
    <el-form-item label="编号" prop="book_id" v-if="edit_type">
      <el-input v-model="form.id" :disabled="edit_type"></el-input>
    </el-form-item>
    <el-form-item label="书  名" prop="name">
      <!--      readonly不可编辑但可见，disabled不可编辑且灰显-->
      <el-input v-model="form.name" :disabled="edit_type"></el-input>
    </el-form-item>
    <!--    <el-form-item label="单选框" prop="sex">-->
    <!--      <el-radio-group v-model="sexValue">-->
    <!--        <el-radio label="男"></el-radio>-->
    <!--        <el-radio label="女"></el-radio>-->
    <!--      </el-radio-group>-->
    <!--    </el-form-item>-->
    <el-form-item label="ISBN编码" prop="isbn_number">
      <el-input v-model="form.isbn_number" :disabled="edit_type"></el-input>
    </el-form-item>
    <el-form-item label="出版社" prop="publishing">
      <el-select v-model="form.publishing" placeholder="请选择">
        <el-option v-for="(item, index) in publishers" :key="index" :value="item.id"
                   :label="item.name"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="书籍作者" prop="author">
      <el-select v-model="form.author" placeholder="请选择">
        <el-option v-for="(item, index) in authors" :key="index" :value="item.id"
                   :label="item.name"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="所属类别" prop="book_type">
      <el-select v-model="form.book_type" placeholder="请选择">
        <el-option v-for="(item, index) in book_types" :key="index" :value="item.id"
                   :label="item.type_name"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="图书价格" prop="book_price">
      <el-input v-model="form.book_price"></el-input>
    </el-form-item>
    <el-form-item label="出版时间" prop="publish_time">
      <el-date-picker type="date" v-model="form.publish_time" value-format="YYYY-MM-DD HH:mm:ss"></el-date-picker>
    </el-form-item>
    <el-form-item label="图书简介" prop="description">
      <el-input type="textarea" v-model="form.description"></el-input>
    </el-form-item>
    <el-upload
        class="upload-demo"
        drag
        :action="uploadUrl"
        :data="form.id"
        :auto-upload="true"
        :headers="uploadHeaders"
        :before-upload="beforeAvatarUpload"
        :on-success="handleAvatarSuccess"
        :on-error="handleAvatarError"
        multiple
        v-if="edit_type"

    >
      <el-icon class="el-icon--upload">
        <upload-filled/>
      </el-icon>
      <div class="el-upload__text">
        拖动书籍照片到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          jpg/png files with a size less than 2MB
        </div>
      </template>
    </el-upload>

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
import webServerSrc from '../components/global.vue';
import {formatDateTime} from '../utils/timehandle';

const uploadUrl = ref(webServerSrc.webServerSrc).value + '/upload';

const route = useRoute();
const router = useRouter();
const publishers = ref([]);
const authors = ref([]);
const book_types = ref([]);
const selectedPublisherName = ref('');
const selectedAuthorName = ref('');
const selectedTypeName=ref('');
const bookPhoto = ref('');
const uploadHeaders = reactive({
  'X-Access-Token': localStorage.getItem('token'),
  'Refresh-Token': localStorage.getItem('refresh_token'),
});
//defineProps用于获取父组件传递的数据，且在组件内部不需要引入defineProps方法可以直接使用
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
  isbn_number: '',
  publishing: '',
  author: '',
  book_type: '',
  book_status: 0,
  book_price: '',
  publish_time: undefined,
  description: '',
  photo: '',
};

const form = ref({...(props.edit ? props.data : defaultData)});
const edit_type = ref(props.edit ? true : false);

//在 Vue3 中，特别是在涉及表单验证的场景中，trigger 通常指的是表单验证的触发时机或条件。在一些第三方 UI 库如 Element Plus、Vant 等的表单组件（如 el-form、van-form 等）中，trigger 属性用于定义表单域（如 el-form-item、van-field 等）中验证规则的触发时机，比如：
//'blur'：在表单字段失去焦点时触发验证。
//'change'：在表单字段值发生改变时触发验证。
//'input'：在表单字段每次输入时都触发验证（实时验证）。
//'manual'：手动触发验证，通常配合自定义验证方法使用，需要开发者自己调用 validate 方法进行验证
const rules: FormRules = {
  name: [{required: true, message: '图书名不能为空', trigger: 'blur'}],
  isbn_number: [{required: true, message: 'ISBN不能为空', trigger: 'blur'}],
  publishing: [{required: true, message: '出版时间不能为空', trigger: 'blur'}],
  book_type: [{required: true, message: '图书类别不能为空', trigger: 'blur'}],
  author: [{required: true, message: '作者不能为空', trigger: 'blur'}],
  book_price: [{required: true, message: '价格不能为空', trigger: 'blur'}],
};
const formRef = ref<FormInstance>();


//onMounted 钩子函数在组件挂载后发起 AJAX 请求。这是一个生命周期钩子，会在组件 DOM 渲染完成后执行
onMounted(async () => {
  try {
    const response1 = await postRequest('/publishing/query', {});
    if (response1.data.status) {
      publishers.value = response1.data.infos;
    } else {
      console.log(response1.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }
  try {
    const response2 = await postRequest('/author/query', {});

    if (response2.data.status) {
      authors.value = response2.data.infos;
    } else {
      console.log(response2.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }
  ;
  try {
    const response3 = await postRequest('/classification/query', {});

    if (response3.data.status) {
      book_types.value = response3.data.infos;
    } else {
      console.log(response3.data);
    }
  } catch (error) {
    console.error('请求出错', error);
  }
  ;
  if (edit_type) {
    form.value.publishing = publishers.value.find(i => i.name === form.value.publishing)?.id;
    form.value.author = authors.value.find(i => i.name === form.value.author)?.id;
  }
  form.value.publish_time = formatDateTime(form.value.publish_time);
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
        'isbn_number': form.value.isbn_number,
        'publishing': form.value.publishing,
        'author': form.value.author,
        'book_type': book_types.value.find(i => i.type_name === form.value.book_type)?.id,
        'book_price': form.value.book_price,
        'status': form.value.book_status,
        'publish_time': form.value.publish_time,
        'photo': bookPhoto.value,
        'description': form.value.description,
      };
    } else {
      url.value = '/add';
      data.value = {
        'name': form.value.name,
        'isbn_number': form.value.isbn_number,
        'publishing': form.value.publishing,
        'author': form.value.author,
        'book_type': form.value.book_type,
        'status': 0,
        'book_price': form.value.book_price,
        'publish_time': form.value.publish_time,
        'description': form.value.description,
      }
    }
    ;
    try {
      const response = await postRequest(route.fullPath + url.value, data.value);
      console.log(form.value.book_status);
      if (response.data.status) {
        //find 方法会遍历数组，对每个元素执行提供的函数，直到找到使得函数返回值为 true 的元素，并返回该元素。如果没找到匹配项，则返回 undefined。这里使用了可选链运算符 (?.) 来避免在未找到匹配项的情况下尝试访问 name 属性导致的错误
        selectedPublisherName.value = publishers.value.find(i => i.id === form.value.publishing)?.name;
        selectedAuthorName.value = authors.value.find(i => i.id === form.value.author)?.name;
        selectedTypeName.value = book_types.value.find(i => i.id === form.value.book_type)?.type_name;
        //props.update(form.value);
        props.update({
          'id': response.data.id ? response.data.id : form.value.id,
          'name': form.value.name,
          'book_status': form.value.book_status,
          'isbn_number': form.value.isbn_number,
          'publishing': selectedPublisherName.value,
          'author': selectedAuthorName.value,
          'book_type': selectedTypeName.value,
          'book_price': form.value.book_price,
          'publish_time': form.value.publish_time,
          'photo': bookPhoto.value ? bookPhoto.value : form.value.photo,
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
  // response 是后端返回的数据
  if (response.status) {
    ElMessage.success(response.message);
    bookPhoto.value = response.path;
    //根据传入的参数创建一个指向该参数对象的URL.这个URL的生命仅存在于它被创建的这个文档里.新的对象URL指向执行的File对象或者是Blob对象.
    form.value.thumb = URL.createObjectURL(uploadFile.raw!);
  } else {
    ElMessage.error(response.message)
  }


};

const handleAvatarError: UploadProps['onError'] = (response, uploadFile) => {
  console.log(response.message);
};

//图片上传前校验
const beforeAvatarUpload: UploadProps['beforeUpload'] = rawFile => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('图片必须是JPG或PNG格式!');
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
