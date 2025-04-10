document.addEventListener('DOMContentLoaded', function() {
  const detectButton = document.getElementById('detectButton');
  const resultDiv = document.getElementById('result');

  detectButton.addEventListener('click', async () => {
    try {
      // 显示加载状态
      resultDiv.innerHTML = '<div class="loading">正在获取页面内容...</div>';
      
      // 获取当前标签页
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // 注入并执行内容脚本来获取页面文本
      const [{result}] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          // 获取页面所有可见文本
          return document.body.innerText;
        }
      });

      resultDiv.innerHTML = '<div class="loading">正在分析内容...</div>';

      // 发送到API进行检测
      const response = await fetch('http://127.0.0.1:9099/quick/detection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: result
        })
      });

      const data = await response.json();
      
      if (data.success && data.data) {
        // 格式化显示检测结果
        const newsStatus = data.data.IsNewsTrue === 1 ? 
          '<span class="true-news">真实新闻</span>' : 
          '<span class="false-news">虚假新闻</span>';

        let reasonsHtml = '';
        if (data.data.reasons && data.data.reasons.length > 0) {
          reasonsHtml = data.data.reasons.map(reason => 
            `<div class="reason-item">${reason}</div>`
          ).join('');
        }

        resultDiv.innerHTML = `
          <div class="result-header">检测结果</div>
          <div class="result-section">
            <div class="result-label">新闻真实性：</div>
            <div>${newsStatus}</div>
          </div>
          <div class="result-section">
            <div class="result-label">判断依据：</div>
            ${reasonsHtml}
          </div>
          <div class="recommendation">
            <div class="result-label">建议：</div>
            ${data.data.recommendation}
          </div>
        `;
        
        // 保存到历史记录
        const history = JSON.parse(localStorage.getItem('detectionHistory') || '[]');
        history.unshift({
          text: result,
          result: data.data,
          timestamp: new Date().getTime(),
          url: tab.url
        });
        localStorage.setItem('detectionHistory', JSON.stringify(history));
      } else {
        resultDiv.innerHTML = `<div style="color: red;">检测失败：${data.msg || '未知错误'}</div>`;
      }
    } catch (error) {
      console.error('Error:', error);
      resultDiv.innerHTML = `
        <div style="color: red;">
          错误：${error.message}<br>
          请确保：<br>
          1. 后端服务已启动<br>
          2. 后端服务地址正确
        </div>
      `;
    }
  });
}); 