<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
    <el-form-item label="角色名称" prop="name">
      <el-input v-model="form.name" :disabled="edit_type"></el-input>
    </el-form-item>
    <div class="mgb20 tree-wrapper" v-if="edit_type">
      <el-tree
          ref="tree"
          :data="data"
          node-key="id"
          default-expand-all
          show-checkbox
          :default-checked-keys="checkedKeys"
      />
    </div>
    <el-form-item>
      <el-button type="primary" @click="saveEdit(formRef,edit_type)">保 存</el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import {ElMessage, ElTree, FormInstance, FormRules, UploadProps} from 'element-plus';
import {ref, onMounted, nextTick} from 'vue';
import {useRoute} from "vue-router";
import {postRequest} from "../api";
import moment from "moment";
import {usePermissStore} from "../store/permiss";


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
  name: '',
  permission_ids: []
};

// 后端返回数据转换为的角色选项列表
const roleOptions = ref([]);
const role = ref<string>('admin');

interface Tree {
  id: string;
  label: string;
  children?: Tree[];
}

const form = ref({...(props.edit ? props.data : defaultData)});
const edit_type = ref(props.edit ? true : false);
const rules: FormRules = {
  name: [{required: true, message: '名称不能为空', trigger: 'blur'}]
};
const formRef = ref<FormInstance>();


//定义权限的代号以及对应的试图，这里的id需要和sidebar.vue里的权限permiss对应上
const data: Tree[] = [
  {
    id: '0',
    label: '数据大屏'
  },
  {
    id: '1',
    label: '系统首页'
  },
  {
    id: '2',
    label: '出版社管理',
    children: [
      {
        id: '11',
        label: '新增'
      },
      {
        id: '12',
        label: '编辑'
      },
      {
        id: '13',
        label: '删除'
      }
    ]
  },
  {
    id: '3',
    label: '作者管理',
    children: [
      {
        id: '14',
        label: '新增'
      },
      {
        id: '15',
        label: '编辑'
      },
      {
        id: '16',
        label: '删除'
      }
    ]
  },
  {
    id: '4',
    label: '图书管理',
    children: [
      {
        id: '17',
        label: '新增'
      },
      {
        id: '18',
        label: '编辑'
      },
      {
        id: '19',
        label: '删除'
      },
      {
        id: '20',
        label: '导出EXCEL'
      },
      {
        id: '21',
        label: '批量删除'
      }]
  },
  {
    id: '5',
    label: '图书借阅',
    children: [{
      id: '6',
      label: '图书查询'
    }, {
      id: '6',
      label: '借阅管理'
    },
    ]
  },
  {
    id: '7',
    label: '角色管理'
  },
  {
    id: '8',
    label: '用户管理'
  },
  {
    id: '9',
    label: '审计管理'
  }
  ,{
    id: '10',
    label: '公告管理'
  },
  {
    id: '11',
    label: '联系作者'
  }
];

const permiss = usePermissStore();

// 获取当前权限
const checkedKeys = ref<string[]>([]);
const getPremission = async () => {
  // 从后端请求接口返回权限列表
  const response = await postRequest('/role/query', {'id': form.value.id});
  checkedKeys.value = response.data.infos[0].permission_ids;
  // 这是从本地文件中根据角色获取权限列表
  // checkedKeys.value = permiss.defaultList[role.value];
  //checkedKeys.value = ['1','2','3','4']
};
getPremission();

// 保存权限
const tree = ref<InstanceType<typeof ElTree>>();


//编辑条目后点击保存的逻辑
const saveEdit = (formEl: FormInstance | undefined, op: Boolean) => {
  // 获取选中的权限
  if (!formEl) return;
  formEl.validate(async valid => {
    if (!valid) return false;
    const url = ref('');
    const data = ref({});
    if (op) {
      url.value = '/update';
      data.value = {
        id: form.value.id,
        permission_ids: tree.value!.getCheckedKeys(false)

      };
    } else {
      url.value = '/add';
      data.value = {
        'name': form.value.name
      }
    }
    ;
    try {
      // 发起 HTTP 请求
      const response = await postRequest(route.fullPath + url.value, data.value);
      if (response.data.status) {
        // props.update(form.value);
        if (op) {
          props.update({
            'id': response.data.id ? response.data.id : form.value.id,
            'name': form.value.name,
            'permission_ids': tree.value!.getCheckedKeys(false)
          })
        } else {
          props.update({
            'id': response.data.id ? response.data.id : form.value.id,
            'name': form.value.name,
          })
        }

        ElMessage.success(response.data.message);
      } else {
        ElMessage.error(response.data.message);
      }
    } catch (error) {
      ElMessage.error('请求错误！', error);
      return
    }
  });
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
