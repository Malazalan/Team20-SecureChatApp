<template>
    <el-dialog :visible.sync="isVisible" title="Search Friends" @close="handleClose" width="20%"
        :custom-class="'round-dialog'">
        <el-form :model="form" :rules="rules" ref="searchForm">
            <el-form-item label="Please enter phone number" label-position="left" prop="phoneNumber">
                <el-input v-model="form.phoneNumber" clearable></el-input>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose">Cancel</el-button>
            <el-button type="primary" @click="validateForm">Search</el-button>
        </span>
    </el-dialog>
</template>



<script>
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
                phoneNumber: ''
            },
            rules: {
                phoneNumber: [
                    { required: true, message: 'Please enter a phone number', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: 'Invalid phone number format', trigger: 'blur' }
                ]
            }
        };
    },
    methods: {
        handleClose() {
            this.$emit('update:isVisible', false);
            this.form = {}
        },
        validateForm() {
            this.$refs.searchForm.validate((valid) => {
                if (valid) {
                    this.searchFriend();
                } else {
                    console.log('Form validation failed');
                    return false;
                }
            });
        },
        searchFriend() {
            console.log('Searching for friend with phone number:', this.form.phoneNumber);
            this.handleClose();
        }
    }
};
</script>