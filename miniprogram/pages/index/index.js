Page({
  data: {
    inputText: '',
    result: null,
    // 开发环境使用 http，生产环境需要使用 https
    isDev: true  // 上线前记得改为 false
  },

  onInputChange(e) {
    this.setData({
      inputText: e.detail.value
    });
  },

  detectNews() {
    if (!this.data.inputText.trim()) {
      wx.showToast({
        title: '请输入新闻内容',
        icon: 'none'
      });
      return;
    }

    // 检查是否开启了调试模式
    if (!this.data.isDev && !wx.getSystemInfoSync().platform.includes('devtools')) {
      wx.showModal({
        title: '提示',
        content: '当前为生产环境，请使用 HTTPS 协议的域名',
        showCancel: false
      });
      return;
    }

    wx.showLoading({
      title: '检测中...'
    });

    // 根据环境使用不同的 API 地址
    const apiUrl = this.data.isDev 
      ? 'http://127.0.0.1:9099/quick/detection'
      : 'https://your-domain.com/detection/detection_task/quick';  // 这里替换为您的生产环境域名

    wx.request({
      url: apiUrl,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        "text": this.data.inputText
      },
      success: (res) => {
        console.log('API返回数据：', res.data);
        if (res.data.success && res.data.data) {
          this.setData({
            result: res.data.data
          }, () => {
            // 检测成功后自动保存到历史记录
            const history = wx.getStorageSync('newsHistory') || [];
            const newRecord = {
              text: this.data.inputText,
              result: this.data.result,
              timestamp: new Date().getTime()
            };
            
            history.unshift(newRecord);
            wx.setStorageSync('newsHistory', history);
          });
        } else {
          wx.showToast({
            title: res.data.msg || '请求失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('请求失败：', err);
        if (this.data.isDev) {
          wx.showModal({
            title: '开发环境提示',
            content: '请确保：\n1. 后端服务已启动\n2. 开发者工具中已勾选"不校验合法域名"选项',
            showCancel: false
          });
        } else {
          wx.showToast({
            title: '检测失败，请稍后重试',
            icon: 'none'
          });
        }
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  saveToHistory() {
    const history = wx.getStorageSync('newsHistory') || [];
    const newRecord = {
      text: this.data.inputText,
      result: this.data.result,
      timestamp: new Date().getTime()
    };
    
    history.unshift(newRecord);
    wx.setStorageSync('newsHistory', history);
    
    wx.showToast({
      title: '已保存到历史记录',
      icon: 'success'
    });
  }
}); 