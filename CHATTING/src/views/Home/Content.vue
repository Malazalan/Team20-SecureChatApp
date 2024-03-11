<template>
  <div class="content">

    <div class="search-bar">
      <el-input v-model="searchQuery" placeholder="Search for friends/messages" prefix-icon="el-icon-search" clearable>
      </el-input>
    </div>

    <!-- 消息列表 -->
    <div v-if="currentView === 'messages'" class="message-container">
      <el-card class="box-card" v-for="message in filteredItems" :key="message.id"
        :class="{ 'is-selected': message.id === selectedItemId }">
        <div class="item-content" @click="itemClicked(message)">
          <el-avatar :src="message.receiverAvatar" size="small"></el-avatar>
          <div class="text-info">
            <div class="item-name">{{ message.receiverName }}</div>
            <div class="item-message">{{ message.content }}</div>
          </div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </el-card>
    </div>

    <!-- 好友列表 -->
    <div v-if="currentView === 'list'" class="message-container">
      <el-card class="box-card" v-for="friend in filteredFriends" :key="friend.id"
        :class="{ 'is-selected': friend.id === selectedItemId }">
        <div class="item-content" @click="itemClicked(friend)">
          <el-avatar :src="friend.receiverAvatar" size="small"></el-avatar>
          <div class="text-info">
            <div class="item-name">{{ friend.receiverName }}</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "Content",
  props: {
    currentView: String,
  },

  data() {
    return {
      messages: [],
      friends: [],
      selectedItemId: null,
      searchQuery: '',
    };
  },

  async created() {
    await this.fetchData();
  },
  mounted() {
    this.$router.push({ name: 'index', params: { value: this.selectedItemId } });

  },

  computed: {
    // 根据搜索框的内容过滤消息列表
    filteredItems() {
      if (!this.searchQuery) {
        return this.messages;
      }
      return this.messages.filter(message =>
        (message.senderName?.toLowerCase().includes(this.searchQuery) || false) ||
        (message.content?.toLowerCase().includes(this.searchQuery) || false)
      );
    },

    // 根据搜索框的内容过滤好友列表
    filteredFriends() {
      if (!this.searchQuery) {
        return this.friends;
      }
      return this.friends.filter(friend => friend.receiverName.toLowerCase().includes(this.searchQuery));
    },
  },

  methods: {
    async fetchData() {
      try {
        const usersResponse = await axios.get('http://localhost:3000/users');
        const messagesResponse = await axios.get('http://localhost:3000/messages');
        this.friends = usersResponse.data;
        this.messages = messagesResponse.data
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },

    itemClicked(item) {
      this.selectedItemId = item.id;
      this.$emit('chatSelected', item);
    },
  },
};
</script>

<style scoped>
.search-bar {
  margin-bottom: 10px;
}

.is-selected {
  background: linear-gradient(145deg, #bae7ff, #91d5ff) !important;
}

.message-time {
  margin-left: auto;
  color: #999;
  font-size: 12px;
}

.content {
  width: 250px;
  overflow-y: auto;
  padding: 10px;
}

::v-deep .el-card__body,
.el-main {
  padding: 10px;
  width: 100%;
}

.box-card {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  background: linear-gradient(145deg, #e6f7ff, #bae7ff);
  border-radius: 8px;
}

.box-card:hover {
  background: linear-gradient(145deg, #bae7ff, #91d5ff);
}

.item-content {
  display: flex;
  align-items: center;
}

.text-info {
  margin-left: 10px;
}

.item-name {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 5px;
}

.item-message {
  color: #666;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100px;
}
</style>
