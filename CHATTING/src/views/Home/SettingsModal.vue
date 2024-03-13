<template>
  <el-dialog :visible="isVisible" title="Settings" width="50%" @close="close">
    <div class="settings-container">
      <div class="settings-menu">
        <el-menu default-active="1" @select="handleSelect" class="el-menu-vertical-demo">
          <el-menu-item index="1">Personal Center</el-menu-item>
          <el-menu-item index="2">Security Instructions</el-menu-item>
          <el-menu-item index="3">Binding Settings</el-menu-item>
        </el-menu>
      </div>
      <div class="settings-content">
        <div v-if="activeMenuIndex === '1'">
          <el-form label-position="left" label-width="110px">
            <el-form-item label="My Avatar:">
              <el-avatar :src="userInfo.avatar" size="large"></el-avatar>
              <el-button @click="modifyAvatar" type="text">Click to modify avatar</el-button>
            </el-form-item>
            <el-form-item label="Login Account:">
              <span>{{ userInfo.mobile }}</span> <!-- 绑定手机号 -->
              <el-button @click="handleModifyAccount" type="text">Modify</el-button>
            </el-form-item>
            <el-form-item label="Email Address:">
              <span>{{ userInfo.email }}</span> <!-- 绑定邮箱 -->
              <el-button @click="handleModifyEmail" type="text">Modify</el-button>
            </el-form-item>
            <el-form-item label="My Nickname:">
              <el-input v-model="userInfo.nickname"></el-input>
            </el-form-item>
            <el-form-item label="My Gender:">
              <el-radio-group v-model="userInfo.gender">
                <el-radio label="Male">Male</el-radio>
                <el-radio label="Female">Female</el-radio>
                <el-radio label="Secret">Secret</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="My Birthday:">
              <el-date-picker v-model="userInfo.birthday" type="date" placeholder="Select date">
              </el-date-picker>
            </el-form-item>
            <el-form-item label="Personal Signature:">
              <el-input type="textarea" v-model="userInfo.signature"></el-input>
            </el-form-item>
          </el-form>
        </div>

        <div v-else-if="activeMenuIndex === '2'">
          <p>Security settings content</p>
        </div>
        <div v-else-if="activeMenuIndex === '3'">
          <el-form label-position="left" label-width="110px">
            <!-- 绑定手机号 -->
            <el-form-item label="Phone number:">
              <el-input v-model="userInfo.mobile" readonly></el-input>
              <el-button @click="showModifyMobileDialog" type="text">Modify</el-button>
            </el-form-item>

            <!-- 绑定邮箱 -->
            <el-form-item label="Email address:">
              <el-input v-model="userInfo.email" readonly></el-input>
              <el-button @click="showModifyEmailDialog" type="text">Modify</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div slot="footer" class="dialog-footer">
          <el-button @click="saveChanges">Save Changes</el-button>
        </div>
      </div>
    </div>


    <div> <!-- 添加一个根元素包裹所有内容 -->
      <!-- ...你现有的模板代码... -->
      <!-- 修改手机号的对话框 -->
      <el-dialog title="Modify phone number" :visible.sync="showMobileDialog" width="30%">
        <el-input v-model="newMobile" placeholder="Enter new phone number"></el-input>
        <span slot="footer" class="dialog-footer">
            <el-button @click="showMobileDialog = false">Cancel</el-button>
            <el-button type="primary" @click="confirmModifyMobile">Save</el-button>
        </span>
      </el-dialog>

      <!-- 修改邮箱的对话框 -->
      <el-dialog title="Modify email address" :visible.sync="showEmailDialog" width="30%">
        <el-input v-model="newEmail" placeholder="Enter new email address"></el-input>
        <span slot="footer" class="dialog-footer">
            <el-button @click="showEmailDialog = false">Cancel</el-button>
            <el-button type="primary" @click="confirmModifyEmail">Save</el-button>
        </span>
      </el-dialog>
    </div> <!-- 根元素结束 -->

  </el-dialog>
</template>


<script>
import axios from 'axios';

export default {
  name: 'SettingsModal',
  props: {
    isVisible: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      activeMenuIndex: '1',
      userInfo: {
        avatar: '',
        nickname: '',
        gender: '',
        birthday: '',
        signature: '',
      },
      showMobileDialog: false,
      showEmailDialog: false,
      newMobile: '', // 新手机号
      newEmail: '', // 新邮箱
    };


  },

  created() {
    this.fetchUserInfo();
  },

  methods: {
    async fetchUserInfo() {
      try {
        const response = await axios.get('/api/user/info'); // 假设这是你的API端点
        this.userInfo = response.data;
      } catch (error) {
        console.error('Error fetching user info:', error);
      }

      try {
        const response = await axios.get('/api/user/info'); // 假设这是你的API端点
        this.userInfo = {
          ...this.userInfo,
          mobile: response.data.mobile, // 假设后端发送的数据中包含了mobile字段
          email: response.data.email, // 假设后端发送的数据中包含了email字段
          // ...其他可能的用户信息字段
        };
      } catch (error) {
        console.error('Error fetching user info:', error);
      }
    },


    handleSelect(index) {
      this.activeMenuIndex = index;
    },

    close() {
      this.$emit('close');
    },

    saveChanges() {
      this.$emit('close');
    },

    modifyAvatar() {
    },
    handleModifyAccount() {
      this.activeMenuIndex = '3';
    },

    handleModifyEmail() {
      this.activeMenuIndex = '3';
    },
    showModifyMobileDialog() {
      this.newMobile = this.userInfo.mobile; // 使用当前手机号初始化
      this.showMobileDialog = true;
    },

    showModifyEmailDialog() {
      this.newEmail = this.userInfo.email; // 使用当前邮箱初始化
      this.showEmailDialog = true;
    },

    confirmModifyMobile() {
      this.userInfo.mobile = this.newMobile; // 更新手机号
      this.showMobileDialog = false;
    },

    confirmModifyEmail() {
      this.userInfo.email = this.newEmail; // 更新邮箱
      this.showEmailDialog = false;
    },

  },
};
</script>

<style scoped>
.dialog-footer {
  width: 100%;
  text-align: right;
}

.el-button {
  margin-left: 10px;
}

.settings-container {
  display: flex;
  width: 100%;
}

.settings-menu {
  flex: 1;
  border-right: 1px solid #efefef;
  padding-right: 20px;
  max-width: 200px;
}

.settings-content {
  flex: 3;
  padding-left: 20px;
}
</style>