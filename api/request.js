/**
 * 通用请求函数
 * 处理后端API返回值
 */

// 导入环境配置
const { getConfig } = require('../config/env');

// 获取当前环境下的服务器接口地址
const getBaseUrl = () => {
  const config = getConfig();
  return config.apiBaseUrl;
};

/**
 * 请求服务器函数
 * @param {String} url 接口地址
 * @param {Object} data 请求参数
 * @param {String} method 请求方式，默认POST
 * @returns {Promise} Promise对象
 */
const request = (url, data = {}, method = 'POST') => {
  return new Promise((resolve, reject) => {
    // 获取存储的token
    const token = wx.getStorageSync('token') || '';
    // 获取当前环境下的BASE_URL
    const BASE_URL = getBaseUrl();
    
    // 日志输出
    const config = getConfig();
    if (config.enableLog) {
      console.log(`[API请求] ${method} ${BASE_URL + url}`, data);
    }
    
    wx.request({
      url: BASE_URL + url,
      data,
      method,
      header: {
        'content-type': 'application/json',
        'auth': token,
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        const { error, body, message } = res.data;
        
        // 日志输出
        if (config.enableLog) {
          console.log(`[API响应] ${BASE_URL + url}`, res.data);
        }
        
        // 处理不同错误码
        if (error === 0) {
          // 成功
          resolve(body);
        } else if (error === 401) {
          // 未登录，需要登录
          wx.showToast({
            title: '请先登录',
            icon: 'none'
          });
          // 跳转到登录页
          setTimeout(() => {
            wx.navigateTo({
              url: '/pages/login/login'
            });
          }, 1500);
          reject(new Error('请先登录'));
        } else if (error === 500) {
          // 系统异常
          wx.showToast({
            title: '系统异常，请稍后再试',
            icon: 'none'
          });
          reject(new Error('系统异常'));
        } else {
          // 其他业务异常
          wx.showToast({
            title: message || '请求失败',
            icon: 'none'
          });
          reject(new Error(message || '请求失败'));
        }
      },
      fail: (err) => {
        // 日志输出
        if (config.enableLog) {
          console.error(`[API错误] ${BASE_URL + url}`, err);
        }
        
        wx.showToast({
          title: '网络异常，请检查网络连接',
          icon: 'none'
        });
        reject(new Error('网络异常'));
      }
    });
  });
};

// 导出
module.exports = {
  request
}; 