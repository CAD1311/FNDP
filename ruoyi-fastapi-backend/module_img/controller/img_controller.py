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
from module_img.service.img_service import ImgService
from module_img.entity.vo.img_vo import DeleteImgModel, ImgModel, ImgPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


imgController = APIRouter(prefix='/news/img', dependencies=[Depends(LoginService.get_current_user)])


@imgController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('news:img:list'))]
)
async def get_news_img_list(
    request: Request,
img_page_query: ImgPageQueryModel = Depends(ImgPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    img_page_query_result = await ImgService.get_img_list_services(query_db, img_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=img_page_query_result)


@imgController.post('', dependencies=[Depends(CheckUserInterfaceAuth('news:img:add'))])
@ValidateFields(validate_model='add_img')
@Log(title='news_img', business_type=BusinessType.INSERT)
async def add_news_img(
    request: Request,
    add_img: ImgModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_img.update_by = current_user.user.user_name
    add_img.update_time = datetime.now()
    add_img.create_by = current_user.user.user_name
    add_img.create_time = datetime.now()
    add_img_result = await ImgService.add_img_services(query_db, add_img)
    logger.info(add_img_result.message)

    return ResponseUtil.success(msg=add_img_result.message)


@imgController.put('', dependencies=[Depends(CheckUserInterfaceAuth('news:img:edit'))])
@ValidateFields(validate_model='edit_img')
@Log(title='news_img', business_type=BusinessType.UPDATE)
async def edit_news_img(
    request: Request,
    edit_img: ImgModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_img.update_by = current_user.user.user_name
    edit_img.update_time = datetime.now()
    edit_img_result = await ImgService.edit_img_services(query_db, edit_img)
    logger.info(edit_img_result.message)

    return ResponseUtil.success(msg=edit_img_result.message)


@imgController.delete('/{img_ids}', dependencies=[Depends(CheckUserInterfaceAuth('news:img:remove'))])
@Log(title='news_img', business_type=BusinessType.DELETE)
async def delete_news_img(request: Request, img_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_img = DeleteImgModel(imgIds=img_ids)
    delete_img_result = await ImgService.delete_img_services(query_db, delete_img)
    logger.info(delete_img_result.message)

    return ResponseUtil.success(msg=delete_img_result.message)


@imgController.get(
    '/{img_id}', response_model=ImgModel, dependencies=[Depends(CheckUserInterfaceAuth('news:img:query'))]
)
async def query_detail_news_img(request: Request, img_id: int, query_db: AsyncSession = Depends(get_db)):
    img_detail_result = await ImgService.img_detail_services(query_db, img_id)
    logger.info(f'获取img_id为{img_id}的信息成功')

    return ResponseUtil.success(data=img_detail_result)


@imgController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('news:img:export'))])
@Log(title='news_img', business_type=BusinessType.EXPORT)
async def export_news_img_list(
    request: Request,
    img_page_query: ImgPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    img_query_result = await ImgService.get_img_list_services(query_db, img_page_query, is_page=False)
    img_export_result = await ImgService.export_img_list_services(img_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(img_export_result))
