from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_img.entity.do.news_img_do import NewsImg
from module_img.entity.vo.news_img_vo import News_imgModel, News_imgPageQueryModel
from utils.page_util import PageUtil
from redis import asyncio as aioredis
from typing import Optional
import json


class News_imgDao:
    """
    新闻图片模块数据库操作层
    """

    @classmethod
    async def get_news_img_detail_by_id(cls, db: AsyncSession, img_id: int):
        """
        根据图片编号获取新闻图片详细信息

        :param db: orm对象
        :param img_id: 图片编号
        :return: 新闻图片信息对象
        """
        news_img_info = (
            (
                await db.execute(
                    select(NewsImg)
                    .where(
                        NewsImg.img_id == img_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_img_info

    @classmethod
    async def get_news_img_by_ids(
        cls,
        db: AsyncSession,
        img_ids: list[int],
        redis: aioredis.Redis = None
    ) -> list[NewsImg]:
        """
        批量获取新闻图片（优先使用 Redis 缓存）
        """
        if not redis:
            return await cls._get_news_img_by_ids_db(db, img_ids)

        # 构建缓存键并批量查询
        cache_keys = [f"news_img:{iid}" for iid in img_ids]
        cached_data = await redis.mget(cache_keys)

        # 分离命中和未命中的 img_id
        cached_dict = {}
        missed_ids = []
        for iid, data in zip(img_ids, cached_data):
            if data:
                cached_dict[iid] = NewsImg(**json.loads(data))
            else:
                missed_ids.append(iid)

        # 回源查询未命中的数据
        if missed_ids:
            db_images = await cls._get_news_img_by_ids_db(db, missed_ids)
            # 写入缓存
            async with redis.pipeline() as pipe:
                for img in db_images:
                    key = f"news_img:{img.img_id}"
                    pipe.setex(key, 3600, json.dumps(img.__dict__))
                await pipe.execute()
            cached_dict.update({img.img_id: img for img in db_images})

        # 按输入顺序返回结果
        return [cached_dict.get(iid) for iid in img_ids]

    @classmethod
    async def _get_news_img_by_ids_db(cls, db: AsyncSession, img_ids: list[int]):
        """数据库批量查询实现"""
        result = await db.execute(select(NewsImg).where(NewsImg.img_id.in_(img_ids)))
        return result.scalars().all()
    

    @classmethod
    async def get_news_img_detail_by_info(cls, db: AsyncSession, news_img: News_imgModel):
        """
        根据新闻图片参数获取新闻图片信息

        :param db: orm对象
        :param news_img: 新闻图片参数对象
        :return: 新闻图片信息对象
        """
        news_img_info = (
            (
                await db.execute(
                    select(NewsImg).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return news_img_info

    @classmethod
    async def get_news_img_by_ids(
        cls,
        db: AsyncSession,
        img_ids: list[int],
        redis: aioredis.Redis = None
    ) -> list[NewsImg]:
        """
        批量获取新闻图片（优先使用 Redis 缓存）
        """
        if not redis:
            return await cls._get_news_img_by_ids_db(db, img_ids)

        # 构建缓存键并批量查询
        cache_keys = [f"news_img:{iid}" for iid in img_ids]
        cached_data = await redis.mget(cache_keys)

        # 分离命中和未命中的 img_id
        cached_dict = {}
        missed_ids = []
        for iid, data in zip(img_ids, cached_data):
            if data:
                cached_dict[iid] = NewsImg(**json.loads(data))
            else:
                missed_ids.append(iid)

        # 回源查询未命中的数据
        if missed_ids:
            db_images = await cls._get_news_img_by_ids_db(db, missed_ids)
            # 写入缓存
            async with redis.pipeline() as pipe:
                for img in db_images:
                    key = f"news_img:{img.img_id}"
                    pipe.setex(key, 3600, json.dumps(img.__dict__))
                await pipe.execute()
            cached_dict.update({img.img_id: img for img in db_images})

        # 按输入顺序返回结果
        return [cached_dict.get(iid) for iid in img_ids]

    @classmethod
    async def _get_news_img_by_ids_db(cls, db: AsyncSession, img_ids: list[int]):
        """数据库批量查询实现"""
        result = await db.execute(select(NewsImg).where(NewsImg.news_id.in_(img_ids)))
        return result.scalars().all()

    @classmethod
    async def get_news_img_list(cls, db: AsyncSession, query_object: News_imgPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取新闻图片列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻图片列表信息对象
        """
        query = (
            select(NewsImg)
            .where(
                NewsImg.img_id == query_object.img_id if query_object.img_id else True,
                NewsImg.news_id == query_object.news_id if query_object.news_id else True,
                NewsImg.img_data == query_object.img_data if query_object.img_data else True,
                NewsImg.update_by == query_object.update_by if query_object.update_by else True,
                NewsImg.update_time == query_object.update_time if query_object.update_time else True,
                NewsImg.create_by == query_object.create_by if query_object.create_by else True,
                NewsImg.create_time == query_object.create_time if query_object.create_time else True,
            )
            .order_by(NewsImg.img_id)
            .distinct()
        )
        news_img_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return news_img_list

    @classmethod
    async def add_news_img_dao(cls, db: AsyncSession, news_img: News_imgModel):
        """
        新增新闻图片数据库操作

        :param db: orm对象
        :param news_img: 新闻图片对象
        :return:
        """
        db_news_img = NewsImg(**news_img.model_dump(exclude={}))
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

