<template>
  <div class="sidebar">
    <el-popover placement="right" width="200" trigger="hover">
      <div class="user-info-popover">
        <el-avatar :src="userInfo.avatar" size="large"></el-avatar>
        <div class="user-info">
          <h3>{{ userInfo.name }}</h3>
          <p>{{ userInfo.signature }}</p>
        </div>
      </div>
      <el-avatar slot="reference" :src="userInfo.avatar" class="avatar" size="large"></el-avatar>
    </el-popover>
    <el-dropdown @command="handleStatusChange">
      <span class="el-dropdown-link">
        {{ isOnline ? 'Online' : 'Offline' }}
        <i class="el-icon-arrow-down"></i>
      </span>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item command="online">Online</el-dropdown-item>
        <el-dropdown-item command="offline">Offline</el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
    <!-- ...其他元素... -->
    <el-menu class="menu" default-active="1" @select="$emit('select', $event)">
      <el-menu-item index="1"><i class="el-icon-message"></i> message</el-menu-item>
      <el-menu-item index="2"><i class="el-icon-s-custom"></i> list</el-menu-item>
      <el-menu-item index="3"><i class="el-icon-setting"></i> setup</el-menu-item>
      <el-menu-item index="5"><i class="el-icon-plus"></i> add</el-menu-item>
    </el-menu>
    <el-button type="danger" round @click="$emit('select', '4')">log off</el-button>
  </div>
</template>

<script>
export default {
  name: "Sidebar",
  data() {
    return {
      userInfo: {
        avatar: 'https://tupian.qqw21.com/article/UploadPic/2020-2/20202312212244618.jpg',
        name: 'Vue Ninja',
        signature: 'Coding with heart.',
      },
      isOnline: true,
    };
  },

  methods: {
    handleStatusChange(command) {
      this.isOnline = command === 'online';
    },
  },
}
</script>

<style scoped>
.sidebar {
  flex: 0 0 150px;
  border-right: 2px solid #f0f2f5;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  background-color: #fff;
}

.avatar {
  margin-bottom: 30px;
}

.menu {
  width: 100%;
  font-size: 16px;
}

.el-button.is-round {
  border-radius: 20px;
  padding: 12px 23px;
  position: fixed;
  bottom: 20px;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-info-popover {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-info h3 {
  margin: 10px 0 5px 0;
  font-size: 14px;
  font-weight: bold;
}

.user-info p {
  font-size: 12px;
  color: #666;
  text-align: center;
}

</style>