from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_news.service.news_service import NewsService
from module_news.entity.vo.news_vo import DeleteNewsModel, NewsModel, NewsPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil
import datetime


newsController = APIRouter(prefix='/news/news', dependencies=[Depends(LoginService.get_current_user)])


@newsController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news:list'))]
)
async def get_news_news_list(
    request: Request,
news_page_query: NewsPageQueryModel = Depends(NewsPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    news_page_query_result = await NewsService.get_news_list_services(query_db, news_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=news_page_query_result)


@newsController.post('', dependencies=[Depends(CheckUserInterfaceAuth('news:news:add'))])
@ValidateFields(validate_model='add_news')
@Log(title='新闻信息', business_type=BusinessType.INSERT)
async def add_news_news(
    request: Request,
    add_news: NewsModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_news_result = await NewsService.add_news_services(query_db, add_news)
    logger.info(add_news_result.message)

    return ResponseUtil.success(msg=add_news_result.message)


@newsController.put('', dependencies=[Depends(CheckUserInterfaceAuth('news:news:edit'))])
@ValidateFields(validate_model='edit_news')
@Log(title='新闻信息', business_type=BusinessType.UPDATE)
async def edit_news_news(
    request: Request,
    edit_news: NewsModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_news.update_by = current_user.user.user_name
    edit_news.update_time = datetime.now()
    edit_news_result = await NewsService.edit_news_services(query_db, edit_news)
    logger.info(edit_news_result.message)

    return ResponseUtil.success(msg=edit_news_result.message)


@newsController.delete('/{news_ids}', dependencies=[Depends(CheckUserInterfaceAuth('news:news:remove'))])
@Log(title='新闻信息', business_type=BusinessType.DELETE)
async def delete_news_news(request: Request, news_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_news = DeleteNewsModel(newsIds=news_ids)
    delete_news_result = await NewsService.delete_news_services(query_db, delete_news)
    logger.info(delete_news_result.message)

    return ResponseUtil.success(msg=delete_news_result.message)


@newsController.get(
    '/{news_id}', response_model=NewsModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news:query'))]
)
async def query_detail_news_news(request: Request, news_id: int, query_db: AsyncSession = Depends(get_db)):
    news_detail_result = await NewsService.news_detail_services(query_db, news_id)
    logger.info(f'获取news_id为{news_id}的信息成功')

    return ResponseUtil.success(data=news_detail_result)


@newsController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('news:news:export'))])
@Log(title='新闻信息', business_type=BusinessType.EXPORT)
async def export_news_news_list(
    request: Request,
    news_page_query: NewsPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    news_query_result = await NewsService.get_news_list_services(query_db, news_page_query, is_page=False)
    news_export_result = await NewsService.export_news_list_services(news_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(news_export_result))
