// 导入API
const { updateUserInfo, getUserInfo } = require('../../api/userApi');
const { getConfig } = require('../../config/env');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    nickname: '',       // 用户昵称
    avatarUrl: '',      // 头像URL
    userId: '',         // 用户ID
    isFormValid: false, // 表单是否有效
    tempFilePath: ''    // 临时文件路径
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    // 获取用户ID
    const userId = wx.getStorageSync('userId');
    if (userId) {
      this.setData({
        userId: userId
      });
      // 加载用户信息
      this.loadUserInfo();
    } else {
      wx.showToast({
        title: '登录信息丢失，请重新登录',
        icon: 'none'
      });
      
      // 跳转到登录页
      setTimeout(() => {
        wx.navigateTo({
          url: '/pages/login/login'
        });
      }, 1500);
    }
  },

  /**
   * 加载用户信息
   */
  loadUserInfo: function() {
    wx.showLoading({
      title: '加载中...',
    });
    
    getUserInfo().then(res => {
      wx.hideLoading();
      
      if (res.nickname) {
        this.setData({
          nickname: res.nickname
        });
      }
      
      if (res.avatar) {
        this.setData({
          avatarUrl: res.avatar
        });
      }
      
      // 检查表单是否有效
      this.checkFormValid();
    }).catch(err => {
      wx.hideLoading();
      console.error('获取用户信息失败:', err);
    });
  },

  /**
   * 选择头像
   */
  chooseAvatar: function() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        // 预览头像
        this.setData({
          avatarUrl: res.tempFilePaths[0],
          tempFilePath: res.tempFilePaths[0]
        });
        
        // 检查表单是否有效
        this.checkFormValid();
      }
    });
  },

  /**
   * 昵称输入事件
   */
  onNicknameInput: function(e) {
    this.setData({
      nickname: e.detail.value
    });
    
    // 检查表单是否有效
    this.checkFormValid();
  },

  /**
   * 检查表单是否有效
   */
  checkFormValid: function() {
    // 昵称不能为空且长度在2-12个字符之间
    const isNicknameValid = this.data.nickname && this.data.nickname.length >= 2 && this.data.nickname.length <= 12;
    
    // 头像可以使用默认头像
    const isAvatarValid = true;
    
    this.setData({
      isFormValid: isNicknameValid && isAvatarValid
    });
  },

  /**
   * 保存用户信息
   */
  saveUserInfo: function() {
    if (!this.data.isFormValid) {
      return;
    }
    
    wx.showLoading({
      title: '保存中...',
    });
    
    // 封装请求参数
    const data = {
      nickname: this.data.nickname
    };
    
    // 如果有选择新头像，需要先上传
    if (this.data.tempFilePath) {
      this.uploadAvatar().then(avatarUrl => {
        data.avatar = avatarUrl;
        this.submitUserInfo(data);
      }).catch(err => {
        wx.hideLoading();
        wx.showToast({
          title: '头像上传失败，请重试',
          icon: 'none'
        });
      });
    } else {
      // 没有新头像，直接提交
      if (this.data.avatarUrl) {
        data.avatar = this.data.avatarUrl;
      }
      this.submitUserInfo(data);
    }
  },
  
  /**
   * 上传头像
   */
  uploadAvatar: function() {
    return new Promise((resolve, reject) => {
      const { apiBaseUrl } = getConfig();
      const token = wx.getStorageSync('token') || '';
      
      wx.uploadFile({
        url: apiBaseUrl + '/user/upload-avatar',
        filePath: this.data.tempFilePath,
        name: 'avatar',
        header: {
          'auth': token
        },
        success: (res) => {
          const data = JSON.parse(res.data);
          if (data.error === 0 && data.body && data.body.avatarUrl) {
            resolve(data.body.avatarUrl);
          } else {
            reject(new Error(data.message || '上传失败'));
          }
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  },
  
  /**
   * 提交用户信息
   */
  submitUserInfo: function(data) {
    updateUserInfo(data).then(res => {
      wx.hideLoading();
      
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      });
      
      // 保存成功后跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index'
        });
      }, 1500);
    }).catch(err => {
      wx.hideLoading();
      
      wx.showToast({
        title: '保存失败，请重试',
        icon: 'none'
      });
    });
  }
}); 