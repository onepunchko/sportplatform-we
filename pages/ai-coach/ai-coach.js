// pages/ai-coach/ai-coach.js
const app = getApp();
const { callQwenAPI } = require('../../api/aiCoachApi');
const { getConfig } = require('../../config/env');
const { markdownToHtml } = require('../../utils/markdownParser');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    messages: [],     // 聊天消息列表
    inputValue: '',   // 输入框的值
    isTyping: false,  // AI是否正在输入
    scrollToMessage: '', // 滚动到指定消息的ID
    suggestions: [],  // 建议问题列表
    userInfo: null,   // 用户信息
    chatHistory: []   // 对话历史记录，用于API调用
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 初始化AI教练页面
    this.initAICoach();
  },

  /**
   * 初始化AI教练
   */
  initAICoach() {
    // 获取用户信息
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo
      });
    }

    // 检查API配置
    const config = getConfig();
    if (!config.AI_API_KEY || !config.AI_MODEL_ENDPOINT) {
      console.warn('阿里云百炼API未配置，将使用模拟回复');
    }

    // 添加AI欢迎消息
    setTimeout(() => {
      const welcomeContent = '你好！我是你的AI运动教练，很高兴能帮助你。你想了解什么运动或健康相关的问题？';
      
      const welcomeMessage = {
        id: Date.now(),
        type: 'ai',
        content: welcomeContent,
        htmlContent: markdownToHtml(welcomeContent),
        suggestions: [
          '如何制定一个合理的健身计划？',
          '跑步时如何避免受伤？',
          '正确的深蹲姿势是怎样的？',
          '如何提高有氧耐力？'
        ]
      };
      
      const messages = [welcomeMessage];
      
      this.setData({
        messages,
        scrollToMessage: `msg-${welcomeMessage.id}`
      });
      
      // 添加到对话历史
      this.data.chatHistory.push({
        role: 'assistant',
        content: welcomeContent
      });
    }, 500);
  },

  /**
   * 处理输入框变化
   */
  handleInputChange(e) {
    this.setData({
      inputValue: e.detail.value
    });
  },

  /**
   * 发送消息
   */
  sendMessage() {
    const { inputValue } = this.data;
    if (!inputValue.trim()) return;

    // 添加用户消息
    this.addUserMessage(inputValue);

    // 清空输入框
    this.setData({
      inputValue: ''
    });

    // 显示AI正在输入
    this.setData({
      isTyping: true
    });

    // 调用AI回复
    this.getAIResponse(inputValue);
  },

  /**
   * 添加用户消息
   */
  addUserMessage(content) {
    const messages = [...this.data.messages];
    const chatHistory = [...this.data.chatHistory];
    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: content,
      timestamp: new Date().toISOString()
    };

    messages.push(newMessage);
    chatHistory.push({
      role: 'user',
      content: content
    });

    this.setData({
      messages,
      chatHistory,
      scrollToMessage: `msg-${newMessage.id}`
    });
  },

  /**
   * 添加AI消息
   */
  addAIMessage(messageData) {
    const messages = [...this.data.messages];
    const newMessage = {
      id: Date.now(),
      type: 'ai',
      content: messageData.content,
      htmlContent: markdownToHtml(messageData.content),
      suggestions: messageData.suggestions || [],
      trainingPlan: messageData.trainingPlan || null,
      timestamp: new Date().toISOString()
    };

    messages.push(newMessage);

    this.setData({
      messages,
      isTyping: false,
      scrollToMessage: `msg-${newMessage.id}`
    });
    
    // 如果不是欢迎消息，添加到对话历史
    if (this.data.chatHistory.length > 0) {
      const chatHistory = [...this.data.chatHistory];
      chatHistory.push({
        role: 'assistant',
        content: messageData.content
      });
      
      this.setData({
        chatHistory
      });
    }
  },

  /**
   * 获取AI响应
   */
  getAIResponse(userQuestion) {
    // 检查API配置
    const config = getConfig();
    if (!config.AI_API_KEY || !config.AI_MODEL_ENDPOINT) {
      console.log('API未配置，使用模拟回复');
      // 使用模拟回复
      setTimeout(() => {
        const response = this.generateSimulatedResponse(userQuestion);
        this.addAIMessage(response);
      }, 1500);
      return;
    }
    
    // 使用阿里云百炼API
    const systemPrompt = {
      role: 'system',
      content: '你是一个专业的运动健康教练，擅长回答用户关于运动、健身、营养和健康生活方式的问题。你的回答应简洁、专业且有针对性。使用Markdown格式来组织你的回答，包括标题、列表、表格等。对于合适的问题，可以推荐具体的训练计划或者建议后续的问题。'
    };
    
    // 构建对话历史，最多取最近10轮对话
    const recentHistory = [systemPrompt];
    
    // 添加历史对话记录
    if (this.data.chatHistory.length > 0) {
      // 最多添加5轮对话(10条消息)
      const historyMessages = this.data.chatHistory.slice(-10);
      recentHistory.push(...historyMessages);
    }
    
    // 为流式输出创建临时消息对象
    const tempMessage = {
      id: Date.now(),
      type: 'ai',
      content: '',
      htmlContent: '',
      suggestions: [],
      timestamp: new Date().toISOString(),
      isStreaming: true // 添加流式输出标记
    };
    
    // 添加临时消息到UI
    const messages = [...this.data.messages];
    messages.push(tempMessage);
    this.setData({
      messages,
      scrollToMessage: `msg-${tempMessage.id}`
    });
    
    // 创建句子收集器和内容
    let currentSentence = '';
    let fullContent = '';
    
    // 添加当前问题
    recentHistory.push({
      role: 'user',
      content: userQuestion
    });
    
    // 调用阿里云百炼API（流式模式）
    callQwenAPI(userQuestion, recentHistory)
      .then(response => {
        console.log('AI API 响应完成');
        
        // 最终处理回复内容
        const processedResponse = this.processAIResponse(fullContent);
        
        // 更新临时消息
        const updatedMessages = [...this.data.messages];
        const messageIndex = updatedMessages.findIndex(msg => msg.id === tempMessage.id);
        
        if (messageIndex !== -1) {
          updatedMessages[messageIndex] = {
            ...updatedMessages[messageIndex],
            content: processedResponse.content,
            htmlContent: markdownToHtml(processedResponse.content),
            suggestions: processedResponse.suggestions,
            trainingPlan: processedResponse.trainingPlan,
            isStreaming: false // 流式输出结束
          };
          
          this.setData({
            messages: updatedMessages,
            isTyping: false,
            scrollToMessage: `msg-${tempMessage.id}`
          });
        }
        
        // 添加到对话历史
        const chatHistory = [...this.data.chatHistory];
        chatHistory.push({
          role: 'assistant',
          content: processedResponse.content
        });
        
        this.setData({
          chatHistory
        });
      })
      .catch(error => {
        console.error('调用AI API失败:', error);
        
        // 显示错误信息
        wx.showToast({
          title: '连接AI服务失败',
          icon: 'none',
          duration: 2000
        });
        
        // 更新临时消息为错误信息
        const updatedMessages = [...this.data.messages];
        const messageIndex = updatedMessages.findIndex(msg => msg.id === tempMessage.id);
        
        if (messageIndex !== -1) {
          const errorResponse = this.generateSimulatedResponse(userQuestion);
          updatedMessages[messageIndex] = {
            ...updatedMessages[messageIndex],
            content: errorResponse.content,
            htmlContent: markdownToHtml(errorResponse.content),
            suggestions: errorResponse.suggestions,
            trainingPlan: errorResponse.trainingPlan,
            isStreaming: false // 流式输出结束
          };
          
          this.setData({
            messages: updatedMessages,
            isTyping: false
          });
          
          // 添加到对话历史
          const chatHistory = [...this.data.chatHistory];
          chatHistory.push({
            role: 'assistant',
            content: errorResponse.content
          });
          
          this.setData({
            chatHistory
          });
        }
      });
    
    // 提供onStreamResponse回调函数用于实时更新UI
    wx.aiCoachStreamCallback = (chunk) => {
      if (!chunk) return;
      
      // 追加内容
      currentSentence += chunk;
      fullContent += chunk;
      
      // 更新UI显示（减少更新频率，只在句子完成或达到一定长度时更新）
      if (currentSentence.includes('。') || currentSentence.includes('！') || 
          currentSentence.includes('？') || currentSentence.length > 15) {
        
        // 更新临时消息内容
        const updatedMessages = [...this.data.messages];
        const messageIndex = updatedMessages.findIndex(msg => msg.id === tempMessage.id);
        
        if (messageIndex !== -1) {
          updatedMessages[messageIndex].content = fullContent;
          
          this.setData({
            messages: updatedMessages,
            scrollToMessage: `msg-${tempMessage.id}`
          });
        }
        
        // 重置当前句子
        currentSentence = '';
      }
    };
  },
  
  /**
   * 处理AI响应，提取建议问题和训练计划
   */
  processAIResponse(content) {
    // 这里是一个简单的处理逻辑，实际项目中可以根据需要调整
    let suggestions = [];
    let trainingPlan = null;
    
    // 根据关键词判断内容类型
    if (content.includes('跑步') || content.includes('跑量')) {
      suggestions = ['如何避免跑步膝盖疼痛？', '跑步的正确姿势是什么？', '间歇跑和慢跑哪个更好？'];
      
      if (content.includes('计划') || content.includes('训练')) {
        trainingPlan = {
          title: '初学者跑步计划',
          description: '适合初学者的渐进式跑步训练计划',
          tags: ['初学者', '有氧', '耐力提升']
        };
      }
    } 
    else if (content.includes('增肌') || content.includes('力量') || content.includes('肌肉')) {
      suggestions = ['增肌期怎么安排饮食？', '哑铃增肌有什么好动作？', '如何避免增肌平台期？'];
      
      if (content.includes('计划') || content.includes('训练')) {
        trainingPlan = {
          title: '增肌训练计划',
          description: '针对主要肌群的全面训练计划',
          tags: ['增肌', '力量', '全身']
        };
      }
    }
    else if (content.includes('减脂') || content.includes('减肥') || content.includes('瘦')) {
      suggestions = ['如何减掉腹部脂肪？', 'HIIT训练有什么好处？', '间歇性断食效果好吗？'];
      
      if (content.includes('计划') || content.includes('训练')) {
        trainingPlan = {
          title: '减脂计划',
          description: '组合HIIT和力量训练的减脂计划',
          tags: ['减脂', 'HIIT', '营养控制']
        };
      }
    }
    
    return {
      content: content,
      suggestions: suggestions,
      trainingPlan: trainingPlan
    };
  },

  /**
   * 生成模拟AI响应
   */
  generateSimulatedResponse(question) {
    // 简单的关键词匹配规则，作为API调用失败的备选方案
    question = question.toLowerCase();
    
    if (question.includes('跑步') || question.includes('跑') || question.includes('跑量')) {
      return {
        content: '## 跑步入门指南\n\n跑步是一项很棒的有氧运动。开始跑步前，建议先进行5-10分钟的热身，包括动态拉伸和快走。\n\n### 新手跑步计划\n\n初学者可以从每周跑3次，每次15-20分钟开始，逐渐增加时间和频率。\n\n| 周次 | 跑步时间 | 频率 | 强度 |\n| --- | --- | --- | --- |\n| 第1周 | 15分钟 | 每周3次 | 低强度 |\n| 第2周 | 20分钟 | 每周3次 | 低强度 |\n| 第3周 | 25分钟 | 每周3-4次 | 中低强度 |\n| 第4周 | 30分钟 | 每周4次 | 中强度 |\n\n### 注意事项\n\n* 选择合适的跑鞋非常重要\n* 注意跑姿，保持上身挺直\n* 循序渐进，避免过度训练',
        suggestions: ['如何避免跑步膝盖疼痛？', '跑步的正确姿势是什么？', '间歇跑和慢跑哪个更好？'],
        trainingPlan: {
          title: '初学者5周跑步计划',
          description: '从零开始，5周内逐步提高跑步能力，适合初学者。',
          tags: ['初学者', '有氧', '耐力提升']
        }
      };
    } 
    else if (question.includes('增肌') || question.includes('力量') || question.includes('肌肉')) {
      return {
        content: '# 增肌训练基础\n\n增肌训练需要结合适当的饮食和有效的力量训练。\n\n## 训练原则\n\n1. 每周进行3-4次力量训练\n2. 每次针对不同肌群\n3. 确保摄入足够的蛋白质(每公斤体重1.6-2.2克)\n\n## 推荐训练计划\n\n### A. 胸部和三头肌\n* 平板卧推：4组，每组8-12次\n* 上斜哑铃飞鸟：3组，每组12-15次\n* 绳索下压：3组，每组12-15次\n\n### B. 背部和二头肌\n* 引体向上或高位下拉：4组，每组8-12次\n* 坐姿划船：3组，每组10-12次\n* 哑铃弯举：3组，每组12-15次\n\n### C. 腿部和肩部\n* 杠铃深蹲：4组，每组8-10次\n* 腿举：3组，每组10-12次\n* 肩上推举：3组，每组8-12次',
        suggestions: ['增肌期怎么安排饮食？', '哑铃增肌有什么好动作？', '如何避免增肌平台期？'],
        trainingPlan: {
          title: '4周增肌训练计划',
          description: '针对主要肌群的全面训练，搭配高蛋白饮食，有效增肌。',
          tags: ['增肌', '力量', '全身']
        }
      };
    }
    else if (question.includes('减脂') || question.includes('减肥') || question.includes('瘦')) {
      return {
        content: '# 有效减脂指南\n\n减脂最有效的方法是结合有氧运动、力量训练和控制饮食。\n\n## 关键策略\n\n### 有氧训练\n每周进行3-5次有氧运动(如HIIT、跑步)，每次30-45分钟。\n\n### 力量训练\n每周2-3次力量训练，保持肌肉量，提高代谢率。\n\n### 饮食控制\n保持轻度的热量赤字(每天减少300-500卡路里)。\n\n## HIIT训练示例\n\n| 动作 | 时间 | 休息 | 组数 |\n| --- | --- | --- | --- |\n| 高抬腿 | 30秒 | 15秒 | 4组 |\n| 波比跳 | 30秒 | 15秒 | 4组 |\n| 开合跳 | 30秒 | 15秒 | 4组 |\n| 俯卧撑 | 30秒 | 15秒 | 4组 |\n\n## 饮食建议\n\n* 增加蛋白质摄入(瘦肉、鱼、蛋、豆类)\n* 选择复合碳水化合物(全谷物、蔬菜)\n* 控制脂肪摄入(选择健康脂肪)',
        suggestions: ['如何减掉腹部脂肪？', 'HIIT训练有什么好处？', '间歇性断食效果好吗？'],
        trainingPlan: {
          title: '6周减脂计划',
          description: '组合HIIT和力量训练，高效燃脂，保持肌肉。',
          tags: ['减脂', 'HIIT', '营养控制']
        }
      };
    }
    else if (question.includes('拉伸') || question.includes('柔韧性') || question.includes('僵硬')) {
      return {
        content: '# 提高柔韧性训练指南\n\n提高柔韧性可以通过静态拉伸和动态拉伸来实现。\n\n## 拉伸基本原则\n\n* 每周至少进行3次柔韧性训练\n* 每次15-30分钟\n* 热身后进行动态拉伸\n* 运动后进行静态拉伸\n* 每个姿势保持20-30秒\n\n## 全身拉伸动作\n\n### 上肢拉伸\n1. **肩部拉伸**: 一只手臂横过胸前，另一只手臂辅助拉伸\n2. **三头肌拉伸**: 一只手臂弯曲举过头顶，另一只手按压肘部\n\n### 下肢拉伸\n1. **腘绳肌拉伸**: 坐姿，一腿伸直，上身前倾\n2. **股四头肌拉伸**: 站立，一腿弯曲向后，手抓脚踝\n\n### 躯干拉伸\n1. **猫式伸展**: 四肢支撑，背部轮流拱起和下沉\n2. **侧弯拉伸**: 站立，一手上举，身体向另一侧弯曲',
        suggestions: ['哪些瑜伽动作适合初学者？', '如何改善肩膀僵硬？', '拉伸要多久才有效果？'],
        trainingPlan: {
          title: '全身柔韧性提升计划',
          description: '系统性拉伸训练，每日15分钟，有效提升全身柔韧性。',
          tags: ['柔韧性', '拉伸', '恢复']
        }
      };
    }
    else {
      return {
        content: '# 运动健康指导\n\n作为你的AI运动教练，我可以帮你解答运动健康相关的问题，制定训练计划，或者提供营养建议。\n\n## 常见训练类型\n\n1. **有氧训练**: 提高心肺功能，消耗脂肪\n2. **力量训练**: 增加肌肉质量，提高基础代谢\n3. **柔韧性训练**: 增加关节活动范围，预防损伤\n4. **HIIT训练**: 高效燃脂，节省时间\n\n## 常见问题\n\n| 问题类型 | 建议咨询内容 |\n| --- | --- |\n| 减脂塑形 | HIIT训练计划、营养控制建议 |\n| 增肌增重 | 力量训练方案、高蛋白饮食 |\n| 体能提升 | 有氧训练计划、间歇训练 |\n| 运动恢复 | 拉伸动作、放松技巧 |\n\n请告诉我你的具体需求或疑问，我会尽力提供专业指导。',
        suggestions: ['如何制定适合自己的训练计划？', '运动后肌肉酸痛怎么缓解？', '健身初学者应该注意什么？']
      };
    }
  },
  
  /**
   * 选择建议问题
   */
  selectSuggestion(e) {
    const suggestion = e.currentTarget.dataset.suggestion;
    // 直接将建议问题作为用户输入发送
    this.addUserMessage(suggestion);
    
    // 显示AI正在输入
    this.setData({
      isTyping: true
    });
    
    // 获取AI回复
    this.getAIResponse(suggestion);
  },

  /**
   * 直接提问预设问题
   */
  askQuestion(e) {
    const question = e.currentTarget.dataset.question;
    // 将问题作为用户输入发送
    this.addUserMessage(question);
    
    // 显示AI正在输入
    this.setData({
      isTyping: true
    });
    
    // 获取AI回复
    this.getAIResponse(question);
  },

  /**
   * 保存训练计划
   */
  savePlan(e) {
    const plan = e.currentTarget.dataset.plan;
    
    // 这里可以添加保存计划到用户数据的逻辑
    wx.showToast({
      title: '计划已保存',
      icon: 'success'
    });
    
    // 添加保存后的AI回复
    setTimeout(() => {
      const response = {
        content: `我已经帮你保存了"${plan.title}"计划。你可以在个人资料页查看所有保存的计划。需要我为你详细解释这个计划吗？`,
        suggestions: ['详细解释一下这个计划', '如何开始执行这个计划？', '这个计划适合新手吗？']
      };
      
      this.addAIMessage(response);
    }, 1000);
  },

  /**
   * 加载更多消息（上拉加载）
   */
  loadMoreMessages() {
    // 实际项目中可以实现加载历史消息的逻辑
    console.log('加载更多历史消息');
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
});