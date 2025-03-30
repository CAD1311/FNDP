from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_news.dao.detection_task_dao import Detection_taskDao
from module_news.dao.news_info_dao import News_infoDao
from module_news.entity.vo.news_info_vo import News_infoModel
from module_news.entity.vo.detection_task_vo import DeleteDetection_taskModel, Detection_taskModel, \
    Detection_taskPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil
import asyncio
from utils.mock_qwen import Qwen
from utils.rag import VectorStore,RAG

model_cache_dir = "./models"
save_dir = "./vector_store"



class Detection_taskService:
    """
    新闻检测模块服务层
    """

    def __init__(self):
        self.model = Qwen()
        self.vectorstore=VectorStore.load(
            save_dir=save_dir,
            embedding_model='shibing624/text2vec-base-chinese',
            model_cache_dir=model_cache_dir,
            device='cuda'
        )
        self.rag=RAG(self.vectorstore)

    async def start_service(self):
        await self.model.start()

    @classmethod
    async def get_detection_task_list_services(
            cls, query_db: AsyncSession, query_object: Detection_taskPageQueryModel, is_page: bool = False
    ):
        """
        获取新闻检测列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 新闻检测列表信息对象
        """
        detection_task_list_result = await Detection_taskDao.get_detection_task_list(query_db, query_object, is_page)

        return detection_task_list_result

    @classmethod
    async def add_detection_task_services(cls, query_db: AsyncSession, page_object: Detection_taskModel):
        """
        新增新闻检测信息service

        :param query_db: orm对象
        :param page_object: 新增新闻检测对象
        :return: 新增新闻检测校验结果
        """
        try:
            await Detection_taskDao.add_detection_task_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_detection_task_services(cls, query_db: AsyncSession, page_object: DeleteDetection_taskModel):
        """
        删除新闻检测信息service

        :param query_db: orm对象
        :param page_object: 删除新闻检测对象
        :return: 删除新闻检测校验结果
        """
        if page_object.task_ids:
            task_id_list = page_object.task_ids.split(',')
            try:
                for task_id in task_id_list:
                    await Detection_taskDao.delete_detection_task_dao(query_db, Detection_taskModel(taskId=task_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入任务id为空')

    @classmethod
    async def detection_task_detail_services(cls, query_db: AsyncSession, task_id: int):
        """
        获取新闻检测详细信息service

        :param query_db: orm对象
        :param task_id: 任务id
        :return: 任务id对应的信息
        """
        detection_task = await Detection_taskDao.get_detection_task_detail_by_id(query_db, task_id=task_id)
        if detection_task:
            result = Detection_taskModel(**CamelCaseUtil.transform_result(detection_task))
        else:
            result = Detection_taskModel(**dict())

        return result

    @staticmethod
    async def export_detection_task_list_services(detection_task_list: List):
        """
        导出新闻检测信息service

        :param detection_task_list: 新闻检测信息列表
        :return: 新闻检测信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'taskId': '任务id',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'createBy': '创建者',
            'createTime': '创建时间',
            'taskStatus': '任务状态',
            'userId': '所属用户',
            'newsId': '涉及新闻',
        }
        binary_data = ExcelUtil.export_list2excel(detection_task_list, mapping_dict)

        return binary_data

    async def detection_task_start_services(self, query_db: AsyncSession, page_objects: dict[DeleteDetection_taskModel,bool]):
        """
        新闻检测开始service

        :param news_dict: 新闻信息+是否使用rag(1为使用，0为不使用)
        :param news_info: 新闻信息
        :return: 新闻检测开始校验结果
        """
        try:
            texts=[]
            news_dict={}
            for page_object,value in page_objects.items():
                await Detection_taskDao.add_detection_task_dao(query_db, page_object)
                await query_db.commit()
                news_info=await News_infoDao.get_news_info_detail_by_id(query_db, page_object.news_id)
                news_dict[news_info]=value
            
            for news_info,value in news_dict.items():
                text=f"这是一个在{news_info.publish_time}{news_info.platform}发布的新闻。标题是{news_info.news_title}，正文{news_info.news_content},是属于{news_info.hash_tag}类别的新闻。<image>请你告诉我是否是谣言。"
                if value:
                    text=self.rag.generate(text)+text
            tasks = [self.model.predict(news_item) for news_item in texts]

            results = await asyncio.gather(*tasks)
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

