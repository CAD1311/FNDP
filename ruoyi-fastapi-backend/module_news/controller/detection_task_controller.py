from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_news.service.news_info_service import News_infoService
from module_news.service.detection_task_service import Detection_taskService
from module_news.entity.vo.detection_task_vo import DeleteDetection_taskModel, Detection_taskModel, Detection_taskPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil
from pydantic import BaseModel



# 添加一个函数来获取服务实例
def get_detection_service(request: Request) -> Detection_taskService:
    return request.app.state.detection_service

detection_taskController = APIRouter(prefix='/detection/detection_task', dependencies=[Depends(LoginService.get_current_user)])


@detection_taskController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('detection:detection_task:list'))]
)
async def get_detection_detection_task_list(
    request: Request,
detection_task_page_query: Detection_taskPageQueryModel = Depends(Detection_taskPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    detection_task_page_query_result = await Detection_taskService.get_detection_task_list_services(query_db, detection_task_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=detection_task_page_query_result)



class NewsDetectionRequest(BaseModel):
    news_ids: list[int]


@detection_taskController.post('', dependencies=[Depends(CheckUserInterfaceAuth('detection:detection_task:add'))])
@Log(title='新闻检测', business_type=BusinessType.OTHER)
async def detect_news_news_info(
    params: NewsDetectionRequest,
    request: Request,
    query_db: AsyncSession = Depends(get_db),   
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    service: Detection_taskService = Depends(get_detection_service),  # 从请求中获取服务实例
):
    news_ids = params.news_ids
    add_detection_tasks = []
    if news_ids:
        for news_id in news_ids:
            news_info = await News_infoService.news_info_detail_services(query_db, news_id)
            if news_info:
                add_detection_task = Detection_taskModel() 
                add_detection_task.update_by = current_user.user.user_name
                add_detection_task.update_time = datetime.now()
                add_detection_task.create_by = current_user.user.user_name
                add_detection_task.create_time = datetime.now()
                add_detection_task.task_status = 0
                add_detection_task.user_id = current_user.user.user_id
                add_detection_task.news_id = news_id
                add_detection_task.task_result = ''
                add_detection_task.is_true = 0
                #add_detection_task_result = await Detection_taskService.add_detection_task_services(query_db, add_detection_task)
                add_detection_tasks.append(add_detection_task)
        
        await service.detection_task_start_services(query_db, add_detection_tasks)

    return ResponseUtil.success(msg="检测完成")



@detection_taskController.delete('/{task_ids}', dependencies=[Depends(CheckUserInterfaceAuth('detection:detection_task:remove'))])
@Log(title='新闻检测', business_type=BusinessType.DELETE)
async def delete_detection_detection_task(request: Request, task_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_detection_task = DeleteDetection_taskModel(taskIds=task_ids)
    delete_detection_task_result = await Detection_taskService.delete_detection_task_services(query_db, delete_detection_task)
    logger.info(delete_detection_task_result.message)

    return ResponseUtil.success(msg=delete_detection_task_result.message)


@detection_taskController.get(
    '/{task_id}', response_model=Detection_taskModel, dependencies=[Depends(CheckUserInterfaceAuth('detection:detection_task:query'))]
)
async def query_detail_detection_detection_task(request: Request, task_id: int, query_db: AsyncSession = Depends(get_db)):
    detection_task_detail_result = await Detection_taskService.detection_task_detail_services(query_db, task_id)
    logger.info(f'获取task_id为{task_id}的信息成功')

    return ResponseUtil.success(data=detection_task_detail_result)


@detection_taskController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('detection:detection_task:export'))])
@Log(title='新闻检测', business_type=BusinessType.EXPORT)
async def export_detection_detection_task_list(
    request: Request,
    detection_task_page_query: Detection_taskPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    detection_task_query_result = await Detection_taskService.get_detection_task_list_services(query_db, detection_task_page_query, is_page=False)
    detection_task_export_result = await Detection_taskService.export_detection_task_list_services(detection_task_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(detection_task_export_result))


@detection_taskController.post('/quick')
@Log(title='快速检测', business_type=BusinessType.OTHER)
async def quick_detect_news_news_info(
    text: str,
    service: Detection_taskService = Depends(get_detection_service),
):
    return service.quick_start_services(text)