/**
 * AI教练相关API
 */
const { request } = require('./request');
const { getConfig } = require('../config/env');

/**
 * 获取AI教练回复
 * @param {Object} data 用户消息
 * @returns {Promise}
 */
const getAiReply = (data = {}) => {
  return request('/ai/coach/reply', data);
};

/**
 * 获取聊天历史记录
 * @returns {Promise}
 */
const getChatHistory = () => {
  return request('/ai/coach/history', {});
};

/**
 * 获取AI推荐的运动计划
 * @param {Object} data 用户条件
 * @returns {Promise}
 */
const getAiSportPlan = (data = {}) => {
  return request('/ai/coach/plan', data);
};

/**
 * 直接调用阿里云百炼(Qwen)API - 符合OpenAI兼容模式格式
 * @param {String} prompt 用户提问
 * @param {Array} history 历史对话
 * @returns {Promise}
 */
const callQwenAPI = (prompt, history = []) => {
  const config = getConfig();
  const apiKey = config.AI_API_KEY;
  const modelEndpoint = config.AI_MODEL_ENDPOINT;
  
  if (!apiKey || !modelEndpoint) {
    return Promise.reject(new Error('AI API配置不完整'));
  }
  
  return new Promise((resolve, reject) => {
    // 构建请求参数
    const requestData = {
      model: 'qwen3-8b', // 更新为正确的模型名称
      messages: history.length > 0 ? history : [
        { role: 'system', content: '你是一个专业的运动教练。' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      top_p: 0.8,
      max_tokens: 1500,
      stream: true // 必须设置为true，该模型只支持流式输出
    };
    
    // 创建一个变量收集完整回复
    let fullContent = '';
    let isCompletionDone = false;
    
    // 使用wx.request发起请求
    const requestTask = wx.request({
      url: modelEndpoint,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'Accept': 'text/event-stream' // 添加流式响应的Accept头
      },
      data: requestData,
      enableChunked: true, // 启用分块接收
      responseType: 'text', // 使用文本响应类型
      success: (res) => {
        // 请求成功但可能存在错误
        if (res.statusCode !== 200) {
          reject(new Error(`状态码错误: ${res.statusCode}, 信息: ${JSON.stringify(res.data)}`));
        }
      },
      fail: (err) => {
        reject(err);
      },
      complete: () => {
        // 确保在所有数据接收完成后返回
        if (!isCompletionDone) {
          isCompletionDone = true;
          if (fullContent) {
            resolve({
              text: fullContent,
              choices: [{
                message: {
                  content: fullContent
                }
              }]
            });
          } else {
            reject(new Error('未收到有效回复'));
          }
        }
      }
    });
    
    // 接收数据块
    requestTask.onChunkReceived((response) => {
      try {
        // 将ArrayBuffer转换为字符串
        const decoder = new TextDecoder('utf-8');
        const chunk = decoder.decode(response.data);
        
        // 解析SSE格式的响应
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6).trim();
            
            // 处理完成标记
            if (jsonStr === '[DONE]') {
              if (!isCompletionDone) {
                isCompletionDone = true;
                resolve({
                  text: fullContent,
                  choices: [{
                    message: {
                      content: fullContent
                    }
                  }]
                });
              }
              continue;
            }
            
            // 解析JSON数据
            try {
              const data = JSON.parse(jsonStr);
              if (data.choices && data.choices.length > 0 && 
                  data.choices[0].delta && data.choices[0].delta.content) {
                const contentChunk = data.choices[0].delta.content;
                fullContent += contentChunk;
                
                // 调用全局回调函数进行实时UI更新
                if (typeof wx.aiCoachStreamCallback === 'function') {
                  wx.aiCoachStreamCallback(contentChunk);
                }
              }
            } catch (e) {
              console.error('JSON解析错误:', e, jsonStr);
            }
          }
        }
      } catch (error) {
        console.error('处理数据块错误:', error);
      }
    });
  });
};

module.exports = {
  getAiReply,
  getChatHistory,
  getAiSportPlan,
  callQwenAPI
}; 