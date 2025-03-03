
import request from '@/utils/request'




export function uploadSingleNew(fileId) {
  return request({
    url: 'tool/news',  // 替换为实际文件信息接口
    method: 'get'
  })
}