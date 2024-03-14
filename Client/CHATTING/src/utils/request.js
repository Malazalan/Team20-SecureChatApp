// request.js
import axios from 'axios';
import { Notification } from 'element-ui'; // 如果你使用Element UI

// 创建axios实例
const service = axios.create({
    baseURL: process.env.VUE_APP_BASE_API, // API 的 base_url 你们后端的API
    timeout: 5000 // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
    config => {
        // 在这里可以做一些请求前的操作，比如设置token
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = 'Bearer ' + token;
        }
        return config;
    },
    error => {
        // 处理请求错误
        console.error('Request Error:', error); // for debug
        Promise.reject(error);
    }
);

// 响应拦截器
service.interceptors.response.use(
    response => {
        const res = response.data;
        // 根据实际情况调整，这里假设当code不为200时表示后端返回了某种错误
        if (res.code !== 200) {
            Notification.error({
                title: 'Error',
                message: res.message || 'Error',
                duration: 5000
            });
            // 你可以在这里处理更多的错误情况，比如token过期、服务器错误等
            return Promise.reject(new Error(res.message || 'Error'));
        } else {
            return res;
        }
    },
    error => {
        console.error('Response Error:', error); // for debug
        Notification.error({
            title: 'Error',
            message: error.message,
            duration: 5000
        });
        return Promise.reject(error);
    }
);

export default service;
