// 导入API
const { getUserInfo } = require('./api/userApi');

App({
  globalData: {
    userInfo: null,
    isLogin: false,
    hasUserInfo: false,
    needBindPhone: false, // 标记是否需要跳转到手机号绑定页面
    openId: '' // 存储openId，用于跳转失败时的恢复
  },
  
  onLaunch: function() {
    // 检查登录状态
    this.checkLoginStatus();
  },

  onShow: function() {
    // 再次检查登录状态，防止token过期
    this.checkLoginStatus();

    // 根据检查结果决定是否跳转登录页
    this.checkNeedLogin().catch(err => {
      console.error('自动跳转登录失败:', err);
    });
  },
  
  /**
   * 检查登录状态
   */
  checkLoginStatus: function() {
    const token = wx.getStorageSync('token');
    const expireTime = wx.getStorageSync('expireTime');
    
    // 判断token是否存在且未过期
    if (token && expireTime && new Date().getTime() < expireTime) {
      this.globalData.isLogin = true;
      
      // 获取用户信息
      this.getUserInfo();
    } else {
      // token不存在或已过期，清除本地存储
      wx.removeStorageSync('token');
      wx.removeStorageSync('userId');
      wx.removeStorageSync('expireTime');
      wx.removeStorageSync('openId');
      
      this.globalData.isLogin = false;
      this.globalData.hasUserInfo = false;
    }
  },
  
  /**
   * 获取用户信息
   */
  getUserInfo: function() {
    // 如果已经有用户信息，直接返回
    if (this.globalData.userInfo) {
      return;
    }
    
    // 调用API获取用户信息
    getUserInfo().then(res => {
      this.globalData.userInfo = res;
      
      // 检查用户信息是否完整
      const hasNickname = res.nickname && res.nickname !== '';
      const hasAvatar = res.avatar && res.avatar !== '';
      
      this.globalData.hasUserInfo = hasNickname && hasAvatar;
    }).catch(err => {
      console.error('获取用户信息失败:', err);
      this.globalData.hasUserInfo = false;
    });
  },
  
  /**
   * 检查是否需要登录，如需要则跳转到登录页
   */
  checkNeedLogin: function() {
    return new Promise((resolve, reject) => {
      const pages = getCurrentPages();
      const currentRoute = pages.length ? pages[pages.length - 1].route : '';

      if (!this.globalData.isLogin) {
        // 未登录，跳转到登录页
        if (currentRoute !== 'pages/login/login') {
          wx.reLaunch({
            url: '/pages/login/login',
            success: function() {
              resolve(false);
            },
            fail: function(err) {
              reject(err);
            }
          });
        } else {
          resolve(false);
        }
      } else if (!this.globalData.hasUserInfo) {
        // 已登录但用户信息不完整，跳转到用户信息完善页
        if (currentRoute !== 'pages/user-profile/user-profile') {
          wx.navigateTo({
            url: '/pages/user-profile/user-profile',
            success: function() {
              resolve(false);
            },
            fail: function(err) {
              reject(err);
            }
          });
        } else {
          resolve(false);
        }
      } else {
        // 已登录且信息完整
        resolve(true);
      }
    });
  }
}); 