from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_news.entity.do.news_info_do import NewsInfo
from module_news.entity.vo.news_info_vo import News_infoModel, News_infoPageQueryModel
from utils.page_util import PageUtil
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json

class News_infoDao:
    """
    新闻信息模块数据库操作层
    """

    @classmethod
    async def get_news_info_detail_by_id(cls, db: AsyncSession, news_id: int, redis: aioredis.Redis = None):
        """
        根据新闻编号获取新闻信息详细信息

        :param db: orm对象
        :param news_id: 新闻编号
        :param redis: Redis连接对象
        :return: 新闻信息信息对象
        """
        if redis is not None:
            cache_key = f"news_info:{news_id}"
            cached_data = await redis.get(cache_key)
            if cached_data:
                return NewsInfo(**json.loads(cached_data))
        
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

        if redis is not None and news_info_info is not None:
            await redis.setex(cache_key, 3600, json.dumps(news_info_info.__dict__))
        
        return news_info_info


    @classmethod
    async def get_news_info_by_ids(
        cls, 
        db: AsyncSession, 
        news_ids: list[int],
        redis: aioredis.Redis = None
    ) -> list[NewsInfo]:
        """
        批量获取新闻信息（优先使用 Redis 缓存）
        """
        if not redis:
            return await cls._get_news_info_by_ids_db(db, news_ids)
        
        # 1. 构建缓存键并批量查询
        cache_keys = [f"news_info:{nid}" for nid in news_ids]
        cached_data = await redis.mget(cache_keys)
        
        # 2. 分离命中和未命中的 news_id
        cached_dict = {}
        missed_ids = []
        for nid, data in zip(news_ids, cached_data):
            if data:
                cached_dict[nid] = NewsInfo(**json.loads(data))
            else:
                missed_ids.append(nid)
        
        # 3. 回源查询未命中的数据
        if missed_ids:
            db_news = await cls._get_news_info_by_ids_db(db, missed_ids)
            # 写入缓存（使用 Pipeline 减少网络延迟）[[3]][[5]]
            async with redis.pipeline() as pipe:
                for news in db_news:
                    key = f"news_info:{news.news_id}"
                    pipe.setex(key, 3600, json.dumps(news.__dict__))
                await pipe.execute()
            cached_dict.update({news.news_id: news for news in db_news})
        
        # 4. 按输入顺序返回结果
        return [cached_dict.get(nid) for nid in news_ids]
    
    @classmethod
    async def _get_news_info_by_ids_db(cls, db: AsyncSession, news_ids: list[int]):
        """数据库批量查询实现"""
        result = await db.execute(select(NewsInfo).where(NewsInfo.news_id.in_(news_ids)))
        return result.scalars().all()
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

