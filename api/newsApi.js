/**
 * 资讯相关API
 */
const { request } = require('./request');

/**
 * 获取资讯列表
 * @param {Object} data 查询参数
 * @returns {Promise}
 */
const getNewsList = (data = {}) => {
  return request('/news/list', data);
};

/**
 * 获取资讯详情
 * @param {Object} data 资讯ID
 * @returns {Promise}
 */
const getNewsDetail = (data = {}) => {
  return request('/news/detail', data);
};

/**
 * 获取资讯分类
 * @returns {Promise}
 */
const getNewsCategories = () => {
  return request('/news/categories', {});
};

module.exports = {
  getNewsList,
  getNewsDetail,
  getNewsCategories
}; 