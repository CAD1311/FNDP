from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_img.dao.news_img_dao import News_imgDao
from module_img.entity.vo.news_img_vo import DeleteNews_imgModel, News_imgModel, News_imgPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class News_imgService:
    """
    新闻图片模块服务层
    """

    @classmethod
    async def get_news_img_list_services(
        cls, query_db: AsyncSession, query_object: News_imgPageQueryModel, is_page: bool = False
    ):
        """
        获取新闻图片列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻图片列表信息对象
        """
        news_img_list_result = await News_imgDao.get_news_img_list(query_db, query_object, is_page)

        return news_img_list_result


    @classmethod
    async def add_news_img_services(cls, query_db: AsyncSession, page_object: News_imgModel):
        """
        新增新闻图片信息service

        :param query_db: orm对象
        :param page_object: 新增新闻图片对象
        :return: 新增新闻图片校验结果
        """
        try:
            await News_imgDao.add_news_img_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_news_img_services(cls, query_db: AsyncSession, page_object: News_imgModel):
        """
        编辑新闻图片信息service

        :param query_db: orm对象
        :param page_object: 编辑新闻图片对象
        :return: 编辑新闻图片校验结果
        """
        edit_news_img = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time'})
        news_img_info = await cls.news_img_detail_services(query_db, page_object.img_id)
        if news_img_info.img_id:
            try:
                await News_imgDao.edit_news_img_dao(query_db, edit_news_img)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='新闻图片不存在')

    @classmethod
    async def delete_news_img_services(cls, query_db: AsyncSession, page_object: DeleteNews_imgModel):
        """
        删除新闻图片信息service

        :param query_db: orm对象
        :param page_object: 删除新闻图片对象
        :return: 删除新闻图片校验结果
        """
        if page_object.img_ids:
            img_id_list = page_object.img_ids.split(',')
            try:
                for img_id in img_id_list:
                    await News_imgDao.delete_news_img_dao(query_db, News_imgModel(imgId=img_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入图片编号为空')

    @classmethod
    async def news_img_detail_services(cls, query_db: AsyncSession, img_id: int):
        """
        获取新闻图片详细信息service

        :param query_db: orm对象
        :param img_id: 图片编号
        :return: 图片编号对应的信息
        """
        news_img = await News_imgDao.get_news_img_detail_by_id(query_db, img_id=img_id)
        if news_img:
            result = News_imgModel(**CamelCaseUtil.transform_result(news_img))
        else:
            result = News_imgModel(**dict())

        return result

    @staticmethod
    async def export_news_img_list_services(news_img_list: List):
        """
        导出新闻图片信息service

        :param news_img_list: 新闻图片信息列表
        :return: 新闻图片信息对应excel的二进制数据
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
        binary_data = ExcelUtil.export_list2excel(news_img_list, mapping_dict)

        return binary_data
