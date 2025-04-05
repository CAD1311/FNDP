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
from module_video.service.news_video_service import News_videoService
from module_video.entity.vo.news_video_vo import DeleteNews_videoModel, News_videoModel, News_videoPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


news_videoController = APIRouter(prefix='/news/news_video', dependencies=[Depends(LoginService.get_current_user)])


@news_videoController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news_video:list'))]
)
async def get_news_news_video_list(
    request: Request,
news_video_page_query: News_videoPageQueryModel = Depends(News_videoPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    news_video_page_query_result = await News_videoService.get_news_video_list_services(query_db, news_video_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=news_video_page_query_result)


@news_videoController.post('', dependencies=[Depends(CheckUserInterfaceAuth('news:news_video:add'))])
@ValidateFields(validate_model='add_news_video')
@Log(title='新闻视频', business_type=BusinessType.INSERT)
async def add_news_news_video(
    request: Request,
    add_news_video: News_videoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_news_video.create_by = current_user.user.user_name
    add_news_video.create_time = datetime.now()
    add_news_video.update_by = current_user.user.user_name
    add_news_video.update_time = datetime.now()
    add_news_video_result = await News_videoService.add_news_video_services(query_db, add_news_video)
    logger.info(add_news_video_result.message)

    return ResponseUtil.success(msg=add_news_video_result.message)


@news_videoController.put('', dependencies=[Depends(CheckUserInterfaceAuth('news:news_video:edit'))])
@ValidateFields(validate_model='edit_news_video')
@Log(title='新闻视频', business_type=BusinessType.UPDATE)
async def edit_news_news_video(
    request: Request,
    edit_news_video: News_videoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_news_video.update_by = current_user.user.user_name
    edit_news_video.update_time = datetime.now()
    edit_news_video_result = await News_videoService.edit_news_video_services(query_db, edit_news_video)
    logger.info(edit_news_video_result.message)

    return ResponseUtil.success(msg=edit_news_video_result.message)


@news_videoController.delete('/{video_ids}', dependencies=[Depends(CheckUserInterfaceAuth('news:news_video:remove'))])
@Log(title='新闻视频', business_type=BusinessType.DELETE)
async def delete_news_news_video(request: Request, video_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_news_video = DeleteNews_videoModel(videoIds=video_ids)
    delete_news_video_result = await News_videoService.delete_news_video_services(query_db, delete_news_video)
    logger.info(delete_news_video_result.message)

    return ResponseUtil.success(msg=delete_news_video_result.message)


@news_videoController.get(
    '/{video_id}', response_model=News_videoModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news_video:query'))]
)
async def query_detail_news_news_video(request: Request, video_id: int, query_db: AsyncSession = Depends(get_db)):
    news_video_detail_result = await News_videoService.news_video_detail_services(query_db, video_id)
    logger.info(f'获取video_id为{video_id}的信息成功')

    return ResponseUtil.success(data=news_video_detail_result)


@news_videoController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('news:news_video:export'))])
@Log(title='新闻视频', business_type=BusinessType.EXPORT)
async def export_news_news_video_list(
    request: Request,
    news_video_page_query: News_videoPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    news_video_query_result = await News_videoService.get_news_video_list_services(query_db, news_video_page_query, is_page=False)
    news_video_export_result = await News_videoService.export_news_video_list_services(news_video_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(news_video_export_result))
