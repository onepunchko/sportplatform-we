/**
 * 场地预约相关API
 */
const { request } = require('./request');
const { getConfig } = require('../config/env');

// 本地存储的键名
const STORAGE_KEYS = {
  MY_RESERVATIONS: 'my_reservations'
};

/**
 * 从本地存储获取我的预约数据
 */
function getLocalReservations() {
  return wx.getStorageSync(STORAGE_KEYS.MY_RESERVATIONS) || [];
}

/**
 * 保存预约数据到本地存储
 */
function saveLocalReservations(reservations) {
  wx.setStorageSync(STORAGE_KEYS.MY_RESERVATIONS, reservations);
}

/**
 * 获取场馆列表
 * @param {Object} params - 请求参数
 * @param {string} params.type - 场馆类型
 * @param {string} params.date - 日期，格式：YYYY-MM-DD
 * @param {boolean} params.available - 是否只查询有空闲时段的场馆
 * @returns {Promise}
 */
function getVenueList(params = {}) {
  // 检查是否使用模拟数据
  const config = getConfig();
  if (config.mockData) {
    console.log('使用模拟数据：场馆列表');
    return new Promise(resolve => {
      // 模拟延迟
      setTimeout(() => {
        // 根据类型过滤场馆
        let venues = getMockVenues();
        if (params.type && params.type !== 'all') {
          venues = venues.filter(venue => venue.type === params.type);
        }
        resolve({
          list: venues,
          total: venues.length
        });
      }, 500);
    });
  }
  
  // 正常API请求
  return request({
    url: '/api/venue/list',
    method: 'POST',
    data: params
  });
}

/**
 * 获取场馆详情
 * @param {Object} params - 请求参数
 * @param {number} params.id - 场馆ID
 * @returns {Promise}
 */
function getVenueDetail(params) {
  // 检查是否使用模拟数据
  const config = getConfig();
  if (config.mockData) {
    console.log('使用模拟数据：场馆详情');
    return new Promise(resolve => {
      // 模拟延迟
      setTimeout(() => {
        const venues = getMockVenues();
        const venue = venues.find(v => v.id === params.id) || venues[0];
        resolve(venue);
      }, 500);
    });
  }
  
  // 正常API请求
  return request({
    url: '/api/venue/detail',
    method: 'POST',
    data: params
  });
}

/**
 * 获取场馆时间段
 * @param {Object} params - 请求参数
 * @param {number} params.venueId - 场馆ID
 * @param {string} params.date - 日期，格式：YYYY-MM-DD
 * @returns {Promise}
 */
function getVenueTimeslots(params) {
  // 检查是否使用模拟数据
  const config = getConfig();
  if (config.mockData) {
    console.log('使用模拟数据：场馆时间段');
    return new Promise(resolve => {
      // 模拟延迟
      setTimeout(() => {
        resolve({
          venueId: params.venueId,
          date: params.date,
          timeSlots: getMockTimeSlots()
        });
      }, 500);
    });
  }
  
  // 正常API请求
  return request({
    url: '/api/venue/timeslots',
    method: 'POST',
    data: params
  });
}

/**
 * 预约场馆
 * @param {Object} params - 请求参数
 * @param {number} params.venueId - 场馆ID
 * @param {string} params.date - 日期，格式：YYYY-MM-DD
 * @param {number} params.timeSlotId - 时间段ID
 * @param {number} params.participants - 参与人数
 * @param {string} params.remark - 备注
 * @returns {Promise}
 */
function reserveVenue(params) {
  // 检查是否使用模拟数据
  const config = getConfig();
  if (config.mockData) {
    console.log('使用模拟数据：场馆预约');
    return new Promise(resolve => {
      // 模拟延迟
      setTimeout(() => {
        // 生成预约ID
        const reservationId = Math.floor(Math.random() * 1000) + 1000;
        
        // 获取场馆信息
        const venues = getMockVenues();
        const venue = venues.find(v => v.id === params.venueId);
        
        // 获取时段信息
        const timeSlots = getMockTimeSlots();
        const timeSlot = timeSlots.find(t => t.id === params.timeSlotId);
        
        // 如果找到场馆和时段，创建预约记录
        if (venue && timeSlot) {
          // 获取现有预约列表
          const reservations = getLocalReservations();
          
          // 创建新预约
          const newReservation = {
            id: reservationId,
            venue_id: venue.id,
            venue_name: venue.name,
            venue_type: venue.type,
            venue_image: venue.image,
            date: params.date,
            start_time: timeSlot.startTime,
            end_time: timeSlot.endTime,
            status: 'confirmed',
            price: timeSlot.price,
            participants: params.participants,
            remark: params.remark,
            created_at: formatDate(new Date()) + ' ' + new Date().toTimeString().substring(0, 5)
          };
          
          // 添加到列表
          reservations.push(newReservation);
          
          // 保存到本地存储
          saveLocalReservations(reservations);
        }
        
        resolve({
          reservationId: reservationId,
          success: true
        });
      }, 500);
    });
  }
  
  // 正常API请求
  return request({
    url: '/api/venue/reserve',
    method: 'POST',
    data: params
  });
}

/**
 * 获取我的预约列表
 * @returns {Promise}
 */
function getMyReservations() {
  // 检查是否使用模拟数据
  const config = getConfig();
  if (config.mockData) {
    console.log('使用模拟数据：我的预约');
    return new Promise(resolve => {
      // 模拟延迟
      setTimeout(() => {
        // 从本地存储获取预约数据
        let reservations = getLocalReservations();
        
        // 如果没有预约记录，使用默认的模拟数据
        if (reservations.length === 0) {
          reservations = getMockReservations();
          // 保存到本地存储
          saveLocalReservations(reservations);
        }
        
        // 按创建时间倒序排序
        reservations.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        resolve({
          reservations: reservations
        });
      }, 500);
    });
  }
  
  // 正常API请求
  return request({
    url: '/api/venue/my-reservations',
    method: 'POST'
  });
}

/**
 * 取消预约
 * @param {Object} params - 请求参数
 * @param {number} params.id - 预约ID
 * @returns {Promise}
 */
function cancelReservation(params) {
  // 检查是否使用模拟数据
  const config = getConfig();
  if (config.mockData) {
    console.log('使用模拟数据：取消预约');
    return new Promise(resolve => {
      // 模拟延迟
      setTimeout(() => {
        // 从本地存储获取预约数据
        const reservations = getLocalReservations();
        
        // 查找并移除指定ID的预约
        const updatedReservations = reservations.filter(reservation => reservation.id !== params.id);
        
        // 保存到本地存储
        saveLocalReservations(updatedReservations);
        
        resolve({
          success: true
        });
      }, 500);
    });
  }
  
  // 正常API请求
  return request({
    url: '/api/venue/cancel',
    method: 'POST',
    data: params
  });
}

/**
 * 获取模拟场馆数据
 */
function getMockVenues() {
  return [
    {
      id: 1,
      name: '西区篮球场',
      type: 'basketball',
      image: '/static/images/venues/basketball-court.jpg',
      distance: '500米',
      rating: 4.8,
      reviews: 125,
      price: 15,
      open: true,
      address: '大学西区体育中心',
      description: '标准篮球场，设有6个全场，灯光照明良好，场地平整。',
      facilities: ['更衣室', '饮水机', '休息区', '计分牌'],
      rules: ['禁止穿硬底鞋', '禁止携带食物入场', '爱护场地设施']
    },
    {
      id: 2,
      name: '中心羽毛球馆',
      type: 'badminton',
      image: '/static/images/venues/badminton-court.jpg',
      distance: '800米',
      rating: 4.6,
      reviews: 98,
      price: 20,
      open: true,
      address: '大学中心体育馆',
      description: '室内羽毛球场，木质地板，共8片场地，空调环境。',
      facilities: ['空调', '更衣室', '淋浴', '休息区', '饮水机'],
      rules: ['必须穿专业羽毛球鞋', '保持场地清洁', '遵守预约时间']
    },
    {
      id: 3,
      name: '东区乒乓球室',
      type: 'pingpong',
      image: '/static/images/venues/pingpong-room.jpg',
      distance: '1.2公里',
      rating: 4.5,
      reviews: 87,
      price: 10,
      open: true,
      address: '大学东区学生活动中心',
      description: '室内乒乓球室，配有12张标准球桌，照明充足。',
      facilities: ['空调', '休息区', '饮水机', '更衣室'],
      rules: ['禁止使用有色胶皮', '轻拿轻放球桌设备', '保持安静']
    },
    {
      id: 4,
      name: '北区足球场',
      type: 'football',
      image: '/static/images/venues/football-field.jpg',
      distance: '1.5公里',
      rating: 4.7,
      reviews: 105,
      price: 25,
      open: true,
      address: '大学北区运动场',
      description: '标准11人制足球场，人造草皮，设有夜间照明系统。',
      facilities: ['更衣室', '淋浴', '休息区', '观众席'],
      rules: ['禁止穿钉鞋', '爱护场地设施', '遵守安全规则']
    },
    {
      id: 5,
      name: '游泳馆',
      type: 'swimming',
      image: '/static/images/venues/swimming-pool.jpg',
      distance: '2.0公里',
      rating: 4.9,
      reviews: 156,
      price: 30,
      open: true,
      address: '大学游泳馆',
      description: '标准50米游泳池，室内恒温，水质定期检测。',
      facilities: ['更衣室', '淋浴', '储物柜', '休息区'],
      rules: ['必须穿泳帽', '禁止携带食物', '遵守泳道规则']
    }
  ];
}

/**
 * 获取模拟时间段数据
 */
function getMockTimeSlots() {
  return [
    { id: 1, startTime: '08:00', endTime: '10:00', available: true, price: 15 },
    { id: 2, startTime: '10:00', endTime: '12:00', available: false, price: 15 },
    { id: 3, startTime: '14:00', endTime: '16:00', available: true, price: 15 },
    { id: 4, startTime: '16:00', endTime: '18:00', available: true, price: 20 },
    { id: 5, startTime: '18:00', endTime: '20:00', available: false, price: 20 },
    { id: 6, startTime: '20:00', endTime: '22:00', available: true, price: 20 }
  ];
}

/**
 * 获取模拟预约数据
 */
function getMockReservations() {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const nextWeek = new Date(today);
  nextWeek.setDate(nextWeek.getDate() + 7);
  
  return [
    {
      id: 101,
      venue_id: 1,
      venue_name: '西区篮球场',
      venue_type: '篮球场',
      venue_image: '/static/images/venues/basketball-court.jpg',
      date: formatDate(tomorrow),
      start_time: '18:00',
      end_time: '20:00',
      status: 'confirmed',
      created_at: formatDate(today) + ' 10:30'
    },
    {
      id: 102,
      venue_id: 2,
      venue_name: '中心羽毛球馆',
      venue_type: '羽毛球馆',
      venue_image: '/static/images/venues/badminton-court.jpg',
      date: formatDate(nextWeek),
      start_time: '14:00',
      end_time: '16:00',
      status: 'confirmed',
      created_at: formatDate(today) + ' 09:15'
    }
  ];
}

/**
 * 格式化日期为 YYYY-MM-DD
 */
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

module.exports = {
  getVenueList,
  getVenueDetail,
  getVenueTimeslots,
  reserveVenue,
  getMyReservations,
  cancelReservation
}; 