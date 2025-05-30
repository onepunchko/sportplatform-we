const { getVenueDetail, getVenueTimeslots, reserveVenue } = require('../../api/reservationApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    venueId: null,
    venue: {},
    dateList: [],
    selectedDateIndex: 0,
    selectedDate: '',
    timeSlots: [],
    morningSlots: [],   // 上午时段 (6:00-12:00)
    afternoonSlots: [], // 下午时段 (12:00-18:00)
    eveningSlots: [],   // 晚上时段 (18:00-24:00)
    selectedTimeSlotId: null,
    canReserve: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    if (options.id) {
      this.setData({
        venueId: parseInt(options.id)
      });
      
      // 加载场馆详情
      this.loadVenueDetail();
      
      // 生成未来7天的日期列表
      this.generateDateList();
    } else {
      wx.showToast({
        title: '参数错误',
        icon: 'none'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  /**
   * 加载场馆详情
   */
  loadVenueDetail: function () {
    wx.showLoading({
      title: '加载中',
    });
    
    getVenueDetail({ id: this.data.venueId }).then(res => {
      console.log('获取场馆详情成功', res);
      
      this.setData({
        venue: res
      });
      
      // 加载可用时段
      this.loadTimeSlots();
    }).catch(err => {
      console.error('获取场馆详情失败', err);
      wx.showToast({
        title: '获取场馆详情失败',
        icon: 'none'
      });
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 生成日期列表
   */
  generateDateList: function () {
    const today = new Date();
    const dateList = [];
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() + i);
      
      const month = date.getMonth() + 1;
      const day = date.getDate();
      const weekday = weekdays[date.getDay()];
      
      dateList.push({
        date: `${month}/${day}`,
        day: i === 0 ? '今天' : weekday,
        fullDate: this.formatDate(date)
      });
    }
    
    this.setData({
      dateList: dateList,
      selectedDate: dateList[0].fullDate
    });
  },

  /**
   * 格式化日期为YYYY-MM-DD
   */
  formatDate: function (date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  /**
   * 加载可用时段
   */
  loadTimeSlots: function () {
    wx.showLoading({
      title: '加载中',
    });
    
    getVenueTimeslots({
      venueId: this.data.venueId,
      date: this.data.selectedDate
    }).then(res => {
      console.log('获取时段成功', res);
      
      const timeSlots = res.timeSlots || [];
      
      // 按时间段分类
      this.categorizeTimeSlots(timeSlots);
      
      this.setData({
        timeSlots: timeSlots,
        selectedTimeSlotId: null,
        canReserve: false
      });
    }).catch(err => {
      console.error('获取时段失败', err);
      wx.showToast({
        title: '获取可用时段失败',
        icon: 'none'
      });
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 按时间段分类
   */
  categorizeTimeSlots: function (timeSlots) {
    const morningSlots = [];
    const afternoonSlots = [];
    const eveningSlots = [];
    
    timeSlots.forEach(slot => {
      // 提取小时数
      const startHour = parseInt(slot.startTime.split(':')[0]);
      
      if (startHour >= 6 && startHour < 12) {
        morningSlots.push(slot);
      } else if (startHour >= 12 && startHour < 18) {
        afternoonSlots.push(slot);
      } else {
        eveningSlots.push(slot);
      }
    });
    
    this.setData({
      morningSlots: morningSlots,
      afternoonSlots: afternoonSlots,
      eveningSlots: eveningSlots
    });
  },

  /**
   * 选择日期
   */
  selectDate: function (e) {
    const index = e.currentTarget.dataset.index;
    const selectedDate = this.data.dateList[index].fullDate;
    
    this.setData({
      selectedDateIndex: index,
      selectedDate: selectedDate,
      selectedTimeSlotId: null,
      canReserve: false
    });
    
    // 加载所选日期的时段
    this.loadTimeSlots();
  },

  /**
   * 选择时段
   */
  selectTimeSlot: function (e) {
    const id = e.currentTarget.dataset.id;
    const available = e.currentTarget.dataset.available;
    
    // 只能选择可用的时段
    if (!available) {
      return;
    }
    
    this.setData({
      selectedTimeSlotId: id,
      canReserve: true
    });
  },

  /**
   * 预约场地
   */
  reserve: function () {
    if (!this.data.canReserve) {
      return;
    }
    
    wx.showLoading({
      title: '预约中',
    });
    
    reserveVenue({
      venueId: this.data.venueId,
      date: this.data.selectedDate,
      timeSlotId: this.data.selectedTimeSlotId,
      participants: 1, // 默认人数
      remark: '' // 默认备注
    }).then(res => {
      console.log('预约成功', res);
      
      wx.showToast({
        title: '预约成功',
        icon: 'success'
      });
      
      // 跳转到我的预约页面或者留在当前页面
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }).catch(err => {
      console.error('预约失败', err);
      wx.showToast({
        title: '预约失败，请重试',
        icon: 'none'
      });
    }).finally(() => {
      wx.hideLoading();
    });
  }
}) 