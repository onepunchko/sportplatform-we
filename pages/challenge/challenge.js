// pages/challenge/challenge.js
const { getChallengeList, joinChallenge } = require('../../api/sportApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    activeTab: 0,
    // 挑战分类
    categories: [
      { id: 'all', name: '全部', active: true },
      { id: 'personal', name: '个人挑战', active: false },
      { id: 'team', name: '团队挑战', active: false },
      { id: 'school', name: '校园挑战', active: false },
      { id: 'walkRunning', name: '步行跑步', active: false },
      { id: 'ballGames', name: '球类运动', active: false }
    ],
    // 我的挑战
    myChallenges: [
      {
        id: 1,
        title: '30天跑步挑战',
        description: '每天坚持跑步5公里，持续30天',
        image: '/static/images/running_challenge.jpg',
        progress: 60,
        total: 30,
        completed: 18
      }
    ],
    // 热门挑战
    hotChallenges: [
      {
        id: 2,
        title: '校园马拉松',
        description: '参加校园马拉松比赛，完成10公里跑步',
        image: '/static/images/marathon.jpg',
        participants: 1200,
        deadline: '5月30日',
        difficulty: 4
      },
      {
        id: 3,
        title: '每周篮球赛',
        description: '每周参加至少一场篮球比赛，提高篮球技能',
        image: '/static/images/basketball_challenge.jpg',
        participants: 480,
        deadline: '长期',
        difficulty: 3
      },
      {
        id: 4,
        title: '俯卧撑30天挑战',
        description: '每天完成递增数量的俯卧撑，提升上肢力量',
        image: '/static/images/pushup_challenge.jpg',
        participants: 650,
        deadline: '6月15日',
        difficulty: 2
      }
    ],
    // 备份热门挑战数据，用于筛选
    originalHotChallenges: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    // 备份原始数据
    this.setData({
      originalHotChallenges: this.data.hotChallenges
    });
    this.loadChallenges();
  },

  /**
   * 加载挑战列表
   */
  loadChallenges: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    // 模拟API调用，确保示例数据保持不变
    setTimeout(() => {
      wx.hideLoading();
    }, 500);
    
    /* 实际API调用，目前使用本地数据模拟
    // 获取我的挑战
    getChallengeList({type: 'my'}).then(res => {
      if (res && res.length > 0) {
        this.setData({
          myChallenges: res
        });
      }
    }).catch(err => {
      console.error('获取我的挑战失败', err);
    });
    
    // 获取热门挑战
    getChallengeList({type: 'hot'}).then(res => {
      if (res && res.length > 0) {
        this.setData({
          hotChallenges: res,
          originalHotChallenges: res
        });
      }
    }).catch(err => {
      console.error('获取热门挑战失败', err);
    }).finally(() => {
      wx.hideLoading();
    });
    */
  },

  /**
   * 切换标签页
   */
  switchTab: function(e) {
    const index = parseInt(e.currentTarget.dataset.index);
    console.log('切换到标签：', index);
    
    this.setData({
      activeTab: index
    });
    
    // 处理不同标签的加载逻辑
    switch (index) {
      case 0: // 我的挑战
        // 无需特殊处理
        break;
      case 1: // 发现挑战
        this.resetCategories();
        break;
      case 2: // 热门排行
        wx.showToast({
          title: '热门排行功能开发中',
          icon: 'none'
        });
        break;
      case 3: // 挑战攻略
        wx.showToast({
          title: '挑战攻略功能开发中',
          icon: 'none'
        });
        break;
    }
  },
  
  /**
   * 重置分类选择
   */
  resetCategories: function() {
    const categories = this.data.categories.map(item => {
      return {...item, active: item.id === 'all'};
    });
    
    this.setData({
      categories: categories,
      hotChallenges: this.data.originalHotChallenges
    });
  },

  /**
   * 筛选挑战
   */
  filterChallenges: function(e) {
    const id = e.currentTarget.dataset.id;
    console.log('筛选挑战类别：', id);
    
    // 更新激活的类别
    const categories = this.data.categories.map(item => {
      return {...item, active: item.id === id};
    });
    
    this.setData({
      categories: categories
    });
    
    // 模拟筛选
    if (id === 'all') {
      // 恢复原始数据
      this.setData({
        hotChallenges: this.data.originalHotChallenges
      });
    } else {
      // 创建基于类别的筛选逻辑
      let filtered = [];
      
      // 模拟不同类别的筛选结果
      switch(id) {
        case 'personal':
          filtered = this.data.originalHotChallenges.filter(item => 
            item.title.includes('天') || item.description.includes('个人'));
          break;
        case 'team':
          filtered = this.data.originalHotChallenges.filter(item => 
            item.title.includes('赛') || item.participants > 500);
          break;
        case 'school':
          filtered = this.data.originalHotChallenges.filter(item => 
            item.title.includes('校园') || item.description.includes('校园'));
          break;
        case 'walkRunning':
          filtered = this.data.originalHotChallenges.filter(item => 
            item.title.includes('跑步') || item.title.includes('马拉松'));
          break;
        case 'ballGames':
          filtered = this.data.originalHotChallenges.filter(item => 
            item.title.includes('篮球') || item.description.includes('篮球'));
          break;
        default:
          filtered = this.data.originalHotChallenges;
      }
      
      // 确保结果不为空
      if (filtered.length === 0) {
        // 如果筛选结果为空，显示一个随机挑战
        const randomIndex = Math.floor(Math.random() * this.data.originalHotChallenges.length);
        filtered = [this.data.originalHotChallenges[randomIndex]];
      }
      
      this.setData({
        hotChallenges: filtered
      });
    }
    
    /* 实际API调用
    if (id === 'all') {
      this.loadChallenges();
    } else {
      getChallengeList({category: id}).then(res => {
        if (res) {
          this.setData({
            hotChallenges: res
          });
        }
      }).catch(err => {
        console.error('筛选挑战失败', err);
      });
    }
    */
  },

  /**
   * 参加挑战
   */
  joinChallenge: function(e) {
    const challengeId = parseInt(e.currentTarget.dataset.id);
    
    wx.showModal({
      title: '参加挑战',
      content: '确定要参加这个挑战吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({
            title: '加入中',
          });
          
          // 模拟加入成功
          setTimeout(() => {
            wx.hideLoading();
            
            wx.showToast({
              title: '加入成功',
              icon: 'success'
            });
            
            // 将加入的挑战添加到我的挑战中
            const challenge = this.data.hotChallenges.find(item => item.id === challengeId);
            if (challenge) {
              // 将挑战添加到我的挑战列表
              const myChallenge = {
                ...challenge,
                progress: 0,
                total: 30,
                completed: 0
              };
              
              // 检查是否已存在
              const existing = this.data.myChallenges.find(item => item.id === challengeId);
              if (!existing) {
                this.setData({
                  myChallenges: [...this.data.myChallenges, myChallenge]
                });
              }
              
              // 自动切换到我的挑战标签
              setTimeout(() => {
                this.setData({
                  activeTab: 0
                });
              }, 1000);
            }
          }, 1000);
          
          /* 实际API调用
          joinChallenge({challengeId: challengeId}).then(res => {
            wx.showToast({
              title: '加入成功',
              icon: 'success'
            });
            
            // 重新加载挑战列表
            this.loadChallenges();
            
            // 切换到我的挑战标签
            setTimeout(() => {
              this.setData({
                activeTab: 0
              });
            }, 1000);
          }).catch(err => {
            wx.showToast({
              title: '加入失败',
              icon: 'none'
            });
          }).finally(() => {
            wx.hideLoading();
          });
          */
        }
      }
    });
  },

  /**
   * 查看挑战详情
   */
  viewChallengeDetail: function(e) {
    const challengeId = e.currentTarget.dataset.id;
    wx.showToast({
      title: '挑战详情开发中',
      icon: 'none'
    });
    
    /* 实际跳转
    wx.navigateTo({
      url: `/pages/challengeDetail/challengeDetail?id=${challengeId}`,
    });
    */
  },

  /**
   * 创建挑战
   */
  createChallenge: function() {
    wx.showToast({
      title: '创建挑战功能开发中',
      icon: 'none'
    });
    
    /* 实际跳转
    wx.navigateTo({
      url: '/pages/createChallenge/createChallenge',
    });
    */
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    console.log('挑战页面显示');
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: '参加校园运动挑战',
      path: '/pages/challenge/challenge'
    }
  }
}) 