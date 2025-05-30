const { getUserInfo, updateUserInfo, getSportStats } = require('../../api/userApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    userInfo: {
      name: '张小明',
      avatar: '/static/images/avatar.jpg',
      schoolName: '衡阳师范学院',
      studentId: '2020010101',
      days: 127,
      level: 56,
      points: 32
    },
    activityData: {
      steps: 8546,
      distance: 15.482,
      calories: 320,
      time: 127
    },
    achievements: [
      {
        id: 1,
        name: '运动达人',
        icon: '/static/images/achievement1.png',
        description: '累计运动时长超过100小时'
      },
      {
        id: 2,
        name: '篮球高手',
        icon: '/static/images/achievement2.png',
        description: '累计参加篮球运动50次以上'
      },
      {
        id: 3,
        name: '马拉松新手',
        icon: '/static/images/achievement3.png',
        description: '参加校园马拉松比赛并完赛'
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.loadUserInfo();
    this.loadSportStats();
  },

  /**
   * 加载用户信息
   */
  loadUserInfo: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    getUserInfo().then(res => {
      if (res) {
        this.setData({
          userInfo: res
        });
      }
    }).catch(err => {
      console.error('获取用户信息失败', err);
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 加载运动统计数据
   */
  loadSportStats: function() {
    getSportStats().then(res => {
      if (res) {
        this.setData({
          activityData: res
        });
      }
    }).catch(err => {
      console.error('获取运动统计数据失败', err);
    });
  },

  /**
   * 编辑用户信息
   */
  editUserInfo: function() {
    wx.navigateTo({
      url: '/pages/editProfile/editProfile',
    });
  },

  /**
   * 跳转到我的运动页面
   */
  goToMyActivity: function() {
    wx.navigateTo({
      url: '/pages/myActivity/myActivity',
    });
  },

  /**
   * 跳转到我的成就页面
   */
  goToAchievements: function() {
    wx.navigateTo({
      url: '/pages/achievements/achievements',
    });
  },

  /**
   * 跳转到设置页面
   */
  goToSettings: function() {
    wx.navigateTo({
      url: '/pages/settings/settings',
    });
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    // 可能从编辑页面返回，需要刷新数据
    this.loadUserInfo();
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: `查看${this.data.userInfo.name}的运动档案`,
      path: '/pages/profile/profile'
    }
  }
}) 