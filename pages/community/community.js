// pages/community/community.js
const { getPostList, createPost, likePost, commentPost, getUserList } = require('../../api/communityApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    activeTab: 0,
    activeCategory: 'all',
    // 推荐用户列表
    recommendUsers: [
      {
        id: 1,
        name: '李明',
        avatar: '/static/images/avatar1.jpg'
      },
      {
        id: 2,
        name: '王琳',
        avatar: '/static/images/avatar2.jpg'
      },
      {
        id: 3,
        name: '张华',
        avatar: '/static/images/avatar3.jpg'
      },
      {
        id: 4,
        name: '刘芳',
        avatar: '/static/images/avatar4.jpg'
      }
    ],
    // 社区分类
    categories: [
      { id: 'all', name: '全部' },
      { id: 'running', name: '跑步' },
      { id: 'basketball', name: '篮球' },
      { id: 'football', name: '足球' },
      { id: 'badminton', name: '羽毛球' },
      { id: 'swimming', name: '游泳' },
      { id: 'fitness', name: '健身' },
      { id: 'yoga', name: '瑜伽' }
    ],
    // 帖子列表
    posts: [
      {
        id: 1,
        user: {
          id: 1,
          name: '李明',
          avatar: '/static/images/avatar1.jpg'
        },
        content: '今天完成了7公里的跑步，感觉很棒！想问一下大家平时都用什么软件记录跑步轨迹，有什么好推荐的吗？',
        images: [],
        time: '10分钟前',
        likes: 0,
        comments: 8,
        isLiked: false,
        categories: ['跑步', '全部'],
        commentList: [],
        showComments: false,
        commentInput: ''
      }
    ],
    // 当前发帖内容
    postContent: '',
    postCategory: 'all',
    showEmojiPicker: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.loadPosts();
    this.loadRecommendUsers();
  },

  /**
   * 加载帖子列表
   */
  loadPosts: function(category) {
    wx.showLoading({
      title: '加载中',
    });
    let params = {};
    if (category && category !== 'all') {
      params.category = category;
    }
    getPostList(params).then(res => {
      if (res && res.length > 0) {
        // 处理分类标签
        res.forEach(post => {
          post.categories = this.extractCategories(post.content);
          post.commentList = post.commentList || [];
          post.showComments = false;
          post.commentInput = '';
        });
        this.setData({
          posts: res
        });
      }
    }).catch(err => {
      console.error('获取帖子列表失败', err);
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 加载推荐用户
   */
  loadRecommendUsers: function() {
    getUserList().then(res => {
      if (res && res.length > 0) {
        this.setData({
          recommendUsers: res.slice(0, 8) // 只显示前8个推荐用户
        });
      }
    }).catch(err => {
      console.error('获取推荐用户失败', err);
    });
  },

  /**
   * 切换分类
   */
  switchCategory: function(e) {
    const id = e.currentTarget.dataset.id;
    this.setData({
      activeCategory: id
    });
    this.loadPosts(id);
  },

  /**
   * 跳转到用户详情
   */
  goToUserDetail: function(e) {
    const userId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/userDetail/userDetail?id=${userId}`,
    });
  },

  /**
   * 跳转到帖子详情
   */
  goToPostDetail: function(e) {
    const postId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/postDetail/postDetail?id=${postId}`,
    });
  },

  /**
   * 输入帖子内容
   */
  inputPostContent: function(e) {
    this.setData({
      postContent: e.detail.value
    });
  },

  /**
   * 解析内容中的分类标签（如##篮球、##跑步），返回分类数组
   */
  extractCategories: function(content) {
    const matches = content.match(/##([\u4e00-\u9fa5A-Za-z0-9_]+)/g);
    let categories = ['全部'];
    if (matches) {
      matches.forEach(m => {
        categories.push(m.replace('##', ''));
      });
    }
    return categories;
  },

  /**
   * 发布帖子
   */
  submitPost: function() {
    if (!this.data.postContent.trim()) {
      wx.showToast({
        title: '内容不能为空',
        icon: 'none'
      });
      return;
    }
    wx.showLoading({
      title: '发布中',
    });
    const categories = this.extractCategories(this.data.postContent);
    createPost({content: this.data.postContent, categories}).then(res => {
      wx.showToast({
        title: '发布成功',
        icon: 'success'
      });
      this.setData({
        postContent: ''
      });
      this.loadPosts(this.data.activeCategory);
    }).catch(err => {
      wx.showToast({
        title: '发布失败',
        icon: 'none'
      });
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 显示/隐藏表情选择器
   */
  toggleEmojiPicker: function() {
    this.setData({
      showEmojiPicker: !this.data.showEmojiPicker
    });
  },

  /**
   * 选择图片
   */
  chooseImage: function() {
    wx.chooseImage({
      count: 9,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        // 上传图片逻辑
        console.log('选择的图片', res.tempFilePaths);
      }
    });
  },

  /**
   * 点赞帖子
   */
  likePost: function(e) {
    const postId = e.currentTarget.dataset.id;
    const index = this.data.posts.findIndex(post => post.id === postId);
    if (index === -1) return;
    
    const post = this.data.posts[index];
    const action = post.isLiked ? 'unlike' : 'like';
    
    // 先在UI上反映点赞状态变化，提升用户体验
    const posts = [...this.data.posts];
    posts[index].isLiked = !post.isLiked;
    posts[index].likes = post.isLiked ? Math.max(0, post.likes - 1) : post.likes + 1;
    this.setData({ posts });
    
    // 调用API
    likePost({ postId, action }).then(res => {
      if (res) {
        // 更新实际点赞数量
        const updatedPosts = [...this.data.posts];
        updatedPosts[index].likes = res.likes || res.likes_count || updatedPosts[index].likes;
        updatedPosts[index].isLiked = res.is_liked !== undefined ? res.is_liked : updatedPosts[index].isLiked;
        this.setData({ posts: updatedPosts });
      }
    }).catch(err => {
      console.error('点赞失败', err);
      // 如果点赞失败，恢复原状态
      const recoveredPosts = [...this.data.posts];
      recoveredPosts[index].isLiked = post.isLiked;
      recoveredPosts[index].likes = post.likes;
      this.setData({ posts: recoveredPosts });
      
      wx.showToast({
        title: '操作失败',
        icon: 'none'
      });
    });
  },

  /**
   * 切换评论输入框显示并加载评论
   */
  toggleCommentInput: function(e) {
    const postId = e.currentTarget.dataset.id;
    const posts = this.data.posts.map(post => {
      if (post.id === postId) {
        post.showComments = !post.showComments;
        
        // 如果打开评论区且还没有加载评论，则加载评论
        if (post.showComments && (!post.commentList || post.commentList.length === 0)) {
          // 这里可以加入加载评论列表的逻辑
          // 模拟一些评论数据
          if (post.comments > 0) {
            wx.showLoading({ title: '加载评论中' });
            
            // 模拟网络请求延迟
            setTimeout(() => {
              // 生成模拟评论数据
              const mockComments = [];
              const userNames = ['李明', '王琳', '张华', '刘芳', '赵强'];
              const commentContents = [
                '很棒的分享，谢谢！',
                '我也有同样的经历',
                '请问具体是什么型号的跑鞋？',
                '加油继续坚持！',
                '这个训练方法很不错'
              ];
              
              for (let i = 0; i < Math.min(post.comments, 5); i++) {
                mockComments.push({
                  id: i + 1,
                  user: { name: userNames[Math.floor(Math.random() * userNames.length)] },
                  content: commentContents[Math.floor(Math.random() * commentContents.length)]
                });
              }
              
              // 更新评论列表
              const updatedPosts = [...this.data.posts];
              const postIndex = updatedPosts.findIndex(p => p.id === postId);
              if (postIndex !== -1) {
                updatedPosts[postIndex].commentList = mockComments;
                this.setData({ posts: updatedPosts });
              }
              
              wx.hideLoading();
            }, 500);
          }
        }
      } else {
        post.showComments = false;
      }
      return post;
    });
    this.setData({ posts });
  },

  /**
   * 评论输入
   */
  inputCommentContent: function(e) {
    const postId = e.currentTarget.dataset.id;
    const value = e.detail.value;
    const posts = this.data.posts.map(post => {
      if (post.id === postId) {
        post.commentInput = value;
      }
      return post;
    });
    this.setData({ posts });
  },

  /**
   * 提交评论
   */
  submitComment: function(e) {
    const postId = e.currentTarget.dataset.id;
    const index = this.data.posts.findIndex(post => post.id === postId);
    if (index === -1) return;
    const content = this.data.posts[index].commentInput;
    if (!content.trim()) {
      wx.showToast({ title: '评论不能为空', icon: 'none' });
      return;
    }
    commentPost({ postId, content }).then(res => {
      wx.showToast({ title: '评论成功', icon: 'success' });
      // 新增评论到本地
      const posts = [...this.data.posts];
      posts[index].commentList = posts[index].commentList || [];
      posts[index].commentList.push({
        id: Date.now(),
        user: { name: '我' },
        content
      });
      posts[index].commentInput = '';
      posts[index].comments = (posts[index].comments || 0) + 1;
      // 确保评论区保持打开状态
      posts[index].showComments = true;
      this.setData({ posts });
    }).catch(() => {
      wx.showToast({ title: '评论失败', icon: 'none' });
    });
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: '校园运动社区',
      path: '/pages/community/community'
    }
  }
}) 