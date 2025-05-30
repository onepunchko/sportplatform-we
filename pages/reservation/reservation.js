const { getVenueList, getVenueDetail, reserveVenue, getMyReservations, cancelReservation } = require('../../api/reservationApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    selectedVenueType: 'all',
    venues: [
      {
        id: 1,
        name: '西区篮球场',
        image: '/static/images/venues/basketball-court.jpg',
        distance: '500米',
        rating: 4.8,
        reviews: 125,
        price: 15,
        open: true
      },
      {
        id: 2,
        name: '中心羽毛球馆',
        image: '/static/images/venues/badminton-court.jpg',
        distance: '800米',
        rating: 4.6,
        reviews: 98,
        price: 20,
        open: true
      }
    ],
    myReservations: [],
    showMyReservationsPopup: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.loadVenueList();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    // 刷新场馆列表
    this.loadVenueList();
    
    // 预加载我的预约数据，但不显示弹窗
    this.preloadMyReservations();
  },

  /**
   * 加载场地列表
   */
  loadVenueList: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    // 调用API获取场地列表
    getVenueList({
      type: this.data.selectedVenueType === 'all' ? '' : this.data.selectedVenueType
    }).then(res => {
      console.log('获取场地列表成功', res);
      if (res && res.list) {
        this.setData({
          venues: res.list
        });
      }
    }).catch(err => {
      console.error('获取场地列表失败', err);
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 选择场地类型
   */
  selectVenueType: function(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      selectedVenueType: type
    });
    
    // 重新加载场地列表
    this.loadVenueList();
  },

  /**
   * 进入场地详情
   */
  goToVenueDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/venue-detail/venue-detail?id=${id}`,
    });
  },
  
  /**
   * 前往搜索页面
   */
  goToSearch: function() {
    wx.navigateTo({
      url: '/pages/venue-search/venue-search',
    });
  },

  /**
   * 预加载我的预约数据
   */
  preloadMyReservations: function() {
    // 悄悄获取我的预约数据，不显示加载提示
    getMyReservations().then(res => {
      console.log('预加载我的预约成功', res);
      this.setData({
        myReservations: res.reservations || []
      });
    }).catch(err => {
      console.error('预加载我的预约失败', err);
    });
  },

  /**
   * 显示我的预约弹窗
   */
  showMyReservations: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    // 获取我的预约数据
    getMyReservations().then(res => {
      console.log('获取我的预约成功', res);
      
      // 先显示弹窗，再设置数据，避免闪烁
      this.setData({
        showMyReservationsPopup: true
      });
      
      // 稍微延迟一下设置数据，让动画效果更流畅
      setTimeout(() => {
        this.setData({
          myReservations: res.reservations || []
        });
      }, 100);
    }).catch(err => {
      console.error('获取我的预约失败', err);
      wx.showToast({
        title: '获取预约信息失败',
        icon: 'none'
      });
    }).finally(() => {
      wx.hideLoading();
    });
  },
  
  /**
   * 隐藏我的预约弹窗
   */
  hideMyReservations: function() {
    this.setData({
      showMyReservationsPopup: false
    });
  },
  
  /**
   * 取消预约
   */
  cancelReservation: function(e) {
    const id = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '取消预约',
      content: '确定要取消此预约吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({
            title: '处理中',
          });
          
          cancelReservation({
            id: id
          }).then(res => {
            console.log('取消预约成功', res);
            
            // 取消成功后直接从列表中删除该预约
            const updatedReservations = this.data.myReservations.filter(item => item.id !== id);
            
            // 使用动画效果更新UI
            wx.showToast({
              title: '取消成功',
              icon: 'success',
              duration: 1500
            });
            
            // 设置短暂延迟更新列表，让用户看到取消成功的提示
            setTimeout(() => {
              this.setData({
                myReservations: updatedReservations
              });
            }, 300);
            
          }).catch(err => {
            console.error('取消预约失败', err);
            wx.showToast({
              title: '取消失败，请重试',
              icon: 'none'
            });
          }).finally(() => {
            wx.hideLoading();
          });
        }
      }
    });
  }
}) 