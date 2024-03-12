<template>
  <div class="sidebar">
    <el-avatar src="https://tupian.qqw21.com/article/UploadPic/2020-2/20202312212244618.jpg" class="avatar" size="large"
      icon="el-icon-user"></el-avatar>
    <div class="online-status">
      <span class="online-dot"></span>online
    </div>
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

.online-status {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  color: #4CAF50;
  font-size: 14px;
}

.online-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #4CAF50;
  margin-right: 5px;
}
</style>