from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from module_news.entity.do.news_do import NewsInfo, NewsImg
from module_news.entity.vo.news_vo import NewsModel, NewsPageQueryModel, News_imgModel
from utils.page_util import PageUtil


class NewsDao:
    """
    新闻信息模块数据库操作层
    """

    @classmethod
    async def get_news_detail_by_id(cls, db: AsyncSession, news_id: int):
        """
        根据获取新闻信息详细信息

        :param db: orm对象
        :param news_id: 
        :return: 新闻信息信息对象
        """
        news_info = (
            (
                await db.execute(
                    select(NewsInfo)
                    .options(selectinload(NewsInfo.newsimg_list))
                    .where(
                        NewsInfo.news_id == news_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_info

    @classmethod
    async def get_news_detail_by_info(cls, db: AsyncSession, news: NewsModel):
        """
        根据新闻信息参数获取新闻信息信息

        :param db: orm对象
        :param news: 新闻信息参数对象
        :return: 新闻信息信息对象
        """
        news_info = (
            (
                await db.execute(
                    select(NewsInfo).where(
                        NewsInfo.user_id == news.user_id if news.user_id else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_info

    @classmethod
    async def get_news_list(cls, db: AsyncSession, query_object: NewsPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取新闻信息列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻信息列表信息对象
        """
        query = (
            select(NewsInfo)
            .options(selectinload(NewsInfo.newsimg_list))
            .where(
                NewsInfo.news_id == query_object.news_id if query_object.news_id else True,
                NewsInfo.news_content == query_object.news_content if query_object.news_content else True,
                NewsInfo.user_id == query_object.user_id if query_object.user_id else True,
            )
            .order_by(NewsInfo.news_id)
            .distinct()
        )
        news_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return news_list

    @classmethod
    async def add_news_dao(cls, db: AsyncSession, news: NewsModel):
        """
        新增新闻信息数据库操作

        :param db: orm对象
        :param news: 新闻信息对象
        :return:
        """
        db_news = NewsInfo(**news.model_dump(exclude={'newsimg_list', }))
        db.add(db_news)
        await db.flush()

        return db_news

    @classmethod
    async def edit_news_dao(cls, db: AsyncSession, news: dict):
        """
        编辑新闻信息数据库操作

        :param db: orm对象
        :param news: 需要更新的新闻信息字典
        :return:
        """
        await db.execute(update(NewsInfo), [news])

    @classmethod
    async def delete_news_dao(cls, db: AsyncSession, news: NewsModel):
        """
        删除新闻信息数据库操作

        :param db: orm对象
        :param news: 新闻信息对象
        :return:
        """
        await db.execute(delete(NewsInfo).where(NewsInfo.news_id.in_([news.news_id])))

    @classmethod
    async def add_news_img_dao(cls, db: AsyncSession, news_img: News_imgModel):
        """
        新增新闻图片数据库操作

        :param db: orm对象
        :param news_img: 新闻图片对象
        :return:
        """
        db_news_img = NewsImg(**news_img.model_dump())
        db.add(db_news_img)
        await db.flush()

        return db_news_img

    @classmethod
    async def edit_news_img_dao(cls, db: AsyncSession, news_img: dict):
        """
        编辑新闻图片数据库操作

        :param db: orm对象
        :param news_img: 需要更新的新闻图片字典
        :return:
        """
        await db.execute(update(NewsImg), [news_img])

    @classmethod
    async def delete_news_img_dao(cls, db: AsyncSession, news_img: News_imgModel):
        """
        删除新闻图片数据库操作

        :param db: orm对象
        :param news_img: 新闻图片对象
        :return:
        """
        await db.execute(delete(NewsImg).where(NewsImg.img_id.in_([news_img.img_id])))
