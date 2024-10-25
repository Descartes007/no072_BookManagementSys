<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="clearfix">
              <span>基础信息</span>
            </div>
          </template>
          <div class="info">
            <div class="info-image" @click="showDialog">
              <el-avatar :size="100" :src="avatarImg"/>
              <span class="info-edit">
								<i class="el-icon-lx-camerafill"></i>
							</span>
            </div>

            <div class="info-name">{{ name }}</div>
            <div class="info-desc">{{ form.desc }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="clearfix">
              <span>账户编辑</span>
            </div>
          </template>
          <el-form label-width="90px">
            <el-form-item label="用户名："> {{ name }}</el-form-item>
            <el-form-item label="旧密码：">
              <el-input type="password" v-model="form.old"></el-input>
            </el-form-item>
            <el-form-item label="新密码：">
              <el-input type="password" v-model="form.new"></el-input>
            </el-form-item>
            <el-form-item label="个人简介：">
              <el-input v-model="form.desc"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="onSubmit">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    <el-dialog title="裁剪图片" v-model="dialogVisible" width="600px">
      <vue-cropper
          ref="cropper"
          :src="imgSrc"
          :ready="cropImage"
          :zoom="cropImage"
          :cropmove="cropImage"
          style="width: 100%; height: 400px"
      ></vue-cropper>

      <template #footer>
				<span class="dialog-footer">
					<el-button class="crop-demo-btn" type="primary"
          >选择图片
						<input class="crop-input" type="file" name="image" accept="image/*" @change="setImage(1)"/>
					</el-button>
					<el-button type="primary" @click="saveAvatar">上传并保存</el-button>
				</span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="user">
import {onMounted, reactive, ref} from 'vue';
import VueCropper from 'vue-cropperjs';
import 'cropperjs/dist/cropper.css';
import avatar from '../assets/img/admin.png';
import {ElMessage, FormRules} from 'element-plus';
import {postRequest} from "../api";
import {useRouter} from 'vue-router';

const router = useRouter();
const name = localStorage.getItem('ms_username');
const form = reactive({
  old: '',
  new: '',
  desc: ''
});

onMounted(async () => {
  try {
    const response = await postRequest('/user/query', {name: name})
    if (response.data.status) {
      form.desc = response.data.infos[0].description
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (e) {
    console.log(e);
    ElMessage.error('请求错误');
  }

})

const onSubmit = async () => {
  if (form.old.length < 8) {
    ElMessage.error('旧密码长度必须大于8')
    return
  }
  if (form.new.length < 8) {
    ElMessage.error('新密码长度必须大于8')
    return
  }
  if (form.desc.length > 256) {
    ElMessage.error('个人简介长度不能大于256')
    return
  }
  try {
    // 发起 HTTP 请求
    const response = await postRequest('/user_center/update', {
      name: name,
      oldpwd: form.old,
      newpwd: form.new,
      description: form.desc
    });
    // 处理响应
    if (response.data.status) {
      // 请求成功，处理成功逻辑，例如显示通知或跳转页面
      //   console.log('编辑成功', response.data);
      ElMessage.success(response.data.message);
      localStorage.removeItem('ms_username');
      router.push('/login');
    } else {
      // 请求失败，处理错误逻辑，例如显示错误信息
      //   console.error('编辑失败', response.data.message);
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    // 处理请求错误
    // console.error('请求出错', error);
    ElMessage.error('请求错误！');
  }
};

const avatarImg = ref(avatar);
const imgSrc = ref('');
const cropImg = ref('');
const dialogVisible = ref(false);
const cropper: any = ref();

const showDialog = () => {
  dialogVisible.value = true;
  imgSrc.value = avatarImg.value;
};

const setImage = (e: any) => {
  console.log("aa");
  const file = e.target.files[0];
  if (!file.type.includes('image/')) {
    return;
  }
  const reader = new FileReader();
  reader.onload = (event: any) => {
    dialogVisible.value = true;
    imgSrc.value = event.target.result;
    cropper.value && cropper.value.replace(event.target.result);
  };
  reader.readAsDataURL(file);
};

const cropImage = () => {
  cropImg.value = cropper.value.getCroppedCanvas().toDataURL();
};

const saveAvatar = () => {
  avatarImg.value = cropImg.value;
  dialogVisible.value = false;
};
</script>

<style scoped>
.info {
  text-align: center;
  padding: 35px 0;
}

.info-image {
  position: relative;
  margin: auto;
  width: 100px;
  height: 100px;
  background: #f8f8f8;
  border: 1px solid #eee;
  border-radius: 50px;
  overflow: hidden;
}

.info-edit {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.info-edit i {
  color: #eee;
  font-size: 25px;
}

.info-image:hover .info-edit {
  opacity: 1;
}

.info-name {
  margin: 15px 0 10px;
  font-size: 24px;
  font-weight: 500;
  color: #262626;
}

.crop-demo-btn {
  position: relative;
}

.crop-input {
  position: absolute;
  width: 100px;
  height: 40px;
  left: 0;
  top: 0;
  opacity: 0;
  cursor: pointer;
}
</style>
