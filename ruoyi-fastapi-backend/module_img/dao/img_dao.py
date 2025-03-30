from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_img.entity.do.img_do import NewsImg
from module_img.entity.vo.img_vo import ImgModel, ImgPageQueryModel
from utils.page_util import PageUtil


class ImgDao:
    """
    news_img模块数据库操作层
    """

    @classmethod
    async def get_img_detail_by_id(cls, db: AsyncSession, img_id: int):
        """
        根据图片编号获取news_img详细信息

        :param db: orm对象
        :param img_id: 图片编号
        :return: news_img信息对象
        """
        img_info = (
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

        return img_info

    @classmethod
    async def get_img_detail_by_info(cls, db: AsyncSession, img: ImgModel):
        """
        根据news_img参数获取news_img信息

        :param db: orm对象
        :param img: news_img参数对象
        :return: news_img信息对象
        """
        img_info = (
            (
                await db.execute(
                    select(NewsImg).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return img_info

    @classmethod
    async def get_img_list(cls, db: AsyncSession, query_object: ImgPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取news_img列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: news_img列表信息对象
        """
        query = (
            select(NewsImg)
            .where(
                NewsImg.news_id == query_object.news_id if query_object.news_id else True,
                NewsImg.img_data == query_object.img_data if query_object.img_data else True,
            )
            .order_by(NewsImg.img_id)
            .distinct()
        )
        img_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return img_list

    @classmethod
    async def add_img_dao(cls, db: AsyncSession, img: ImgModel):
        """
        新增news_img数据库操作

        :param db: orm对象
        :param img: news_img对象
        :return:
        """
        db_img = NewsImg(**img.model_dump(exclude={}))
        db.add(db_img)
        await db.flush()

        return db_img

    @classmethod
    async def edit_img_dao(cls, db: AsyncSession, img: dict):
        """
        编辑news_img数据库操作

        :param db: orm对象
        :param img: 需要更新的news_img字典
        :return:
        """
        await db.execute(update(NewsImg), [img])

    @classmethod
    async def delete_img_dao(cls, db: AsyncSession, img: ImgModel):
        """
        删除news_img数据库操作

        :param db: orm对象
        :param img: news_img对象
        :return:
        """
        await db.execute(delete(NewsImg).where(NewsImg.img_id.in_([img.img_id])))

