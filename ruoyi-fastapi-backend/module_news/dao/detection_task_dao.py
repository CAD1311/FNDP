from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_news.entity.do.detection_task_do import DetectionTask
from module_news.entity.vo.detection_task_vo import Detection_taskModel, Detection_taskPageQueryModel
from utils.page_util import PageUtil


class Detection_taskDao:
    """
    新闻检测模块数据库操作层
    """

    @classmethod
    async def get_detection_task_detail_by_id(cls, db: AsyncSession, task_id: int):
        """
        根据任务id获取新闻检测详细信息

        :param db: orm对象
        :param task_id: 任务id
        :return: 新闻检测信息对象
        """
        detection_task_info = (
            (
                await db.execute(
                    select(DetectionTask)
                    .where(
                        DetectionTask.task_id == task_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return detection_task_info

    @classmethod
    async def get_detection_task_detail_by_info(cls, db: AsyncSession, detection_task: Detection_taskModel):
        """
        根据新闻检测参数获取新闻检测信息

        :param db: orm对象
        :param detection_task: 新闻检测参数对象
        :return: 新闻检测信息对象
        """
        detection_task_info = (
            (
                await db.execute(
                    select(DetectionTask).where(
                        DetectionTask.task_status == detection_task.task_status if detection_task.task_status else True,
                        DetectionTask.user_id == detection_task.user_id if detection_task.user_id else True,
                        DetectionTask.news_id == detection_task.news_id if detection_task.news_id else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return detection_task_info

    @classmethod
    async def get_detection_task_list(cls, db: AsyncSession, query_object: Detection_taskPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取新闻检测列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻检测列表信息对象
        """
        query = (
            select(DetectionTask)
            .where(
                DetectionTask.task_status == query_object.task_status if query_object.task_status else True,
                DetectionTask.user_id == query_object.user_id if query_object.user_id else True,
                DetectionTask.news_id == query_object.news_id if query_object.news_id else True,
            )
            .order_by(DetectionTask.task_id)
            .distinct()
        )
        detection_task_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return detection_task_list

    @classmethod
    async def add_detection_task_dao(cls, db: AsyncSession, detection_task: Detection_taskModel):
        """
        新增新闻检测数据库操作

        :param db: orm对象
        :param detection_task: 新闻检测对象
        :return:
        """
        db_detection_task = DetectionTask(**detection_task.model_dump(exclude={}))
        db.add(db_detection_task)
        await db.flush()

        return db_detection_task

    @classmethod
    async def delete_detection_task_dao(cls, db: AsyncSession, detection_task: Detection_taskModel):
        """
        删除新闻检测数据库操作

        :param db: orm对象
        :param detection_task: 新闻检测对象
        :return:
        """
        await db.execute(delete(DetectionTask).where(DetectionTask.task_id.in_([detection_task.task_id])))

