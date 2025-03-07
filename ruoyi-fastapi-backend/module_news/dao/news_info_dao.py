from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_news.entity.do.news_info_do import NewsInfo
from module_news.entity.vo.news_info_vo import News_infoModel, News_infoPageQueryModel
from utils.page_util import PageUtil


class News_infoDao:
    """
    新闻信息模块数据库操作层
    """

    @classmethod
    async def get_news_info_detail_by_id(cls, db: AsyncSession, news_id: int):
        """
        根据新闻编号获取新闻信息详细信息

        :param db: orm对象
        :param news_id: 新闻编号
        :return: 新闻信息信息对象
        """
        news_info_info = (
            (
                await db.execute(
                    select(NewsInfo)
                    .where(
                        NewsInfo.news_id == news_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_info_info

    @classmethod
    async def get_news_info_detail_by_info(cls, db: AsyncSession, news_info: News_infoModel):
        """
        根据新闻信息参数获取新闻信息信息

        :param db: orm对象
        :param news_info: 新闻信息参数对象
        :return: 新闻信息信息对象
        """
        news_info_info = (
            (
                await db.execute(
                    select(NewsInfo).where(
                        NewsInfo.user_id == news_info.user_id if news_info.user_id else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_info_info

    @classmethod
    async def get_news_info_list(cls, db: AsyncSession, query_object: News_infoPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取新闻信息列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻信息列表信息对象
        """
        query = (
            select(NewsInfo)
            .where(
                NewsInfo.news_content == query_object.news_content if query_object.news_content else True,
                NewsInfo.user_id == query_object.user_id if query_object.user_id else True,
                NewsInfo.news_title == query_object.news_title if query_object.news_title else True,
            )
            .order_by(NewsInfo.news_id)
            .distinct()
        )
        news_info_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return news_info_list

    @classmethod
    async def add_news_info_dao(cls, db: AsyncSession, news_info: News_infoModel):
        """
        新增新闻信息数据库操作

        :param db: orm对象
        :param news_info: 新闻信息对象
        :return:
        """
        db_news_info = NewsInfo(**news_info.model_dump(exclude={}))
        db.add(db_news_info)
        await db.flush()

        return db_news_info

    @classmethod
    async def edit_news_info_dao(cls, db: AsyncSession, news_info: dict):
        """
        编辑新闻信息数据库操作

        :param db: orm对象
        :param news_info: 需要更新的新闻信息字典
        :return:
        """
        await db.execute(update(NewsInfo), [news_info])

    @classmethod
    async def delete_news_info_dao(cls, db: AsyncSession, news_info: News_infoModel):
        """
        删除新闻信息数据库操作

        :param db: orm对象
        :param news_info: 新闻信息对象
        :return:
        """
        await db.execute(delete(NewsInfo).where(NewsInfo.news_id.in_([news_info.news_id])))

