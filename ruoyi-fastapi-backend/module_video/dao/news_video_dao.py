from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_video.entity.do.news_video_do import NewsVideo
from module_video.entity.vo.news_video_vo import News_videoModel, News_videoPageQueryModel
from utils.page_util import PageUtil


class News_videoDao:
    """
    新闻视频模块数据库操作层
    """

    @classmethod
    async def get_news_video_detail_by_id(cls, db: AsyncSession, video_id: int):
        """
        根据视频编号获取新闻视频详细信息

        :param db: orm对象
        :param video_id: 视频编号
        :return: 新闻视频信息对象
        """
        news_video_info = (
            (
                await db.execute(
                    select(NewsVideo)
                    .where(
                        NewsVideo.video_id == video_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_video_info

    @classmethod
    async def get_news_video_detail_by_info(cls, db: AsyncSession, news_video: News_videoModel):
        """
        根据新闻视频参数获取新闻视频信息

        :param db: orm对象
        :param news_video: 新闻视频参数对象
        :return: 新闻视频信息对象
        """
        news_video_info = (
            (
                await db.execute(
                    select(NewsVideo).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_video_info

    @classmethod
    async def get_news_video_list(cls, db: AsyncSession, query_object: News_videoPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取新闻视频列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻视频列表信息对象
        """
        query = (
            select(NewsVideo)
            .where(
                NewsVideo.news_id == query_object.news_id if query_object.news_id else True,
                NewsVideo.video_data == query_object.video_data if query_object.video_data else True,
                NewsVideo.create_by == query_object.create_by if query_object.create_by else True,
                NewsVideo.create_time == query_object.create_time if query_object.create_time else True,
                NewsVideo.update_by == query_object.update_by if query_object.update_by else True,
                NewsVideo.update_time == query_object.update_time if query_object.update_time else True,
            )
            .order_by(NewsVideo.video_id)
            .distinct()
        )
        news_video_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return news_video_list

    @classmethod
    async def add_news_video_dao(cls, db: AsyncSession, news_video: News_videoModel):
        """
        新增新闻视频数据库操作

        :param db: orm对象
        :param news_video: 新闻视频对象
        :return:
        """
        db_news_video = NewsVideo(**news_video.model_dump(exclude={}))
        db.add(db_news_video)
        await db.flush()

        return db_news_video

    @classmethod
    async def edit_news_video_dao(cls, db: AsyncSession, news_video: dict):
        """
        编辑新闻视频数据库操作

        :param db: orm对象
        :param news_video: 需要更新的新闻视频字典
        :return:
        """
        await db.execute(update(NewsVideo), [news_video])

    @classmethod
    async def delete_news_video_dao(cls, db: AsyncSession, news_video: News_videoModel):
        """
        删除新闻视频数据库操作

        :param db: orm对象
        :param news_video: 新闻视频对象
        :return:
        """
        await db.execute(delete(NewsVideo).where(NewsVideo.video_id.in_([news_video.video_id])))

