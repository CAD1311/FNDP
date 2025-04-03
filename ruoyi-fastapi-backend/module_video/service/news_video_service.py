from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_video.dao.news_video_dao import News_videoDao
from module_video.entity.vo.news_video_vo import DeleteNews_videoModel, News_videoModel, News_videoPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class News_videoService:
    """
    新闻视频模块服务层
    """

    @classmethod
    async def get_news_video_list_services(
        cls, query_db: AsyncSession, query_object: News_videoPageQueryModel, is_page: bool = False
    ):
        """
        获取新闻视频列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻视频列表信息对象
        """
        news_video_list_result = await News_videoDao.get_news_video_list(query_db, query_object, is_page)

        return news_video_list_result


    @classmethod
    async def add_news_video_services(cls, query_db: AsyncSession, page_object: News_videoModel):
        """
        新增新闻视频信息service

        :param query_db: orm对象
        :param page_object: 新增新闻视频对象
        :return: 新增新闻视频校验结果
        """
        try:
            await News_videoDao.add_news_video_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_news_video_services(cls, query_db: AsyncSession, page_object: News_videoModel):
        """
        编辑新闻视频信息service

        :param query_db: orm对象
        :param page_object: 编辑新闻视频对象
        :return: 编辑新闻视频校验结果
        """
        edit_news_video = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        news_video_info = await cls.news_video_detail_services(query_db, page_object.video_id)
        if news_video_info.video_id:
            try:
                await News_videoDao.edit_news_video_dao(query_db, edit_news_video)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='新闻视频不存在')

    @classmethod
    async def delete_news_video_services(cls, query_db: AsyncSession, page_object: DeleteNews_videoModel):
        """
        删除新闻视频信息service

        :param query_db: orm对象
        :param page_object: 删除新闻视频对象
        :return: 删除新闻视频校验结果
        """
        if page_object.video_ids:
            video_id_list = page_object.video_ids.split(',')
            try:
                for video_id in video_id_list:
                    await News_videoDao.delete_news_video_dao(query_db, News_videoModel(videoId=video_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入视频编号为空')

    @classmethod
    async def news_video_detail_services(cls, query_db: AsyncSession, video_id: int):
        """
        获取新闻视频详细信息service

        :param query_db: orm对象
        :param video_id: 视频编号
        :return: 视频编号对应的信息
        """
        news_video = await News_videoDao.get_news_video_detail_by_id(query_db, video_id=video_id)
        if news_video:
            result = News_videoModel(**CamelCaseUtil.transform_result(news_video))
        else:
            result = News_videoModel(**dict())

        return result

    @staticmethod
    async def export_news_video_list_services(news_video_list: List):
        """
        导出新闻视频信息service

        :param news_video_list: 新闻视频信息列表
        :return: 新闻视频信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'videoId': '视频编号',
            'newsId': '新闻编号',
            'videoData': '视频数据',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
        }
        binary_data = ExcelUtil.export_list2excel(news_video_list, mapping_dict)

        return binary_data
