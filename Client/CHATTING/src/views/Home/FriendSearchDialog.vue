<template>
    <el-dialog :visible.sync="isVisible" title="搜索好友" @close="handleClose" width="20%"
        :custom-class="'round-dialog'">
        <el-form :model="form" :rules="rules" ref="searchForm">
            <el-form-item label="请输入手机号或姓名" label-position="left">
                <el-input v-model="form.keyword" clearable></el-input>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose">取消</el-button>
            <el-button type="primary" @click="validateForm">搜索</el-button>
        </span>
    </el-dialog>
</template>

<script>
import axios from 'axios';

export default {
    name: "FriendSearchDialog",
    props: {
        isVisible: {
            type: Boolean,
            required: true
        }
    },
    data() {
        return {
            form: {
                keyword: ''
            },
            rules: {
                keyword: [
                    { required: true, message: '请输入手机号或姓名', trigger: 'blur' }
                ]
            }
        };
    },
    methods: {
        handleClose() {
            this.$emit('update:isVisible', false);
            this.form.keyword = ''; // Clear keyword
        },
        validateForm() {
            this.$refs.searchForm.validate((valid) => {
                if (valid) {
                    this.searchFriend();
                } else {
                    console.log('表单验证失败');
                    return false;
                }
            });
        },
        searchFriend() {
            axios.get('/search', {
                params: {
                    keyword: this.form.keyword
                }
            })
            .then(response => {
                const userData = response.data;
                if (userData) {
                    console.log('找到用户：', userData);
                } else {
                    console.log('未找到提供的信息对应的用户。');
                }
                this.handleClose();
            })
            .catch(error => {
                console.error('搜索用户时出错：', error);
                alert('搜索用户失败。请稍后再试。');
            });
        }
    }
};
</script>
