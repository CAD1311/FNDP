import request from '@/utils/request'

// 查询新闻列表
export function listNews(query) {
  return request({
    url: '/news/news_info/list',
    method: 'get',
    params: query
  })
}



// 新增新闻
export function addNews(data) {
  return request({
    url: '/news/news_info',
    method: 'post',
    data: data
  })
}

// 修改新闻
export function updateNews(data) {
  return request({
    url: '/news/news_info',
    method: 'put',
    data: data
  })
}

// 删除新闻
export function delNews(newsId) {
  return request({
    url: '/news/news_info/' + newsId,
    method: 'delete'
  })
}

//导出新闻
export function exportNews(query) {
  return request({
    url: '/news/news_info/export',
    method: 'get',
    params: query
  })
}

//qury detail
export function getNews(newsId) {
  return request({
    url: '/news/news_info/' + newsId,
    method: 'get'
  })
  }