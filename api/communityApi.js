/**
 * 社区相关API
 */
const { request } = require('./request');
const { getConfig } = require('../config/env');

// 本地存储键名
const STORAGE_KEY = 'community_posts';

// 获取本地帖子
function getLocalPosts() {
  return wx.getStorageSync(STORAGE_KEY) || [];
}

// 保存帖子到本地
function saveLocalPosts(posts) {
  wx.setStorageSync(STORAGE_KEY, posts);
}

/**
 * 获取社区动态列表
 * @param {Object} data 查询参数
 * @returns {Promise}
 */
const getPostList = (data = {}) => {
  const config = getConfig();

  // 如果启用模拟数据，优先从本地存储读取
  if (config.mockData) {
    return new Promise(resolve => {
      setTimeout(() => {
        let posts = getLocalPosts();
        if (posts.length === 0) {
          posts = generateMockPosts();
          saveLocalPosts(posts);
        }
        resolve(posts);
      }, 300);
    });
  }

  // 真实请求，失败时仍使用模拟数据
  return new Promise((resolve, reject) => {
    request('/community/posts', data)
      .then(res => {
        if (!res || !res.posts || res.posts.length === 0) {
          console.log('使用模拟数据代替空列表');
          const mock = generateMockPosts();
          resolve(mock);
        } else {
          resolve(res);
        }
      })
      .catch(err => {
        console.error('获取帖子列表失败:', err);
        console.log('请求失败，使用模拟数据');
        resolve(generateMockPosts());
      });
  });
};

/**
 * 生成模拟帖子数据
 * @returns {Array} 模拟帖子列表
 */
const generateMockPosts = () => {
  const mockPosts = [];
  const now = new Date();
  
  // 用户名和头像
  const users = [
    { id: 1, name: '李明', avatar: '/static/images/avatar1.jpg' },
    { id: 2, name: '王琳', avatar: '/static/images/avatar2.jpg' },
    { id: 3, name: '张华', avatar: '/static/images/avatar3.jpg' },
    { id: 4, name: '刘芳', avatar: '/static/images/avatar4.jpg' },
    { id: 5, name: '赵强', avatar: '/static/images/avatar5.jpg' }
  ];
  
  // 帖子内容模板
  const contentTemplates = [
    "今天完成了{distance}公里的跑步，感觉很棒！#运动健康 #跑步",
    "在{location}打了2小时篮球，球技有进步！#篮球 #运动",
    "分享一下今天的健身计划：{workout}。坚持就是胜利！#健身 #坚持",
    "今天尝试了{activity}，很有挑战性但也很有趣！推荐大家尝试。"
  ];
  
  // 地点
  const locations = ["大学体育馆", "西区操场", "健身中心", "游泳馆", "篮球场"];
  
  // 活动
  const activities = ["跑步", "篮球", "足球", "羽毛球", "游泳", "健身", "瑜伽"];
  
  // 健身内容
  const workouts = [
    "胸肌训练 + HIIT 30分钟",
    "背部肌群 + 10公里跑步",
    "腿部训练日 + 拉伸",
    "全身有氧 45分钟"
  ];
  
  // 生成20条模拟帖子
  for (let i = 0; i < 20; i++) {
    // 随机选择用户
    const user = users[Math.floor(Math.random() * users.length)];
    
    // 随机选择内容模板
    const template = contentTemplates[Math.floor(Math.random() * contentTemplates.length)];
    
    // 填充模板
    let content = template;
    content = content.replace('{distance}', Math.floor(Math.random() * 15) + 3);
    content = content.replace('{location}', locations[Math.floor(Math.random() * locations.length)]);
    content = content.replace('{workout}', workouts[Math.floor(Math.random() * workouts.length)]);
    content = content.replace('{activity}', activities[Math.floor(Math.random() * activities.length)]);
    
    // 创建随机时间（最近7天内）
    const hoursAgo = Math.floor(Math.random() * 24 * 7);
    const postTime = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000);
    
    // 添加模拟帖子
    mockPosts.push({
      id: i + 1,
      user: {
        id: user.id,
        name: user.name,
        avatar: user.avatar
      },
      content: content,
      images: Math.random() > 0.6 ? ['/static/images/posts/post' + (Math.floor(Math.random() * 5) + 1) + '.jpg'] : [],
      time: formatTimeAgo(postTime),
      likes: Math.floor(Math.random() * 50),
      comments: Math.floor(Math.random() * 20),
      isLiked: Math.random() > 0.5,
      commentList: []
    });
  }
  
  return mockPosts;
};

/**
 * 格式化时间为"几分钟前"、"几小时前"等
 * @param {Date} time 时间
 * @returns {String} 格式化后的时间文本
 */
const formatTimeAgo = (time) => {
  const now = new Date();
  const diff = now.getTime() - time.getTime();
  
  // 分钟
  const minutes = Math.floor(diff / (60 * 1000));
  if (minutes < 60) {
    return minutes + '分钟前';
  }
  
  // 小时
  const hours = Math.floor(diff / (60 * 60 * 1000));
  if (hours < 24) {
    return hours + '小时前';
  }
  
  // 天
  const days = Math.floor(diff / (24 * 60 * 60 * 1000));
  return days + '天前';
};

/**
 * 获取帖子详情
 * @param {Object} data 帖子ID
 * @returns {Promise}
 */
const getPostDetail = (data = {}) => {
  return request('/community/post/detail', data);
};

/**
 * 发布帖子
 * @param {Object} data 帖子内容
 * @returns {Promise}
 */
const createPost = (data = {}) => {
  return request('/community/post/create', data);
};

/**
 * 点赞帖子
 * @param {Object} data 点赞参数
 * @param {number} data.postId 帖子ID
 * @param {string} data.action 操作类型: like / unlike (可选)
 * @returns {Promise}
 */
const likePost = (data = {}) => {
  const reqData = {
    post_id: data.postId
  };

  const config = getConfig();

  if (config.mockData) {
    return new Promise(resolve => {
      setTimeout(() => {
        const posts = getLocalPosts();
        const index = posts.findIndex(p => p.id === data.postId);
        if (index !== -1) {
          const post = posts[index];
          let isLiked;
          if (data.action === 'like') {
            isLiked = true;
          } else if (data.action === 'unlike') {
            isLiked = false;
          } else {
            isLiked = !post.isLiked;
          }
          post.isLiked = isLiked;
          post.likes = Math.max(0, isLiked ? post.likes + 1 : post.likes - 1);
          posts[index] = post;
          saveLocalPosts(posts);
          resolve({ is_liked: post.isLiked, likes_count: post.likes, likes: post.likes });
        } else {
          resolve({ is_liked: false, likes_count: 0, likes: 0 });
        }
      }, 300);
    });
  }

  return new Promise((resolve, reject) => {
    request('/community/like/toggle', reqData)
      .then(res => {
        if (res) {
          if (res.likes_count !== undefined && res.likes === undefined) {
            res.likes = res.likes_count;
          } else if (res.likes !== undefined && res.likes_count === undefined) {
            res.likes_count = res.likes;
          }
        }
        resolve(res);
      })
      .catch(err => {
        console.error('点赞请求失败:', err);
        if (err && err.message && err.message.includes('动态不存在')) {
          console.log('使用模拟数据替代');
          const likes_count = Math.floor(Math.random() * 50) + 5;
          const mockResult = {
            is_liked: !data.action || data.action === 'like',
            likes_count: likes_count,
            likes: likes_count
          };
          resolve(mockResult);
        } else {
          reject(err);
        }
      });
  });
};

/**
 * 评论帖子
 * @param {Object} data 评论内容
 * @returns {Promise}
 */
const commentPost = (data = {}) => {
  const config = getConfig();

  if (config.mockData) {
    return new Promise(resolve => {
      setTimeout(() => {
        const posts = getLocalPosts();
        const index = posts.findIndex(p => p.id === data.postId);
        if (index !== -1) {
          const post = posts[index];
          const commentId = Date.now();
          post.commentList = post.commentList || [];
          post.commentList.push({ id: commentId, user: { name: '我' }, content: data.content });
          post.comments = (post.comments || 0) + 1;
          posts[index] = post;
          saveLocalPosts(posts);
          resolve({ comment_id: commentId, success: true });
        } else {
          resolve({ comment_id: 0, success: false });
        }
      }, 300);
    });
  }

  return request('/community/post/comment', data);
};

/**
 * 获取用户列表
 * @returns {Promise}
 */
const getUserList = () => {
  return request('/community/users', {});
};

module.exports = {
  getPostList,
  getPostDetail,
  createPost,
  likePost,
  commentPost,
  getUserList
}; 