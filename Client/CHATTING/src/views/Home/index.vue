<template>
    <div class="home-container">
        <Sidebar @select="handleSelect" />

        <Content :currentView="currentView" @chatSelected="selectChat" />
        <div class="chat" v-if="currentChatUser.name">
            <div class="chat-header">
                <el-avatar :src="currentChatUser?.avatar" size="small"></el-avatar>
                <span>{{ currentChatUser?.name }}</span>
            </div>
            <div class="chat-history">
                <div v-for="message in chatHistory" :key="message.id" class="message-item"
                    :class="{ 'sender': message.isSender }">
                    <el-avatar v-if="message.isSender" :src="currentUserAvatar" size="small"
                        class="message-avatar"></el-avatar>
                    <el-avatar v-else :src="currentChatUser?.avatar" size="small" class="message-avatar"></el-avatar>
                    <div v-if="message.type !== 'audio'" class="message-content"
                        :style="{ backgroundColor: message.isSender ? '#f0f0f0' : '' }">
                        {{ message.content }}
                    </div>
                    <audio v-else controls :src="message.content" class="audio-message"></audio>
                </div>
            </div>

            <div class="chat-input">
                <div class="input-buttons">
                    <el-button icon="el-icon-s-ticket" @click="showEmojiPicker = !showEmojiPicker"></el-button>
                    <el-button icon="el-icon-microphone" @click="startRecording"></el-button>
                    <el-button icon="el-icon-upload" @click="stopRecording" v-if="isRecording">"Stop and
                        upload</el-button>
                </div>
                <el-input type="textarea" :autosize="{ minRows: 10, maxRows: 20 }" placeholder="Please enter content"
                    v-model="chatInput" class="chat-textarea" @keyup.enter.native="sendMessage">
                </el-input>
                <div class="send-button">
                    <el-button @click="sendMessage">send</el-button>
                </div>
            </div>
        </div>

        <div v-else class="chat-background-only">
            <img src="../../assets/images/1.png" alt="" srcset="">
        </div>
        <div v-if="showEmojiPicker">
            <Picker @select="addEmoji" />
        </div>

        <SettingsModal :isVisible="isSettingsVisible" @close="handleSettingsModalClose" />
        <FriendSearchDialog :isVisible="isFriendSearchVisible" @update:isVisible="isFriendSearchVisible = $event" />
    </div>
</template>

<script>
import Sidebar from './Sidebar.vue';
import Content from './Content.vue';
import SettingsModal from './SettingsModal.vue';
import FriendSearchDialog from './FriendSearchDialog.vue';
import { Picker } from 'emoji-mart-vue';
import axios from 'axios';
import router from "@/router";

export default {
    name: "Home",
    data() {
        return {
            currentUserAvatar: 'https://tupian.qqw21.com/article/UploadPic/2020-2/20202312212244618.jpg',
            currentChatUser: {
                avatar: '',
                name: ''
            },
            currentView: 'messages',
            selectedChat: null,
            chatInput: '',
            isSettingsVisible: false,
            showEmojiPicker: false,
            chatHistory: [],
            isRecording: false,
            isFriendSearchVisible: false,
        };
    },

    components: {
        Sidebar,
        Content,
        SettingsModal,
        FriendSearchDialog,
        Picker
    },

    methods: {
        async startRecording() {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.audioChunks = [];
                this.mediaRecorder.ondataavailable = event => {
                    this.audioChunks.push(event.data);
                };
                this.mediaRecorder.start();
                this.isRecording = true;
            } else {
                console.error('Audio recording is not supported by your browser.');
            }
        },
        stopRecording() {
            this.mediaRecorder.stop();
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);

                // 构造一个特殊的音频消息对象
                const audioMessage = {
                    id: Date.now(),
                    content: audioUrl, // 使用生成的URL
                    isSender: true,
                    type: 'audio' // 新增一个类型属性来区分消息类型
                };

                // 直接向chatHistory添加新消息
                this.chatHistory.push(audioMessage);
                this.isRecording = false;
            };
        },
        addEmoji(emoji) {
            this.chatInput += emoji.native;
            this.showEmojiPicker = false;
        },

        handleSelect(key, keyPath) {
            switch (key) {
                case "1":
                    this.currentView = 'messages';
                    break;
                case "2":
                    this.currentView = 'list';
                    break;
                case "3":
                    this.isSettingsVisible = true;
                    break;
                case "4":
                    this.$router.push('/login');
                    break;
                case "5":
                    this.isFriendSearchVisible = true;
                    break;
            }
            this.chatHistory = [];
            this.chatInput = '';
            this.selectedChat = null;
            this.currentChatUser = {
                avatar: '',
                name: ''
            }
        },

        handleSettingsModalClose() {
            this.isSettingsVisible = false;
        },

        async selectChat(item) {
            try {
                const response = await axios.get(`http://localhost:3000/ChatHistory/${item.receiverId}`);
                this.chatHistory = response.data.messages;
                this.currentChatUser.avatar = item.receiverAvatar
                this.currentChatUser.name = item.receiverName
            } catch (error) {
                console.error("Error fetching chat history:", error);
            }
            this.chatInput = '';
            this.showEmojiPicker = false;
        },

      sendMessage: function () {
        if (!this.chatInput.trim()) return; // 检查输入是否为空
        //请求后端接口
        //receiverID=selectedItemId
        //senderID= 1
        //message:chatInput
        // 创建要发送的 JSON 数据
        const selectedItemId = this.$route.params.value;
        console.log(selectedItemId);
        const originalMessage = {
          receiverID: 1,
          senderID: 1,
          message: this.chatInput
        };

// 转换为 JSON 字符串
        const originalMessageString = JSON.stringify(originalMessage);
       console.log(originalMessageString);
// 发送 POST 请求
        fetch('http://127.0.0.1:5432/api/encrypt', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: originalMessageString
        })
            .then(response => {
              // 处理响应
              if (response.ok) {
                // 请求成功
                return response.json();
              } else {
                // 请求失败
                throw new Error('Network response was not ok');
              }
            })
            .then(data => {
              // 处理返回的数据
              console.log(data);
            })
            .catch(error => {
              // 处理错误
              console.error('There was a problem with your fetch operation:', error);
            });
        let newMessage = {
          id: Date.now(), // 生成唯一ID
          content: this.chatInput,
          isSender: true // 标记为发送者
        };

        // 直接向chatHistory添加新消息
        this.chatHistory.push(newMessage);

        // 清空输入框
        this.chatInput = '';
      }
    }
}
</script>

<style scoped>
.chat-input {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-top: 20px;
}

.input-buttons {
  align-self: flex-start;
  margin-bottom: 10px;
}

.chat-textarea .el-textarea__inner {
  border-radius: 15px;
  padding: 10px;
}

.send-button {
  position: fixed;
  right: 20px;
  bottom: 30px;
  z-index: 1000;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f2f5;
}

.chat-header span {
  margin-left: 10px;
  font-weight: bold;
}

.chat-history {
  overflow-y: auto;
  flex-grow: 1;
  padding: 10px;
}

.message-item {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 10px;
}

.message-avatar {
  background-color: #f2f2f2;
  margin-right: 10px;
}

.message-item.sender {
  justify-content: flex-end;
}

.message-content {
  background-color: #eef5fd;
  border-radius: 15px;
  padding: 8px 12px;
  max-width: 70%;
  word-break: break-word;
}

.message-item.sender .message-content {
  background-color: #daf5cb;
}

.message-item.sender .message-avatar {
  order: 2;
  margin-left: 10px;
  margin-right: 0;
}

.chat-input {
  display: flex;
  align-items: center;
  margin-top: 20px;
}

.el-input .el-input__inner,
.el-button {
  height: 40px;
  border-radius: 20px;
}

.el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
  color: white;
}

.home-container {
  display: flex;
  height: 100vh;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.content,
.chat {
  background-color: #f9fafc;
  width: 250px;
}

.chat {
  background: linear-gradient(to right, #ffffff, #bdcee9);
  flex: 3;
  border-left: 2px solid #f0f2f5;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.chat-history p {
  margin: 10px 0;
  padding: 8px;
  background-color: #eef5fd;
  border-radius: 4px;
  line-height: 1.5;
}

.chat-input .el-input {
  flex-grow: 1;
}

.el-input,
.el-button {
  margin-right: 10px;
}

.el-button {
  padding: 0 15px;
}

.el-button--icon {
  border: none;
  background-color: transparent;
}

.el-icon-smile,
.el-icon-microphone {
  color: #409eff;
}

.chat-background-only {
  background: linear-gradient(to right, #e6e9f0, #eef1f5);
  flex: 3;
  display: flex;
  justify-content: center;
  align-items: center;
}

.chat-background-only img {
  width: 400px;
}
</style>