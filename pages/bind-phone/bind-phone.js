// 导入API
const { bindPhone, sendSmsCode } = require('../../api/userApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    phone: '',       // 手机号
    code: '',        // 验证码
    openId: '',      // 微信openId
    codeSent: false, // 是否已发送验证码
    countdown: 60,   // 倒计时（秒）
    showError: false, // 是否显示错误提示
    errorMessage: '' // 错误信息
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    console.log('绑定手机号页面参数:', options);
    // 获取从登录页传递过来的openId
    if (options && options.openId) {
      this.setData({
        openId: options.openId
      });
      console.log('从URL参数获取到openId:', options.openId);
    } else {
      // 尝试从全局状态获取
      const app = getApp();
      if (app && app.globalData && app.globalData.openId) {
        this.setData({
          openId: app.globalData.openId
        });
        console.log('从全局状态获取到openId:', app.globalData.openId);
      } else {
        // 最后尝试从本地存储获取
        const openId = wx.getStorageSync('openId');
        if (openId) {
          this.setData({
            openId: openId
          });
          console.log('从本地存储获取到openId:', openId);
        } else {
          this.showError('登录信息丢失，请返回重新登录');
          console.error('无法获取openId，登录信息丢失');
        }
      }
    }
  },

  /**
   * 页面显示时检查
   */
  onShow: function() {
    // 如果没有openId，再次尝试获取
    if (!this.data.openId) {
      const app = getApp();
      if (app && app.globalData && app.globalData.openId) {
        this.setData({
          openId: app.globalData.openId
        });
        console.log('页面显示时，从全局状态获取到openId:', app.globalData.openId);
      }
    }
  },

  /**
   * 手机号输入
   */
  onPhoneInput: function(e) {
    this.setData({
      phone: e.detail.value
    });
  },

  /**
   * 清除手机号
   */
  clearPhone: function() {
    this.setData({
      phone: ''
    });
  },

  /**
   * 验证码输入
   */
  onCodeInput: function(e) {
    this.setData({
      code: e.detail.value
    });
  },

  /**
   * 显示错误提示
   */
  showError: function(message) {
    this.setData({
      showError: true,
      errorMessage: message
    });
  },

  /**
   * 关闭错误提示
   */
  closeError: function() {
    this.setData({
      showError: false,
      errorMessage: ''
    });
  },

  /**
   * 使用微信授权获取手机号
   */
  useWechatPhoneNumber: function() {
    // 返回到登录页面，使用微信授权获取手机号
    wx.navigateBack({
      delta: 1,
      success: () => {
        console.log('成功返回登录页');
      },
      fail: (err) => {
        console.error('返回登录页失败:', err);
        wx.redirectTo({
          url: '/pages/login/login'
        });
      }
    });
  },

  /**
   * 发送验证码
   */
  sendCode: function() {
    const phone = this.data.phone;
    
    // 验证手机号格式
    if (!/^1\d{10}$/.test(phone)) {
      this.showError('请输入正确的11位手机号码');
      return;
    }
    
    // 显示加载中
    wx.showLoading({
      title: '发送中...',
    });
    
    // 模拟发送验证码，始终使用0628作为验证码
    setTimeout(() => {
      wx.hideLoading();
      
      wx.showToast({
        title: '验证码已发送',
        icon: 'success'
      });
      
      // 开始倒计时
      this.startCountdown();
      
      // 设置固定验证码
      this.setData({
        code: '0628'
      });
      
      console.log('已发送验证码: 0628');
    }, 1000);
    
    // 注释掉真实API调用
    /*
    sendSmsCode({
      phone: phone
    }).then(res => {
      wx.hideLoading();
      
      wx.showToast({
        title: '验证码已发送',
        icon: 'success'
      });
      
      // 开始倒计时
      this.startCountdown();
    }).catch(err => {
      wx.hideLoading();
      
      // 显示错误提示
      this.showError(err && err.message ? err.message : '验证码发送失败，请稍后重试');
    });
    */
  },
  
  /**
   * 开始倒计时
   */
  startCountdown: function() {
    let seconds = this.data.countdown;
    
    this.setData({
      codeSent: true
    });
    
    const timer = setInterval(() => {
      seconds--;
      
      if (seconds <= 0) {
        clearInterval(timer);
        this.setData({
          codeSent: false,
          countdown: 60
        });
        return;
      }
      
      this.setData({
        countdown: seconds
      });
    }, 1000);
  },
  
  /**
   * 绑定手机号
   */
  bindPhone: function() {
    const { phone, code, openId } = this.data;
    
    // 验证手机号格式
    if (!/^1\d{10}$/.test(phone)) {
      this.showError('请输入正确的11位手机号码');
      return;
    }
    
    // 验证验证码格式
    if (!/^\d{4}$/.test(code)) {
      this.showError('请输入4位数字验证码');
      return;
    }
    
    // 检查是否有openId
    if (!openId) {
      this.showError('登录信息丢失，请返回重新登录');
      return;
    }

    // 检查验证码是否为0628
    if (code !== '0628') {
      this.showError('验证码错误，请输入正确的验证码');
      return;
    }
    
    // 显示加载中
    wx.showLoading({
      title: '绑定中...',
    });
    
    // 模拟绑定成功
    setTimeout(() => {
      wx.hideLoading();
      
      wx.showToast({
        title: '绑定成功',
        icon: 'success'
      });
      
      // 保存登录状态
      const mockData = {
        token: 'mock_token_' + new Date().getTime(),
        userId: 'user_' + phone,
        expireTime: new Date().getTime() + 24 * 60 * 60 * 1000
      };
      
      wx.setStorageSync('token', mockData.token);
      wx.setStorageSync('userId', mockData.userId);
      wx.setStorageSync('phoneNumber', phone);
      wx.setStorageSync('expireTime', mockData.expireTime);
      
      // 更新全局登录状态
      const app = getApp();
      if (app && app.globalData) {
        app.globalData.isLogin = true;
        app.globalData.userInfo = {
          phoneNumber: phone,
          userId: mockData.userId
        };
      }
      
      // 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index',
          success: () => {
            console.log('跳转到首页成功');
          },
          fail: (err) => {
            console.error('跳转到首页失败:', err);
            // 如果switchTab失败，尝试使用redirectTo
            wx.redirectTo({
              url: '/pages/index/index'
            });
          }
        });
      }, 1500);
    }, 1500);
    
    // 注释掉真实API调用
    /*
    bindPhone({
      phone: phone,
      code: code,
      openId: openId
    }).then(res => {
      wx.hideLoading();
      
      wx.showToast({
        title: '绑定成功',
        icon: 'success'
      });
      
      // 保存登录状态
      const { token, userId, expireTime } = res;
      wx.setStorageSync('token', token);
      wx.setStorageSync('userId', userId);
      wx.setStorageSync('phoneNumber', phone);
      wx.setStorageSync('expireTime', expireTime || (new Date().getTime() + 24 * 60 * 60 * 1000));
      
      // 更新全局登录状态
      const app = getApp();
      if (app && app.globalData) {
        app.globalData.isLogin = true;
      }
      
      // 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index',
          success: () => {
            console.log('跳转到首页成功');
          },
          fail: (err) => {
            console.error('跳转到首页失败:', err);
            // 如果switchTab失败，尝试使用redirectTo
            wx.redirectTo({
              url: '/pages/index/index'
            });
          }
        });
      }, 1500);
    }).catch(err => {
      wx.hideLoading();
      
      // 显示错误提示
      this.showError(err && err.message ? err.message : '绑定失败，请检查验证码是否正确');
    });
    */
  }
}); 