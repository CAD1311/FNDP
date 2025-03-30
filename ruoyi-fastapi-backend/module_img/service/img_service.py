from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_img.dao.img_dao import ImgDao
from module_img.entity.vo.img_vo import DeleteImgModel, ImgModel, ImgPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class ImgService:
    """
    news_img模块服务层
    """

    @classmethod
    async def get_img_list_services(
        cls, query_db: AsyncSession, query_object: ImgPageQueryModel, is_page: bool = False
    ):
        """
        获取news_img列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: news_img列表信息对象
        """
        img_list_result = await ImgDao.get_img_list(query_db, query_object, is_page)

        return img_list_result


    @classmethod
    async def add_img_services(cls, query_db: AsyncSession, page_object: ImgModel):
        """
        新增news_img信息service

        :param query_db: orm对象
        :param page_object: 新增news_img对象
        :return: 新增news_img校验结果
        """
        try:
            await ImgDao.add_img_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_img_services(cls, query_db: AsyncSession, page_object: ImgModel):
        """
        编辑news_img信息service

        :param query_db: orm对象
        :param page_object: 编辑news_img对象
        :return: 编辑news_img校验结果
        """
        edit_img = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time'})
        img_info = await cls.img_detail_services(query_db, page_object.img_id)
        if img_info.img_id:
            try:
                await ImgDao.edit_img_dao(query_db, edit_img)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='news_img不存在')

    @classmethod
    async def delete_img_services(cls, query_db: AsyncSession, page_object: DeleteImgModel):
        """
        删除news_img信息service

        :param query_db: orm对象
        :param page_object: 删除news_img对象
        :return: 删除news_img校验结果
        """
        if page_object.img_ids:
            img_id_list = page_object.img_ids.split(',')
            try:
                for img_id in img_id_list:
                    await ImgDao.delete_img_dao(query_db, ImgModel(imgId=img_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入图片编号为空')

    @classmethod
    async def img_detail_services(cls, query_db: AsyncSession, img_id: int):
        """
        获取news_img详细信息service

        :param query_db: orm对象
        :param img_id: 图片编号
        :return: 图片编号对应的信息
        """
        img = await ImgDao.get_img_detail_by_id(query_db, img_id=img_id)
        if img:
            result = ImgModel(**CamelCaseUtil.transform_result(img))
        else:
            result = ImgModel(**dict())

        return result

    @staticmethod
    async def export_img_list_services(img_list: List):
        """
        导出news_img信息service

        :param img_list: news_img信息列表
        :return: news_img信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'imgId': '图片编号',
            'newsId': '新闻编号',
            'imgData': '图片数据',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'createBy': '创建者',
            'createTime': '创建时间',
        }
        binary_data = ExcelUtil.export_list2excel(img_list, mapping_dict)

        return binary_data
