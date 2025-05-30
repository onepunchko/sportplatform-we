const { getSportStats } = require('../../api/userApi');
const { getMyReservations } = require('../../api/reservationApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    // 运动数据
    sportData: {
      steps: 8546,      // 步数
      distance: 3.2,     // 距离（千米）
      calories: 232,     // 卡路里
      duration: 45       // 运动时长（分钟）
    },
    // 场地预约
    reservations: [],
    // 校园热门活动
    hotActivities: [
      {
        id: 1,
        title: '校园马拉松',
        time: '5月15日 · 上午8:00',
        image: 'https://img.freepik.com/free-photo/soccer-players-action-professional-stadium_31965-8365.jpg'
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    if (wx.getUserProfile) {
      this.setData({
        canIUseGetUserProfile: true
      })
    }
    
    // 检查登录状态
    this.checkLoginStatus();
  },
  
  /**
   * 检查登录状态
   */
  checkLoginStatus: function() {
    // 获取应用实例
    const app = getApp();
    
    // 检查登录状态
    const token = wx.getStorageSync('token');
    const expireTime = wx.getStorageSync('expireTime');
    const currentTime = new Date().getTime();
    
    console.log('检查登录状态:', {token: !!token, expireTime, currentTime});
    
    // 判断token是否存在且未过期
    if (token && expireTime && currentTime < expireTime) {
      console.log('用户已登录，token有效');
      app.globalData.isLogin = true;
      
      // 加载数据
      this.getSportData();
      this.getReservations();
    } else {
      console.log('用户未登录或token已过期，需要跳转登录页');
      // token不存在或已过期，清除本地存储
      wx.removeStorageSync('token');
      wx.removeStorageSync('userId');
      wx.removeStorageSync('expireTime');
      wx.removeStorageSync('openId');
      
      app.globalData.isLogin = false;
      app.globalData.hasUserInfo = false;
      
      // 使用两阶段策略 - 先显示提示再导航
      wx.showModal({
        title: '登录提示',
        content: '请先登录后使用完整功能',
        showCancel: false,
        success: () => {
          // 强制跳转到登录页面 - 使用redirectTo而非reLaunch
          wx.redirectTo({
            url: '/pages/login/login',
            success: () => {
              console.log('跳转登录页成功');
            },
            fail: (err) => {
              console.error('跳转登录页失败:', err);
              
              // 如果redirectTo失败，尝试使用reLaunch
              setTimeout(() => {
                wx.reLaunch({
                  url: '/pages/login/login'
                });
              }, 500);
            }
          });
        }
      });
    }
  },

  /**
   * 获取用户运动数据
   */
  getSportData: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    getSportStats().then(res => {
      this.setData({
        'sportData.steps': res.steps || 0,
        'sportData.distance': res.distance || 0,
        'sportData.calories': res.calories || 0,
        'sportData.duration': res.duration || 0
      });
    }).catch(err => {
      console.error('获取运动数据失败', err);
      
      // 检查是否是因为未登录导致的
      if (err.message === '请先登录') {
        this.checkLoginStatus();
      }
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 获取预约数据
   */
  getReservations: function() {
    getMyReservations().then(res => {
      this.setData({
        reservations: res.slice(0, 2) // 只显示最近的两个预约
      });
    }).catch(err => {
      console.error('获取预约数据失败', err);
      
      // 检查是否是因为未登录导致的
      if (err.message === '请先登录') {
        this.checkLoginStatus();
      }
    });
  },
  
  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    // 获取应用实例
    const app = getApp();
    console.log('首页显示, 全局登录状态:', app.globalData.isLogin);
    
    // 如果用户已登录，刷新数据
    if (app.globalData.isLogin) {
      console.log('已登录状态，刷新数据');
      this.getSportData();
      this.getReservations();
    } else {
      console.log('未登录状态，执行登录检查');
      this.checkLoginStatus();
    }
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: '大学生运动健康小程序',
      path: '/pages/index/index'
    }
  },

  /**
   * 跳转到场地预约页面
   */
  goToReservation: function() {
    wx.switchTab({
      url: '/pages/reservation/reservation',
    })
  },

  /**
   * 跳转到运动追踪页面
   */
  goToTracking: function() {
    wx.switchTab({
      url: '/pages/tracking/tracking',
    })
  },
  
  /**
   * 跳转到运动社区页面
   */
  goToCommunity: function() {
    wx.switchTab({
      url: '/pages/community/community',
    })
  },
  
  /**
   * 跳转到活动详情页面
   */
  goToActivityDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/activityDetail/activityDetail?id=${id}`,
    })
  },
  
  /**
   * 跳转到AI教练页面
   */
  goToAiCoach: function() {
    wx.navigateTo({
      url: '/pages/ai-coach/ai-coach',
    })
  },
  
  /**
   * 跳转到运动挑战页面
   */
  goToChallenge: function() {
    wx.navigateTo({
      url: '/pages/challenge/challenge',
    })
  },
  
  /**
   * 跳转到运动资讯页面
   */
  goToNews: function() {
    wx.navigateTo({
      url: '/pages/news/news',
    })
  }
}) 