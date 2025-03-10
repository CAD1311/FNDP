import request from '@/utils/request'

// 查询新闻信息列表
export function listNews_info(query) {
  return request({
    url: '/news/news_info/list',
    method: 'get',
    params: query
  })
}

// 查询新闻信息详细
export function getNews_info(newsId) {
  return request({
    url: '/news/news_info/' + newsId,
    method: 'get'
  })
}

// 新增新闻信息
export function addNews_info(data) {
  return request({
    url: '/news/news_info',
    method: 'post',
    data: data
  })
}

// 修改新闻信息
export function updateNews_info(data) {
  return request({
    url: '/news/news_info',
    method: 'put',
    data: data
  })
}

// 删除新闻信息
export function delNews_info(newsId) {
  return request({
    url: '/news/news_info/' + newsId,
    method: 'delete'
  })
}


// 检测新闻信息
export function checkNews_info(newsIds) {
  return request({
    url: '/news/news_info/check',
    method: 'post',
    data: newsIds
  });
}
