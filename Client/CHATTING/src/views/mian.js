import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import './assets/css/main.css'

Vue.use(ElementUI);

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

Vue.prototype.$errorHandler = function (error) {
  this.$notify.error({
    title: '错误',
    message: error
  });
};

Vue.prototype.$successHandler = function (message) {
  this.$notify({
    title: '成功',
    message: message,
    type: 'success'
  });
};