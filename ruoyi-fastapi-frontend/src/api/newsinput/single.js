
import request from '@/utils/request'


// json
export function getJSON() {
  return request({
    url: '/tool/news',
    headers: {
      isToken: false
    },
    method: 'get',
    timeout: 20000
  })
}