from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_news.service.news_img_service import News_imgService
from module_news.entity.vo.news_img_vo import DeleteNews_imgModel, News_imgModel, News_imgPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


news_imgController = APIRouter(prefix='/news/news_img', dependencies=[Depends(LoginService.get_current_user)])


@news_imgController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news_img:list'))]
)
async def get_news_news_img_list(
    request: Request,
news_img_page_query: News_imgPageQueryModel = Depends(News_imgPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    news_img_page_query_result = await News_imgService.get_news_img_list_services(query_db, news_img_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=news_img_page_query_result)


@news_imgController.post('', dependencies=[Depends(CheckUserInterfaceAuth('news:news_img:add'))])
@ValidateFields(validate_model='add_news_img')
@Log(title='新闻图片', business_type=BusinessType.INSERT)
async def add_news_news_img(
    request: Request,
    add_news_img: News_imgModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_news_img_result = await News_imgService.add_news_img_services(query_db, add_news_img)
    logger.info(add_news_img_result.message)

    return ResponseUtil.success(msg=add_news_img_result.message)


@news_imgController.put('', dependencies=[Depends(CheckUserInterfaceAuth('news:news_img:edit'))])
@ValidateFields(validate_model='edit_news_img')
@Log(title='新闻图片', business_type=BusinessType.UPDATE)
async def edit_news_news_img(
    request: Request,
    edit_news_img: News_imgModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_news_img.update_by = current_user.user.user_name
    edit_news_img.update_time = datetime.now()
    edit_news_img_result = await News_imgService.edit_news_img_services(query_db, edit_news_img)
    logger.info(edit_news_img_result.message)

    return ResponseUtil.success(msg=edit_news_img_result.message)


@news_imgController.delete('/{img_ids}', dependencies=[Depends(CheckUserInterfaceAuth('news:news_img:remove'))])
@Log(title='新闻图片', business_type=BusinessType.DELETE)
async def delete_news_news_img(request: Request, img_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_news_img = DeleteNews_imgModel(imgIds=img_ids)
    delete_news_img_result = await News_imgService.delete_news_img_services(query_db, delete_news_img)
    logger.info(delete_news_img_result.message)

    return ResponseUtil.success(msg=delete_news_img_result.message)


@news_imgController.get(
    '/{img_id}', response_model=News_imgModel, dependencies=[Depends(CheckUserInterfaceAuth('news:news_img:query'))]
)
async def query_detail_news_news_img(request: Request, img_id: int, query_db: AsyncSession = Depends(get_db)):
    news_img_detail_result = await News_imgService.news_img_detail_services(query_db, img_id)
    logger.info(f'获取img_id为{img_id}的信息成功')

    return ResponseUtil.success(data=news_img_detail_result)


@news_imgController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('news:news_img:export'))])
@Log(title='新闻图片', business_type=BusinessType.EXPORT)
async def export_news_news_img_list(
    request: Request,
    news_img_page_query: News_imgPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    news_img_query_result = await News_imgService.get_news_img_list_services(query_db, news_img_page_query, is_page=False)
    news_img_export_result = await News_imgService.export_news_img_list_services(news_img_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(news_img_export_result))
