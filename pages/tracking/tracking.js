// pages/tracking/tracking.js
const { getSportTracking, getSportGoal, setSportGoal } = require('../../api/sportApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 今日目标
    goal: {
      progress: 65, // 完成度
      steps: {
        target: 12000,  // 目标步数
        completed: 7800  // 已完成
      },
      distance: {
        target: 5,    // 目标距离（公里）
        completed: 3.2  // 已完成
      },
      calories: {
        target: 400,    // 目标卡路里
        completed: 260  // 已完成
      },
      duration: {
        target: 60,    // 目标时长（分钟）
        completed: 39  // 已完成
      }
    },
    // 本周统计
    weekStats: [
      { day: '周一', value: 6254 },
      { day: '周二', value: 7542 },
      { day: '周三', value: 5124 },
      { day: '周四', value: 8435 },
      { day: '周五', value: 4258 },
      { day: '周六', value: 9125 },
      { day: '周日', value: 4778 }
    ],
    // 最近记录
    recentRecords: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.loadTrackingData();
    this.loadGoalData();
  },

  /**
   * 加载运动追踪数据
   */
  loadTrackingData: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    getSportTracking().then(res => {
      if (res && res.weekStats) {
        this.setData({
          weekStats: res.weekStats
        });
      }
      
      if (res && res.recentRecords) {
        this.setData({
          recentRecords: res.recentRecords
        });
      }
    }).catch(err => {
      console.error('获取运动追踪数据失败', err);
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 加载目标数据
   */
  loadGoalData: function() {
    getSportGoal().then(res => {
      if (res) {
        this.setData({
          goal: res
        });
      }
    }).catch(err => {
      console.error('获取目标数据失败', err);
    });
  },

  /**
   * 设置目标
   */
  setGoal: function(e) {
    const type = e.currentTarget.dataset.type;
    const value = e.detail.value;
    
    const data = {};
    data[type] = {
      target: value
    };
    
    setSportGoal(data).then(res => {
      wx.showToast({
        title: '设置成功',
        icon: 'success'
      });
      
      // 重新加载目标数据
      this.loadGoalData();
    }).catch(err => {
      wx.showToast({
        title: '设置失败',
        icon: 'none'
      });
    });
  },

  /**
   * 开始记录运动
   */
  startTracking: function() {
    wx.showActionSheet({
      itemList: ['跑步', '健走', '骑行', '其他运动'],
      success: (res) => {
        if (!res.cancel) {
          // 根据用户选择的运动类型，跳转到相应的运动记录页面
          const sportType = ['run', 'walk', 'cycle', 'other'][res.tapIndex];
          
          wx.navigateTo({
            url: `/pages/record/record?type=${sportType}`,
            success: () => {
              console.log('跳转到运动记录页面');
            },
            fail: (error) => {
              console.error('跳转失败', error);
              wx.showToast({
                title: '功能开发中',
                icon: 'none'
              });
            }
          });
        }
      },
      fail: (res) => {
        console.log(res.errMsg);
      }
    });
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    this.loadTrackingData();
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: '查看我的运动记录',
      path: '/pages/tracking/tracking'
    }
  }
}) 