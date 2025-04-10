Page({
  data: {
    historyList: []
  },

  onShow() {
    this.loadHistory();
  },

  loadHistory() {
    const history = wx.getStorageSync('newsHistory') || [];
    const formattedHistory = history.map(item => ({
      ...item,
      formattedTime: this.formatTime(item.timestamp)
    }));
    
    this.setData({
      historyList: formattedHistory
    });
  },

  formatTime(timestamp) {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hour = date.getHours().toString().padStart(2, '0');
    const minute = date.getMinutes().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hour}:${minute}`;
  },

  deleteItem(e) {
    const index = e.currentTarget.dataset.index;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条记录吗？',
      success: (res) => {
        if (res.confirm) {
          const history = wx.getStorageSync('newsHistory') || [];
          history.splice(index, 1);
          wx.setStorageSync('newsHistory', history);
          this.loadHistory();
          
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          });
        }
      }
    });
  },

  clearAllHistory() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有历史记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.setStorageSync('newsHistory', []);
          this.setData({
            historyList: []
          });
          
          wx.showToast({
            title: '已清空所有记录',
            icon: 'success'
          });
        }
      }
    });
  }
}); 