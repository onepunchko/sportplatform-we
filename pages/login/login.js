// 导入API
const { wxLogin, updatePhone } = require('../../api/userApi');
const { getConfig } = require('../../config/env');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    hasUserInfo: false,     // 是否已获取用户信息
    hasPhoneNumber: false,  // 是否已获取手机号
    showRejectGuide: false, // 是否显示拒绝授权引导
    token: '',              // 用户token
    userId: '',             // 用户ID
    openId: '',             // 微信openId
    isLoginSuccessful: false  // 登录是否成功
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    console.log('登录页加载');
    // 检查本地存储中是否有登录状态
    const token = wx.getStorageSync('token');
    const expireTime = wx.getStorageSync('expireTime');
    const currentTime = new Date().getTime();
    
    console.log('当前登录状态:', {token: !!token, expireTime, currentTime});
    
    // 如果有token且未过期，直接跳转到首页
    if (token && expireTime && currentTime < expireTime) {
      console.log('已有有效token，直接跳转首页');
      this.redirectAfterLogin();
    } else {
      console.log('无有效token，需要登录');
      // 获取全局应用状态
      const app = getApp();
      app.globalData.isLogin = false;
    }
  },
  
  /**
   * 页面显示时触发
   */
  onShow: function() {
    console.log('登录页显示');
    
    // 检查是否需要跳转到手机号绑定页面（处理导航失败的情况）
    const app = getApp();
    if (app.globalData.needBindPhone && app.globalData.openId) {
      const openId = app.globalData.openId;
      
      // 清除标记
      app.globalData.needBindPhone = false;
      
      // 设置到页面数据中
      this.setData({
        openId: openId
      });
      
      // 延迟一下再跳转，确保页面已经完全加载
      setTimeout(() => {
        // 直接使用redirectTo跳转
        wx.redirectTo({
          url: `/pages/bind-phone/bind-phone?openId=${openId}`,
          fail: function(err) {
            console.error('延迟跳转绑定手机页也失败:', err);
            
            // 最后尝试使用reLaunch
            setTimeout(() => {
              wx.reLaunch({
                url: `/pages/bind-phone/bind-phone?openId=${openId}`
              });
            }, 500);
          }
        });
      }, 800);
    }
  },

  /**
   * 微信登录
   */
  handleWxLogin: function() {
    console.log('触发微信登录');
    wx.showLoading({
      title: '授权中...',
    });
    
    // 调用微信登录接口
    wx.login({
      success: (res) => {
        console.log('wx.login成功', res);
        if (res.code) {
          // 发送code到后端
          this.loginWithWxCode(res.code);
        } else {
          this.showLoginError('微信登录失败，请重试');
          this.setData({
            showRejectGuide: true
          });
        }
      },
      fail: (err) => {
        console.error('wx.login失败:', err);
        this.showLoginError('微信登录失败，请重试');
        this.setData({
          showRejectGuide: true
        });
      }
    });
  },

  /**
   * 使用微信code登录
   */
  loginWithWxCode: function(code) {
    console.log('使用code登录:', code);
    // 调用后端接口，传入code
    wxLogin({
      code: code
    }).then(res => {
      console.log('登录成功, 返回数据:', res);
      // 保存token和userId
      this.setData({
        token: res.token,
        userId: res.userId,
        openId: res.openId,
        hasUserInfo: true
      });
      
      // 保存到本地存储，设置过期时间为1天
      const expireTime = new Date().getTime() + 24 * 60 * 60 * 1000;
      wx.setStorageSync('token', res.token);
      wx.setStorageSync('userId', res.userId);
      wx.setStorageSync('openId', res.openId);
      wx.setStorageSync('expireTime', expireTime);
      
      // 设置全局登录状态
      const app = getApp();
      app.globalData.isLogin = true;
      
      wx.hideLoading();
      
      // 检查是否有手机号
      if (res.phoneNumber) {
        this.setData({
          hasPhoneNumber: true
        });
        
        // 检查用户信息是否完整
        this.checkUserInfoComplete(res);
      }
    }).catch(err => {
      console.error('微信登录接口调用失败:', err);
      this.showLoginError('登录失败，请重试');
    });
  },

  /**
   * 检查用户信息是否完整
   */
  checkUserInfoComplete: function(userInfo) {
    // 检查是否有昵称和头像
    const hasNickname = userInfo.nickname && userInfo.nickname !== '';
    const hasAvatar = userInfo.avatar && userInfo.avatar !== '';
    
    if (!hasNickname || !hasAvatar) {
      // 登录成功但信息不完整，跳转到完善信息页面
      setTimeout(() => {
        wx.navigateTo({
          url: '/pages/user-profile/user-profile'
        });
      }, 1000);
    } else {
      // 信息完整，直接跳转到首页
      setTimeout(() => {
        this.redirectAfterLogin();
      }, 1000);
    }
  },

  /**
   * 获取手机号
   */
  getPhoneNumber: function(e) {
    console.log('获取手机号返回数据:', e.detail);
    
    // 保存openId到局部变量，避免作用域问题
    const openId = this.data.openId;
    
    // 检查是否获取成功
    if (e.detail.errMsg !== 'getPhoneNumber:ok') {
      this.showLoginError('获取手机号失败，请手动输入');
      
      // 保存状态到全局，避免导航失败情况
      const app = getApp();
      app.globalData.needBindPhone = true;
      app.globalData.openId = openId;
      
      // 尝试使用showModal先显示提示，然后再导航
      wx.showModal({
        title: '提示',
        content: '获取手机号失败，需要手动输入',
        showCancel: false,
        success: () => {
          // 修复导航超时问题：使用redirectTo替代navigateTo
          wx.redirectTo({
            url: `/pages/bind-phone/bind-phone?openId=${openId}`,
            success: function() {
              console.log('跳转到手动绑定手机号页面成功');
            },
            fail: function(err) {
              console.error('跳转到手动绑定手机号页面失败:', err);
              // 此时已经保存到全局状态，页面onShow时会处理
            }
          });
        }
      });
      return;
    }
    
    wx.showLoading({
      title: '验证中...',
    });

    // 发送加密数据到后端
    updatePhone({
      encryptedData: e.detail.encryptedData,
      iv: e.detail.iv,
      openId: openId
    }).then(res => {
      console.log('手机号解密成功:', res);
      wx.hideLoading();
      
      this.setData({
        hasPhoneNumber: true
      });
      
      // 保存手机号
      wx.setStorageSync('phoneNumber', res.phoneNumber);
      
      // 手机号获取成功，跳转首页或完善信息
      // 检查用户信息完整性
      const app = getApp();
      if (app.globalData.hasUserInfo) {
        // 信息完整，直接跳转首页
        this.redirectAfterLogin();
      } else {
        // 信息不完整，前往完善信息页
        wx.navigateTo({
          url: '/pages/user-profile/user-profile'
        });
      }
    }).catch(err => {
      console.error('更新手机号失败:', err);
      this.showLoginError('手机号绑定失败，请手动输入');
      
      // 保存状态到全局，避免导航失败情况
      const app = getApp();
      app.globalData.needBindPhone = true;
      app.globalData.openId = openId;
      
      // 尝试使用showModal先显示提示，然后再导航
      wx.showModal({
        title: '提示',
        content: '手机号绑定失败，需要手动输入',
        showCancel: false,
        success: () => {
          wx.redirectTo({
            url: `/pages/bind-phone/bind-phone?openId=${openId}`
          });
        }
      });
    });
  },
  
  /**
   * 显示错误提示
   */
  showLoginError: function(message) {
    wx.hideLoading();
    wx.showToast({
      title: message,
      icon: 'none',
      duration: 2000
    });
  },
  
  /**
   * 取消授权
   */
  cancelAuth: function() {
    this.setData({
      showRejectGuide: false
    });
  },
  
  /**
   * 跳转到手动绑定手机号页面
   */
  goToBindPhone: function() {
    // 确保有openId
    const openId = this.data.openId;
    if (openId) {
      // 先保存到全局状态，避免导航失败情况
      const app = getApp();
      app.globalData.needBindPhone = true;
      app.globalData.openId = openId;
      
      // 使用两阶段导航策略
      wx.showModal({
        title: '手机号绑定',
        content: '即将跳转到手机号绑定页面',
        showCancel: false,
        success: () => {
          // 修复导航超时问题：使用redirectTo而非navigateTo
          wx.redirectTo({
            url: `/pages/bind-phone/bind-phone?openId=${openId}`,
            fail: function(err) {
              console.error('跳转到手动绑定手机号页面失败:', err);
              // 已保存到全局状态，不需要再处理
            }
          });
        }
      });
    } else {
      console.error('缺少openId，无法跳转到手动绑定页面');
      wx.showToast({
        title: '登录信息不完整，请重试',
        icon: 'none'
      });
      // 重新触发微信登录
      setTimeout(() => {
        this.handleWxLogin();
      }, 1500);
    }
  },
  
  /**
   * 显示隐私政策
   */
  showPrivacyPolicy: function() {
    wx.navigateTo({
      url: '/pages/privacy/privacy'
    });
  },
  
  /**
   * 登录成功后的跳转处理
   */
  redirectAfterLogin: function() {
    console.log('登录成功，准备跳转');
    this.setData({
      isLoginSuccessful: true
    });
    
    // 使用redirectTo替代switchTab，避免超时问题
    wx.redirectTo({
      url: '/pages/index/index',
      success: function() {
        console.log('跳转首页成功');
      },
      fail: function(err) {
        console.error('跳转首页失败:', err);
        // 如果redirectTo失败，尝试使用reLaunch
        wx.reLaunch({
          url: '/pages/index/index'
        });
      }
    });
  }
}); 