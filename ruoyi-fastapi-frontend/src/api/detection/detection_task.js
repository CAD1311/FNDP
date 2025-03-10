import request from '@/utils/request'

// 查询新闻检测列表
export function listDetection_task(query) {
  return request({
    url: '/detection/detection_task/list',
    method: 'get',
    params: query
  })
}

// 查询新闻检测详细
export function getDetection_task(taskId) {
  return request({
    url: '/detection/detection_task/' + taskId,
    method: 'get'
  })
}

// 新增新闻检测
export function addDetection_task(data) {
  return request({
    url: '/detection/detection_task',
    method: 'post',
    data: data
  })
}

// 修改新闻检测
export function updateDetection_task(data) {
  return request({
    url: '/detection/detection_task',
    method: 'put',
    data: data
  })
}

// 删除新闻检测
export function delDetection_task(taskId) {
  return request({
    url: '/detection/detection_task/' + taskId,
    method: 'delete'
  })
}
