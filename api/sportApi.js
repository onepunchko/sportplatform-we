/**
 * 运动相关API
 */
const { request } = require('./request');

/**
 * 获取运动记录列表
 * @param {Object} data 查询参数
 * @returns {Promise}
 */
const getSportList = (data = {}) => {
  return request('/sport/list', data);
};

/**
 * 获取运动追踪数据
 * @returns {Promise}
 */
const getSportTracking = () => {
  return request('/sport/tracking', {});
};

/**
 * 上传运动数据
 * @param {Object} data 运动数据
 * @returns {Promise}
 */
const uploadSportData = (data = {}) => {
  return request('/sport/upload', data);
};

/**
 * 获取运动目标
 * @returns {Promise}
 */
const getSportGoal = () => {
  return request('/sport/goal', {});
};

/**
 * 设置运动目标
 * @param {Object} data 目标数据
 * @returns {Promise}
 */
const setSportGoal = (data = {}) => {
  return request('/sport/goal/set', data);
};

/**
 * 获取运动挑战列表
 * @returns {Promise}
 */
const getChallengeList = () => {
  return request('/sport/challenge/list', {});
};

/**
 * 参加运动挑战
 * @param {Object} data 挑战ID
 * @returns {Promise}
 */
const joinChallenge = (data = {}) => {
  return request('/sport/challenge/join', data);
};

module.exports = {
  getSportList,
  getSportTracking,
  uploadSportData,
  getSportGoal,
  setSportGoal,
  getChallengeList,
  joinChallenge
}; 