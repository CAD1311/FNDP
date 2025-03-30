import request from '@/utils/request'

// 查询news_img列表
export function listImg(query) {
  return request({
    url: '/news/img/list',
    method: 'get',
    params: query
  })
}

// 查询news_img详细
export function getImg(imgId) {
  return request({
    url: '/news/img/' + imgId,
    method: 'get'
  })
}

// 新增news_img
export function addImg(data) {
  return request({
    url: '/news/img',
    method: 'post',
    data: data
  })
}

// 修改news_img
export function updateImg(data) {
  return request({
    url: '/news/img',
    method: 'put',
    data: data
  })
}

// 删除news_img
export function delImg(imgId) {
  return request({
    url: '/news/img/' + imgId,
    method: 'delete'
  })
}
