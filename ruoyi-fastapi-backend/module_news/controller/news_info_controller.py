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
from module_news.entity.vo.news_info_vo import DeleteNews_infoModel, News_infoModel, News_infoPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil
import datetime


news_infoController = APIRouter(prefix='/news/news_info', dependencies=[Depends(LoginService.get_current_user)])


@news_infoController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news_info:list'))]
)
async def get_news_news_info_list(
    request: Request,
news_info_page_query: News_infoPageQueryModel = Depends(News_infoPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    news_info_page_query_result = await News_infoService.get_news_info_list_services(query_db, news_info_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=news_info_page_query_result)


@news_infoController.post('', dependencies=[Depends(CheckUserInterfaceAuth('news:news_info:add'))])
@ValidateFields(validate_model='add_news_info')
@Log(title='新闻信息', business_type=BusinessType.INSERT)
async def add_news_news_info(
    request: Request,
    add_news_info: News_infoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_news_info_result = await News_infoService.add_news_info_services(query_db, add_news_info)
    logger.info(add_news_info_result.message)

    return ResponseUtil.success(msg=add_news_info_result.message)


@news_infoController.put('', dependencies=[Depends(CheckUserInterfaceAuth('news:news_info:edit'))])
@ValidateFields(validate_model='edit_news_info')
@Log(title='新闻信息', business_type=BusinessType.UPDATE)
async def edit_news_news_info(
    request: Request,
    edit_news_info: News_infoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_news_info.update_by = current_user.user.user_name
    edit_news_info.update_time = datetime.now()
    edit_news_info_result = await News_infoService.edit_news_info_services(query_db, edit_news_info)
    logger.info(edit_news_info_result.message)

    return ResponseUtil.success(msg=edit_news_info_result.message)


@news_infoController.delete('/{news_ids}', dependencies=[Depends(CheckUserInterfaceAuth('news:news_info:remove'))])
@Log(title='新闻信息', business_type=BusinessType.DELETE)
async def delete_news_news_info(request: Request, news_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_news_info = DeleteNews_infoModel(newsIds=news_ids)
    delete_news_info_result = await News_infoService.delete_news_info_services(query_db, delete_news_info)
    logger.info(delete_news_info_result.message)

    return ResponseUtil.success(msg=delete_news_info_result.message)


@news_infoController.get(
    '/{news_id}', response_model=News_infoModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news_info:query'))]
)
async def query_detail_news_news_info(request: Request, news_id: int, query_db: AsyncSession = Depends(get_db)):
    news_info_detail_result = await News_infoService.news_info_detail_services(query_db, news_id)
    logger.info(f'获取news_id为{news_id}的信息成功')

    return ResponseUtil.success(data=news_info_detail_result)


@news_infoController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('news:news_info:export'))])
@Log(title='新闻信息', business_type=BusinessType.EXPORT)
async def export_news_news_info_list(
    request: Request,
    news_info_page_query: News_infoPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    news_info_query_result = await News_infoService.get_news_info_list_services(query_db, news_info_page_query, is_page=False)
    news_info_export_result = await News_infoService.export_news_info_list_services(news_info_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(news_info_export_result))
