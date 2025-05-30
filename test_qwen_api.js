// Node.js测试阿里云百炼API
const axios = require('axios');

// 测试配置
const config = {
  apiKey: "sk-93132de1224a4d4689d535c19efd47a6", // 使用config/env.js中的相同API密钥
  modelEndpoint: "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  model: "qwen3-8b"
};

// API请求数据
const requestData = {
  model: config.model,
  messages: [
    { role: 'system', content: '你是一个专业的运动教练。' },
    { role: 'user', content: '你是谁？' }
  ],
  temperature: 0.7,
  top_p: 0.8,
  max_tokens: 1500,
  stream: true // 添加流模式参数
};

// 调用API
async function testQwenAPI() {
  try {
    console.log("发送请求到阿里云百炼API...");
    console.log("请求数据:", JSON.stringify(requestData, null, 2));
    
    const response = await axios({
      method: 'post',
      url: config.modelEndpoint,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`
      },
      data: requestData,
      responseType: 'stream' // 使用流响应类型
    });
    
    console.log("API连接成功，开始接收流数据...");
    
    let fullContent = '';
    
    // 处理流响应
    response.data.on('data', (chunk) => {
      const chunkStr = chunk.toString();
      
      // 流式响应格式为 "data: {JSON数据}\n\n"
      if (chunkStr.startsWith('data: ')) {
        try {
          // 移除 "data: " 前缀并解析JSON
          const jsonStr = chunkStr.replace(/^data: /, '').trim();
          
          // 忽略 [DONE] 消息
          if (jsonStr === '[DONE]') return;
          
          const data = JSON.parse(jsonStr);
          if (data.choices && data.choices.length > 0 && data.choices[0].delta && data.choices[0].delta.content) {
            const content = data.choices[0].delta.content;
            fullContent += content;
            process.stdout.write(content); // 实时输出内容
          }
        } catch (e) {
          console.error('解析流数据出错:', e);
        }
      }
    });
    
    // 处理流结束
    response.data.on('end', () => {
      console.log("\n\n完整回复:");
      console.log(fullContent);
    });
    
    // 处理错误
    response.data.on('error', (err) => {
      console.error('流数据接收错误:', err);
    });
    
  } catch (error) {
    console.error("API调用失败:");
    
    if (error.response) {
      // 服务器响应了，但返回了错误状态码
      console.error("错误状态:", error.response.status);
      console.error("错误头信息:", JSON.stringify(error.response.headers, null, 2));
      console.error("错误数据:", error.response.data);
    } else if (error.request) {
      // 请求已发送，但没有收到响应
      console.error("没有收到响应，请求详情:", error.request);
    } else {
      // 其他错误
      console.error("错误信息:", error.message);
    }
    
    console.error("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code");
  }
}

// 执行测试
testQwenAPI(); 