/**
 * 环境配置文件
 * 支持开发环境和生产环境切换
 */

// 当前环境，可选值：development, production
const ENV = 'development';

// 环境配置
const envConfig = {
  development: {
    apiBaseUrl: 'http://127.0.0.1:5000',
    enableLog: true,
    mockData: true,
    version: '1.0.0-dev',
    // 添加阿里云百炼API配置
    AI_API_KEY: 'sk-93132de1224a4d4689d535c19efd47a6',
    AI_MODEL_ENDPOINT: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
  },
  production: {
    apiBaseUrl: 'https://www.halocc.ggff.net',
    enableLog: false,
    mockData: false,
    version: '1.0.0',
    // 添加阿里云百炼API配置
    AI_API_KEY: '',
    AI_MODEL_ENDPOINT: ''
  }
};

// 当前环境配置
const currentConfig = envConfig[ENV];

// 切换环境方法
const switchEnv = (env) => {
  if (env !== 'development' && env !== 'production') {
    console.error('环境参数错误，只能为development或production');
    return false;
  }
  
  // 这里只是示例，实际小程序中不能直接修改文件
  // 可以通过本地存储实现环境切换
  wx.setStorageSync('ENV', env);
  console.log(`已切换到${env}环境，重启小程序后生效`);
  return true;
};

// 获取当前环境
const getEnv = () => {
  return wx.getStorageSync('ENV') || ENV;
};

// 根据本地存储获取实际配置
const getConfig = () => {
  const currentEnv = getEnv();
  return envConfig[currentEnv];
};

module.exports = {
  ENV,
  config: currentConfig,
  getConfig,
  switchEnv,
  getEnv
}; 