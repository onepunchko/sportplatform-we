// pages/record/record.js

Page({
  /**
   * 页面的初始数据
   */
  data: {
    sportType: '', // 运动类型：'run', 'walk', 'cycle', 'other'
    sportTypeName: '', // 运动类型名称：'跑步', '健走', '骑行', '其他'
    startTime: 0, // 开始时间戳
    currentTime: 0, // 当前时间戳
    timerDisplay: '00:00:00', // 计时器显示
    isPaused: false, // 是否暂停
    pausedTime: 0, // 暂停时间
    
    // 位置相关
    location: {
      latitude: 39.908823, // 默认纬度
      longitude: 116.397470 // 默认经度
    },
    markers: [], // 地图标记点
    polyline: [{ // 轨迹线
      points: [],
      color: '#3399FF',
      width: 5,
      arrowLine: true
    }],
    
    // 运动数据
    distance: '0.00', // 距离（公里）
    pace: '0:00', // 配速（分钟/公里）
    calories: '0', // 消耗卡路里
    
    // 记录轨迹点
    trackPoints: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    // 获取运动类型
    const sportType = options.type || 'run';
    const sportTypeNameMap = {
      'run': '跑步',
      'walk': '健走',
      'cycle': '骑行',
      'other': '其他运动'
    };
    
    this.setData({
      sportType: sportType,
      sportTypeName: sportTypeNameMap[sportType]
    });
    
    // 获取当前位置
    this.getCurrentLocation();
    
    // 开始计时和记录轨迹
    this.startTracking();
  },

  /**
   * 获取当前位置
   */
  getCurrentLocation: function () {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        const latitude = res.latitude;
        const longitude = res.longitude;
        
        // 更新位置信息
        this.setData({
          location: {
            latitude: latitude,
            longitude: longitude
          },
          markers: [{
            id: 0,
            latitude: latitude,
            longitude: longitude,
            width: 20,
            height: 20,
            callout: {
              content: '起点',
              color: '#ffffff',
              fontSize: 12,
              borderRadius: 4,
              bgColor: '#3399FF',
              padding: 6,
              display: 'ALWAYS'
            }
          }],
          'polyline[0].points': [{
            latitude: latitude,
            longitude: longitude
          }],
          trackPoints: [{
            latitude: latitude,
            longitude: longitude,
            timestamp: Date.now()
          }]
        });
      },
      fail: (err) => {
        console.error('获取位置失败', err);
        wx.showToast({
          title: '获取位置失败，请检查位置权限',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 开始记录
   */
  startTracking: function () {
    const now = Date.now();
    this.setData({
      startTime: now,
      currentTime: now
    });
    
    // 启动计时器
    this.timer = setInterval(() => {
      if (!this.data.isPaused) {
        const currentTime = Date.now();
        this.setData({
          currentTime: currentTime
        });
        this.updateTimerDisplay();
      }
    }, 1000);
    
    // 启动位置记录
    this.startLocationTracking();
  },

  /**
   * 更新计时器显示
   */
  updateTimerDisplay: function () {
    const duration = this.data.currentTime - this.data.startTime - this.data.pausedTime;
    
    const hours = Math.floor(duration / 3600000);
    const minutes = Math.floor((duration % 3600000) / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    
    const timerDisplay = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    this.setData({
      timerDisplay: timerDisplay
    });
  },

  /**
   * 开始位置追踪
   */
  startLocationTracking: function () {
    // 设置位置监听
    this.locationUpdateInterval = setInterval(() => {
      if (!this.data.isPaused) {
        wx.getLocation({
          type: 'gcj02',
          success: (res) => {
            const latitude = res.latitude;
            const longitude = res.longitude;
            
            // 更新位置信息
            this.updateTrackPoint(latitude, longitude);
          },
          fail: (err) => {
            console.error('获取位置失败', err);
          }
        });
      }
    }, 5000); // 每5秒更新一次位置
  },

  /**
   * 更新轨迹点
   */
  updateTrackPoint: function (latitude, longitude) {
    const trackPoints = this.data.trackPoints;
    const polylinePoints = this.data.polyline[0].points;
    
    // 添加新的轨迹点
    const newTrackPoint = {
      latitude: latitude,
      longitude: longitude,
      timestamp: Date.now()
    };
    
    trackPoints.push(newTrackPoint);
    polylinePoints.push({
      latitude: latitude,
      longitude: longitude
    });
    
    // 更新轨迹线和轨迹点
    this.setData({
      'polyline[0].points': polylinePoints,
      trackPoints: trackPoints,
      location: {
        latitude: latitude,
        longitude: longitude
      }
    });
    
    // 计算距离
    this.calculateDistance();
  },

  /**
   * 计算距离
   */
  calculateDistance: function () {
    const trackPoints = this.data.trackPoints;
    if (trackPoints.length < 2) {
      return;
    }
    
    // 计算总距离
    let totalDistance = 0;
    for (let i = 1; i < trackPoints.length; i++) {
      const start = trackPoints[i - 1];
      const end = trackPoints[i];
      totalDistance += this.getDistance(start.latitude, start.longitude, end.latitude, end.longitude);
    }
    
    // 更新距离（转为公里，保留两位小数）
    const distanceKm = (totalDistance / 1000).toFixed(2);
    
    // 计算配速（分钟/公里）
    const duration = this.data.currentTime - this.data.startTime - this.data.pausedTime;
    const durationMinutes = duration / 60000;
    
    let pace = '0:00';
    if (distanceKm > 0) {
      const paceValue = durationMinutes / parseFloat(distanceKm);
      const paceMinutes = Math.floor(paceValue);
      const paceSeconds = Math.floor((paceValue - paceMinutes) * 60);
      pace = `${paceMinutes}:${paceSeconds.toString().padStart(2, '0')}`;
    }
    
    // 计算卡路里（粗略估算，根据运动类型和时长）
    let caloriesPerHour = 0;
    switch (this.data.sportType) {
      case 'run':
        caloriesPerHour = 600; // 跑步约600卡/小时
        break;
      case 'walk':
        caloriesPerHour = 300; // 健走约300卡/小时
        break;
      case 'cycle':
        caloriesPerHour = 500; // 骑行约500卡/小时
        break;
      default:
        caloriesPerHour = 400; // 默认400卡/小时
    }
    
    const durationHours = duration / 3600000;
    const calories = Math.round(caloriesPerHour * durationHours);
    
    this.setData({
      distance: distanceKm,
      pace: pace,
      calories: calories
    });
  },

  /**
   * 计算两点之间的距离（Haversine公式）
   */
  getDistance: function (lat1, lon1, lat2, lon2) {
    const R = 6371000; // 地球半径（米）
    const dLat = this.deg2rad(lat2 - lat1);
    const dLon = this.deg2rad(lon2 - lon1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;
    return distance;
  },

  /**
   * 角度转弧度
   */
  deg2rad: function (deg) {
    return deg * (Math.PI / 180);
  },

  /**
   * 暂停记录
   */
  pauseTracking: function () {
    this.setData({
      isPaused: true,
      pauseTime: Date.now()
    });
    
    // 显示提示
    wx.showToast({
      title: '已暂停',
      icon: 'none'
    });
  },

  /**
   * 继续记录
   */
  resumeTracking: function () {
    const pauseDuration = Date.now() - this.data.pauseTime;
    this.setData({
      isPaused: false,
      pausedTime: this.data.pausedTime + pauseDuration
    });
    
    // 显示提示
    wx.showToast({
      title: '已继续',
      icon: 'none'
    });
  },

  /**
   * 结束记录
   */
  endTracking: function () {
    // 显示确认框
    wx.showModal({
      title: '结束运动',
      content: '确定结束当前运动记录吗？',
      success: (res) => {
        if (res.confirm) {
          // 停止计时器和位置更新
          clearInterval(this.timer);
          clearInterval(this.locationUpdateInterval);
          
          // 保存运动记录
          this.saveActivityRecord();
          
          // 返回上一页
          wx.navigateBack();
        }
      }
    });
  },

  /**
   * 保存运动记录
   */
  saveActivityRecord: function () {
    const duration = this.data.currentTime - this.data.startTime - this.data.pausedTime;
    const durationMinutes = Math.round(duration / 60000);
    
    const record = {
      type: this.data.sportType,
      typeName: this.data.sportTypeName,
      startTime: new Date(this.data.startTime).toISOString(),
      endTime: new Date(this.data.currentTime).toISOString(),
      duration: durationMinutes,
      distance: parseFloat(this.data.distance),
      calories: parseInt(this.data.calories),
      trackPoints: this.data.trackPoints
    };
    
    console.log('保存运动记录', record);
    
    // TODO: 调用API保存记录
    wx.showToast({
      title: '记录已保存',
      icon: 'success'
    });
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {
    // 清除计时器
    clearInterval(this.timer);
    clearInterval(this.locationUpdateInterval);
  }
}) 