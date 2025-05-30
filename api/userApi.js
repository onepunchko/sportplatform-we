/**
 * 用户相关API
 */
const { request } = require('./request');

/**
 * 账号密码登录
 * @param {Object} data 登录参数
 * @returns {Promise} Promise对象
 */
const login = (data) => {
  return request('/user/login', data);
};

/**
 * 微信登录
 * @param {Object} data 包含微信code的对象
 * @returns {Promise} Promise对象
 */
const wxLogin = (data) => {
  return request('/user/wx-login', data);
};

/**
 * 更新用户手机号
 * @param {Object} data 包含加密数据的对象
 * @returns {Promise} Promise对象
 */
const updatePhone = (data) => {
  return request('/user/update-phone', data);
};

/**
 * 获取用户信息
 * @returns {Promise} Promise对象
 */
const getUserInfo = () => {
  return request('/user/info', {});
};

/**
 * 更新用户信息
 * @param {Object} data 用户信息
 * @returns {Promise} Promise对象
 */
const updateUserInfo = (data) => {
  return request('/user/update', data);
};

/**
 * 获取用户运动统计数据
 * @returns {Promise} Promise对象
 */
const getSportStats = () => {
  return request('/user/sport/stats', {});
};

/**
 * 手动绑定手机号
 * @param {Object} data 手机号和验证码
 * @returns {Promise} Promise对象
 */
const bindPhone = (data) => {
  return request('/user/bind-phone', data);
};

/**
 * 发送短信验证码
 * @param {Object} data 手机号
 * @returns {Promise} Promise对象
 */
const sendSmsCode = (data) => {
  return request('/user/send-sms', data);
};

// 导出
module.exports = {
  login,
  wxLogin,
  updatePhone,
  getUserInfo,
  updateUserInfo,
  getSportStats,
  bindPhone,
  sendSmsCode
}; 