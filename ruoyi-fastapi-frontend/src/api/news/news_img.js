import request from '@/utils/request'

// 查询新闻图片列表
export function listNews_img(query) {
  return request({
    url: '/news/news_img/list',
    method: 'get',
    params: query
  })
}

// 查询新闻图片详细
export function getNews_img(imgId) {
  return request({
    url: '/news/news_img/' + imgId,
    method: 'get'
  })
}

// 新增新闻图片
export function addNews_img(data) {
  return request({
    url: '/news/news_img',
    method: 'post',
    data: data
  })
}

// 修改新闻图片
export function updateNews_img(data) {
  return request({
    url: '/news/news_img',
    method: 'put',
    data: data
  })
}

// 删除新闻图片
export function delNews_img(imgId) {
  return request({
    url: '/news/news_img/' + imgId,
    method: 'delete'
  })
}
