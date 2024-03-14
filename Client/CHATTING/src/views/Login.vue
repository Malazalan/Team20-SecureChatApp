<template>
  <div class="login-wrapper">
    <div class="bg-wrapper">
      <div class="left-wrapper">
        <img src="@/assets/images/logo.jpg" class="logo-img" />
        <span class="title">secure chat</span>
      </div>
      <div class="right-wrapper">
        <!-- 登录表单 -->
        <el-form :model="loginData" :rules="rules" ref="loginForm" v-if="currentForm === 'login'">
          <div class="login-title">Welcome to login</div>
          <el-form-item class="input-item" prop="username">
            <el-input v-model.trim="loginData.username" size="large" clearable class="input-field"
                      placeholder="Mobile phone number" prefix-icon="el-icon-mobile-phone"
                      @input="removeChinese"></el-input>
          </el-form-item>
          <el-form-item class="input-item" prop="password">
            <el-input show-password v-model.trim="loginData.password" size="large" class="input-field"
                      type="password" placeholder="password" prefix-icon="el-icon-lock"></el-input>
          </el-form-item>
          <el-form-item class="submit-item">
            <el-button type="primary" class="submit-button" size="large"
                       @click="handleLogin">login</el-button>
          </el-form-item>
          <div class="actions">
            <el-button type="text" @click="switchForm('register')">Sign up for an account</el-button>
            <el-button type="text" @click="switchForm('forgotPassword')">Forgot password</el-button>
          </div>
        </el-form>

        <!-- 注册表单 -->
        <el-form :model="registerData" :rules="registerRules" ref="registerForm"
                 v-if="currentForm === 'register'">
          <div class="login-title">Sign up for an account</div>
          <el-form-item class="input-item" prop="username">
            <el-input v-model.trim="registerData.username" size="large" clearable class="input-field"
                      placeholder="Mobile phone number" prefix-icon="el-icon-mobile-phone"></el-input>
          </el-form-item>
          <el-form-item class="input-item" prop="password">
            <el-input v-model.trim="registerData.password" size="large" class="input-field" type="password"
                      placeholder="password" prefix-icon="el-icon-lock"></el-input>
          </el-form-item>
          <el-form-item class="input-item" prop="email">
            <el-input v-model.trim="registerData.email" size="large" clearable class="input-field"
                      placeholder="email" prefix-icon="el-icon-message"></el-input>
          </el-form-item>
          <el-form-item class="input-item" prop="verificationCode">
            <el-input v-model.trim="registerData.verificationCode" size="large" clearable
                      class="input-field" placeholder="Captcha" prefix-icon="el-icon-message"></el-input>
            <button @click.prevent="getCode('register')" class="code-btn" :disabled="!show">
              <span v-show="show">verification</span>
              <span v-show="!show" class="count">{{ count }} s</span>
            </button>
          </el-form-item>
          <el-form-item class="submit-item">
            <el-button type="primary" class="submit-button" size="large"
                       @click="handleRegister">enroll</el-button>
          </el-form-item>
        </el-form>

        <!-- 忘记密码表单 -->
        <el-form :model="forgotData" :rules="forgotRules" ref="forgotForm"
                 v-if="currentForm === 'forgotPassword'">
          <div class="login-title">Reset your password</div>
          <el-form-item class="input-item" prop="username">
            <el-input v-model.trim="forgotData.username" size="large" clearable class="input-field"
                      placeholder="Mobile phone number" prefix-icon="el-icon-mobile-phone"></el-input>
          </el-form-item>
          <el-form-item class="input-item" prop="verificationCode">
            <el-input v-model.trim="forgotData.verificationCode" size="large" clearable class="input-field"
                      placeholder="Captcha" prefix-icon="el-icon-message"></el-input>
            <button @click.prevent="getCode('forgot')" class="code-btn" :disabled="!show">
              <span v-show="show">verification</span>
              <span v-show="!show" class="count">{{ count }} s</span>
            </button>
          </el-form-item>
          <el-form-item class="input-item" prop="newPassword">
            <el-input v-model.trim="forgotData.newPassword" size="large" class="input-field" type="password"
                      placeholder="New passwords" prefix-icon="el-icon-lock"></el-input>
          </el-form-item>
          <el-form-item class="submit-item">
            <el-button type="primary" class="submit-button" size="large" @click="handleResetPassword">Reset
              your password</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>


<script>
import {login} from "@/api/login"
import {register} from "@/api/login"
import {ForgetPassword} from "@/api/login";

export default {
  data() {
    return {
      count: 60,
      show: true,
      timer: null,
      currentForm: 'login',
      loginData: {
        username: '',
        password: '',
      },
      registerData: {
        username: '',
        password: '',
        email: '',
        verificationCode: '',
      },
      forgotData: {
        username: '',
        verificationCode: '',
        newPassword: '',
      },
      rules: {
        username: [
          { required: true, message: 'Please enter your mobile number', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: 'Incorrect mobile number format', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Please enter your password', trigger: 'blur' },
        ]
      },
      registerRules: {
        username: [
          { required: true, message: 'Please enter your mobile number', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: 'Incorrect mobile number format', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Please enter your password', trigger: 'blur' },
        ],
        email: [
          { required: true, message: 'Please enter your email', trigger: 'blur' },
          // Use a more appropriate pattern for validating emails
          { pattern:  /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/, message: 'Incorrect email format', trigger: 'blur' }
        ],
        verificationCode: [
          { required: true, message: 'Please enter the verification code', trigger: 'blur' },
          { len: 6, message: 'Verification code should be 6 digits', trigger: 'blur' }
        ],
      },
      forgotRules: {
        username: [
          { required: true, message: 'Please enter your mobile number', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: 'Incorrect mobile number format', trigger: 'blur' }
        ],
        verificationCode: [
          { required: true, message: 'Please enter the verification code', trigger: 'blur' },
          { len: 6, message: 'Verification code should be 6 digits', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: 'Please enter a new password', trigger: 'blur' },
        ],
      },
    };

  },

  methods: {
    getCode(formType) {
      if (!this.timer) {
        this.count = 60;
        this.show = false;
        this.timer = setInterval(() => {
          if (this.count > 0 && this.count <= 60) {
            this.count--;
          } else {
            this.show = true;
            clearInterval(this.timer);
            this.timer = null;
          }
        }, 1000);
      }
    },

    async handleLogin() {
      const valid = await this.$refs.loginForm.validate();
      if (!valid) return;
      login(this.loginData).then((res) =>{
        //后端返回数据中的TOKEN信息
        if(res.status)
        {
          //将TOKEN存入LOCAL SOTRAGE里

        }
        else {
          console.log("DENGLUXXX")
        }
        // 登录逻辑...
        this.$router.push('/');

      })

    },


    async handleRegister() {
      // 验证表单数据
      const valid = await this.$refs.registerForm.validate();
      if (!valid) return; // 表单数据无效时退出函数

      // 调用注册API
      register(this.registerData).then((res) => {
        // 检查后端返回的状态
        if (res.status) {
          // 注册成功
          // 如果后端在注册成功后返回Token，并且你想让用户直接登录，可以像登录逻辑那样处理Token
          // localStorage.setItem('token', res.token);

          // 注册成功的处理逻辑，比如跳转到登录页或首页等
          this.$message.success('注册成功！请登录。');
          this.$router.push('/login'); // 假设你有一个登录页面

        } else {
          // 注册失败的处理逻辑
          // 这里可以显示后端返回的错误消息，或者如果后端没有返回具体错误信息，可以给出默认的错误提示
          this.$message.error(res.message || '注册失败，请稍后再试。');
        }
      }).catch(error => {
        // 网络或其他错误的处理逻辑
        console.error('注册异常', error);
        this.$message.error('注册过程中发生异常，请稍后再试。');
      });
    },



    async handleResetPassword() {
      // 验证表单数据
      const valid = await this.$refs.resetForm.validate();
      if (!valid) return; // 表单数据无效时退出函数

      // 调用忘记密码API
      ForgetPassword(this.forgotData).then((res) => {
        // 检查后端返回的状态
        if (res.status) {
          // 密码重置成功的处理逻辑
          this.$message.success('密码重置成功，请使用新密码登录。');
          this.$router.push('/login'); // 假设你有一个登录页面

        } else {
          // 密码重置失败的处理逻辑
          this.$message.error(res.message || '密码重置失败，请稍后再试。');
        }
      }).catch(error => {
        // 网络或其他错误的处理逻辑
        console.error('密码重置异常', error);
        this.$message.error('密码重置过程中发生异常，请稍后再试。');
      });
    },

    switchForm(form) {
      this.currentForm = form;
      this.resetTimer();
    },

    removeChinese() {
      if (this.currentForm === 'login') {
        this.loginData.username = this.loginData.username.replace(/[\u4e00-\u9fa5]/g, '');
      }
    },

    resetTimer() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
        this.show = true;
      }
    },
  },

  beforeDestroy() {
    this.resetTimer();
  },
};
</script>


<style scoped>
.pr {
  position: relative;
}

.code-btn {
  width: 100px;
  height: 20px;
  position: absolute;
  top: 10px;
  right: 5px;
  z-index: 222;
  color: #ef8466;
  font-size: 14px;
  border: none;
  border-left: 1px solid #bababa;
  padding-left: 10px;
  background-color: #fff;
  cursor: pointer;
}

.login-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;
  background-image: url("@/assets/images/login_bg.jpg");
  background-size: cover;
  display: flex;
  flex-direction: row;
  z-index: 1;
  justify-content: center;
  align-items: center;
}

.bg-wrapper {
  width: 70%;
  height: 65%;
  z-index: 9999;
  opacity: 0.95;
  display: flex;
  flex-direction: row;
}

.left-wrapper {
  display: flex;
  flex: 1;
  background-color: #6190e8;
  border-top-left-radius: 5px;
  border-bottom-left-radius: 5px;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.title {
  color: white;
  font-size: 30px;
  margin-top: 30px;
}

.right-wrapper {
  flex: 1;
  background-color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top-right-radius: 5px;
  border-bottom-right-radius: 5px;
}

.login-title {
  width: 300px;
  text-align: center;
  font-size: 30px;
  margin-bottom: 40px;
}

.logo-img {
  border-radius: 10px;
  width: 80px;
  height: 80px;
}

.input-item {
  margin-top: 20px;
}

.input-field {
  width: 300px;
}

.submit-item {
  margin-top: 30px;
}

.submit-button {
  width: 100%;
}

.actions {
  text-align: center;
}
</style>
