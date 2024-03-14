<template>
    <el-dialog :visible="isVisible" title="Settings" width="50%" @close="close">
        <div class="settings-container">
            <div class="settings-menu">
                <el-menu default-active="1" @select="handleSelect" class="el-menu-vertical-demo">
                    <el-menu-item index="1">Personal Center</el-menu-item>
                    <el-menu-item index="2">Security Notifications</el-menu-item>
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
                            <span>187****2054</span> <el-button type="text">Modify</el-button>
                        </el-form-item>
                        <el-form-item label="Email Address:">
                            <span>837215079@qq.com</span> <el-button type="text">Modify</el-button>
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
                  <div class="security-notifications">
                    <h2 class="title">Security</h2>
                    <p class="description">
                      Your conversations and calls are private to you. End-to-end encryption ensures that only you and the person you're communicating with can see your personal messages and listen to your personal calls, and nobody in between, not even this App. Message types include:
                    </p>
                    <ul class="message-types">
                      <li><img src="@/assets/icons/text-voice-messages-icon.png" alt="Text and Voice Messages" /> Text and voice messages</li>
                      <li><img src="@/assets/icons/audio-video-calls-icon.png" alt="Audio and Video Calls" /> Audio and video calls</li>
                      <li><img src="@/assets/icons/photos-videos-documents-icon.png" alt="Photos, Videos, and Documents" /> Photos, videos, and documents</li>
                      <li><img src="@/assets/icons/location-sharing-icon.png" alt="Location Sharing" /> Location sharing</li>
                      <li><img src="@/assets/icons/status-updates-icon.png" alt="Status Updates" /> Status updates</li>
                    </ul>
                    <div class="notification-setting">
                      <p>Show security notifications on this computer</p>
                      <p>
                        You will receive notifications when the security code for a contact's phone changes. If you have multiple devices, you must enable this setting on each device you want to receive notifications on. <a href="https://your-link-to-more-info.com">Learn more</a>
                      </p>
                    </div>
                  </div>
                </div>
                <div v-else-if="activeMenuIndex === '3'">
                    <p>Binding settings content</p>
                </div>
                <div slot="footer" class="dialog-footer">
                    <el-button @click="saveChanges">Save Changes</el-button>
                </div>
            </div>
        </div>
    </el-dialog>
</template>


<script>
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
                avatar: 'https://www.freeimg.cn/i/2024/03/04/65e57ae09c447.jpg',
                nickname: 'La La La',
                gender: 'Female',
                birthday: '2024-01-28',
                signature: `1. Guess who I am\n2. Do you guess I guess\n3. Do you guess I guess you guess\n4. I guess you guess I guess you don't guess, guess guess don't guess`,
            },

        };
    },
    methods: {
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
.security-notifications .title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 1rem;
}
.security-notifications .description,
.security-notifications .notification-setting p {
  margin-bottom: 1rem;
}
.message-types {
  list-style-type: none;
  padding-left: 0;
  margin-bottom: 1rem;
}

.message-types li {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem; /* Increased line spacing */
}

.message-types li img {
  margin-right: 10px; /* Space between icon and text */
  width: 24px; /* Icon size */
  height: auto;
  vertical-align:middle;
}

.notification-setting a {
  color: #00c39a; /* Link color */
  text-decoration:underline;
}
</style>