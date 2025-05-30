// pages/news/news.js
const { getNewsList, getNewsCategories } = require('../../api/newsApi');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    activeTab: 0,
    searchValue: '',
    // 资讯分类
    categories: [
      { id: 'all', name: '推荐' },
      { id: 'health', name: '健康知识' },
      { id: 'sports', name: '运动技巧' },
      { id: 'campus', name: '校园活动' },
      { id: 'nutrition', name: '营养饮食' },
      { id: 'science', name: '运动科学' }
    ],
    // 资讯列表
    newsList: [
      {
        id: 1,
        title: '校园马拉松月底开跑，请各位运动员提前报名',
        image: 'https://img.freepik.com/free-photo/runners-marathon_53876-18652.jpg',
        source: '校园体育部',
        date: '2023-05-13',
        views: 1245,
        content: '今年校园马拉松将于5月30日举行，参赛选手需要提前两周报名，并参加赛前培训...'
      },
      {
        id: 2,
        title: '运动医学专家来校讲座，揭秘科学健身方法',
        image: 'https://img.freepik.com/free-photo/fitness-concept-with-girl-gym_23-2147680220.jpg',
        source: '运动健康协会',
        date: '2023-05-10',
        views: 867,
        content: '著名运动医学专家王教授将在下周三下午3点于大学体育馆进行科学健身专题讲座...'
      }
    ],
    // 热门资讯
    hotNews: {
      id: 3,
      title: '体医融合视角下大学生体育活动与学业表现的关系研究',
      image: 'https://img.freepik.com/free-photo/woman-doing-squats-with-dumbbells_651396-1264.jpg',
      summary: '本研究通过对大学生体育活动与学业表现的关系进行了深入探讨，发现适量的体育锻炼对提高学习效率有显著帮助。',
      author: '体育学院研究团队',
      date: '2023-05-08',
      views: 1987
    }
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.loadNews();
    this.loadCategories();
  },

  /**
   * 加载资讯列表
   */
  loadNews: function() {
    wx.showLoading({
      title: '加载中',
    });
    
    getNewsList().then(res => {
      if (res && res.length > 0) {
        // 找出浏览量最高的作为热门资讯
        let hotNews = res.reduce((prev, current) => {
          return (prev.views > current.views) ? prev : current;
        });
        
        // 其他资讯列表
        let newsList = res.filter(item => item.id !== hotNews.id);
        
        this.setData({
          hotNews,
          newsList
        });
      }
    }).catch(err => {
      console.error('获取资讯列表失败', err);
    }).finally(() => {
      wx.hideLoading();
    });
  },

  /**
   * 加载资讯分类
   */
  loadCategories: function() {
    getNewsCategories().then(res => {
      if (res && res.length > 0) {
        // 添加"推荐"分类
        const categories = [{ id: 'all', name: '推荐' }, ...res];
        this.setData({
          categories
        });
      }
    }).catch(err => {
      console.error('获取资讯分类失败', err);
    });
  },

  /**
   * 切换分类
   */
  switchCategory: function(e) {
    const id = e.currentTarget.dataset.id;
    
    // 切换选中状态
    this.data.categories.forEach((item, index) => {
      if (item.id === id) {
        this.setData({
          activeTab: index
        });
      }
    });
    
    // 加载对应分类的资讯
    if (id === 'all') {
      this.loadNews();
    } else {
      getNewsList({category: id}).then(res => {
        if (res) {
          // 找出浏览量最高的作为热门资讯
          let hotNews = res.reduce((prev, current) => {
            return (prev.views > current.views) ? prev : current;
          }, {views: 0});
          
          // 其他资讯列表
          let newsList = res.filter(item => item.id !== hotNews.id);
          
          this.setData({
            hotNews,
            newsList
          });
        }
      }).catch(err => {
        console.error('获取分类资讯失败', err);
      });
    }
  },

  /**
   * 搜索资讯
   */
  searchNews: function(e) {
    const value = e.detail.value;
    this.setData({
      searchValue: value
    });
    
    if (value) {
      getNewsList({keyword: value}).then(res => {
        if (res) {
          this.setData({
            newsList: res,
            hotNews: null // 搜索结果不需要显示热门资讯
          });
        }
      }).catch(err => {
        console.error('搜索资讯失败', err);
      });
    } else {
      this.loadNews();
    }
  },

  /**
   * 查看资讯详情
   */
  viewNewsDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/newsDetail/newsDetail?id=${id}`,
    });
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: '校园运动资讯',
      path: '/pages/news/news'
    }
  }
}) 