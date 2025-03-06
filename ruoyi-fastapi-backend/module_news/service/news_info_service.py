from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_news.dao.news_info_dao import News_infoDao
from module_news.entity.vo.news_info_vo import DeleteNews_infoModel, News_infoModel, News_infoPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class News_infoService:
    """
    新闻信息模块服务层
    """

    @classmethod
    async def get_news_info_list_services(
        cls, query_db: AsyncSession, query_object: News_infoPageQueryModel, is_page: bool = False
    ):
        """
        获取新闻信息列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻信息列表信息对象
        """
        news_info_list_result = await News_infoDao.get_news_info_list(query_db, query_object, is_page)

        return news_info_list_result


    @classmethod
    async def add_news_info_services(cls, query_db: AsyncSession, page_object: News_infoModel):
        """
        新增新闻信息信息service

        :param query_db: orm对象
        :param page_object: 新增新闻信息对象
        :return: 新增新闻信息校验结果
        """
        try:
            await News_infoDao.add_news_info_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_news_info_services(cls, query_db: AsyncSession, page_object: News_infoModel):
        """
        编辑新闻信息信息service

        :param query_db: orm对象
        :param page_object: 编辑新闻信息对象
        :return: 编辑新闻信息校验结果
        """
        edit_news_info = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        news_info_info = await cls.news_info_detail_services(query_db, page_object.news_id)
        if news_info_info.news_id:
            try:
                await News_infoDao.edit_news_info_dao(query_db, edit_news_info)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='新闻信息不存在')

    @classmethod
    async def delete_news_info_services(cls, query_db: AsyncSession, page_object: DeleteNews_infoModel):
        """
        删除新闻信息信息service

        :param query_db: orm对象
        :param page_object: 删除新闻信息对象
        :return: 删除新闻信息校验结果
        """
        if page_object.news_ids:
            news_id_list = page_object.news_ids.split(',')
            try:
                for news_id in news_id_list:
                    await News_infoDao.delete_news_info_dao(query_db, News_infoModel(newsId=news_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入新闻编号为空')

    @classmethod
    async def news_info_detail_services(cls, query_db: AsyncSession, news_id: int):
        """
        获取新闻信息详细信息service

        :param query_db: orm对象
        :param news_id: 新闻编号
        :return: 新闻编号对应的信息
        """
        news_info = await News_infoDao.get_news_info_detail_by_id(query_db, news_id=news_id)
        if news_info:
            result = News_infoModel(**CamelCaseUtil.transform_result(news_info))
        else:
            result = News_infoModel(**dict())

        return result

    @staticmethod
    async def export_news_info_list_services(news_info_list: List):
        """
        导出新闻信息信息service

        :param news_info_list: 新闻信息信息列表
        :return: 新闻信息信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'newsId': '新闻编号',
            'newsContent': '新闻内容',
            'userId': '用户编号',
            'newsTitle': '新闻标题',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'createBy': '创建者',
            'createTime': '创建时间',
            'publishTime': '发布时间',
            'platform': '平台',
            'hashTag': '类别',
            'url': '链接',
        }
        binary_data = ExcelUtil.export_list2excel(news_info_list, mapping_dict)

        return binary_data
