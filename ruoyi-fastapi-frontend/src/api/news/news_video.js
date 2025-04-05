import request from '@/utils/request'

// 查询新闻视频列表
export function listNews_video(query) {
  return request({
    url: '/news/news_video/list',
    method: 'get',
    params: query
  })
}

// 查询新闻视频详细
export function getNews_video(videoId) {
  return request({
    url: '/news/news_video/' + videoId,
    method: 'get'
  })
}

// 新增新闻视频
export function addNews_video(data) {
  return request({
    url: '/news/news_video',
    method: 'post',
    data: data
  })
}

// 修改新闻视频
export function updateNews_video(data) {
  return request({
    url: '/news/news_video',
    method: 'put',
    data: data
  })
}

// 删除新闻视频
export function delNews_video(videoId) {
  return request({
    url: '/news/news_video/' + videoId,
    method: 'delete'
  })
}
