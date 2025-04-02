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
from utils.parse_prediction_json import parse_prediction_json
from module_news.dao.detection_task_dao import DetectionTask
from sqlalchemy import delete, select, update,insert, bindparam
import logging

model_cache_dir = "../models"
save_dir = "../vector_store"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
            device='cpu'
        )
        self.rag=RAG(self.vectorstore)

    async def start_service(self):
        await self.model.start()

    def _build_base_text(self, news_info):
        return (
            f"这是一个在{news_info.publish_time}{news_info.platform}发布的新闻。"
            f"标题是{news_info.news_title}，正文{news_info.news_content}，"
            f"属于{news_info.hash_tag}类别。"
        )

    async def _async_predict(self, text: str):
        """将同步预测转为异步执行[[7]][[9]]"""
        return await self.model.predict(text)

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

    async def detection_task_start_services(self, query_db: AsyncSession, page_objects):
        try:
            async with query_db.begin():
                news_ids = [po.news_id for po in page_objects]
                tasks_to_insert = [DetectionTask(**po.model_dump()) for po in page_objects]
                await query_db.execute(insert(DetectionTask), [task.__dict__ for task in tasks_to_insert])
                
                news_info_list = await News_infoDao.get_news_info_by_ids(query_db, news_ids)
                news_info_dict = {info.news_id: info for info in news_info_list}
                
                predict_tasks = []
                for news_id in news_ids:
                    if news_info := news_info_dict.get(news_id):
                        base_text = self._build_base_text(news_info)
                        predict_tasks.append((
                            news_id,
                            self._async_predict(base_text)
                        ))
                logger.info(f"预测任务：{predict_tasks}")
                coroutines = [task[1] for task in predict_tasks]
                results = await asyncio.gather(*coroutines, return_exceptions=True)
                # 新增异常记录
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f'任务{i}异常: {str(result)}', exc_info=True)
                    elif isinstance(result, BaseException):
                        logger.error(f'任务{i}基础异常: {str(result)}')
                logger.info(f"检测结果：{results}")

                update_params = []
                for task, result in zip(predict_tasks, results):
                    news_id = task[0]
                    if isinstance(result, Exception) or \
                       not (parsed := parse_prediction_json(result)) or \
                       not parsed.get('IsNewsTrue') or \
                       not parsed.get('reasons'):
                        logger.error(f'新闻{news_id}解析失败，结果:{result}')
                        continue
                    
                    # 添加字段校验
                    required_fields = ['IsNewsTrue', 'reasons', 'recommendation']
                    if not all(field in parsed for field in required_fields):
                        logger.error(f'新闻{news_id}返回结果缺少必要字段: {parsed}')
                        continue
                    
                    # 字段映射
                    update_params.append({
                        "news_id": news_id,
                        "task_status": 1,
                        "is_true": parsed["IsNewsTrue"],
                        "task_result": f"是否真实：{parsed['IsNewsTrue']}，原因：{parsed['reasons']}，建议：{parsed['recommendation']}"
                    })
                
                logger.info(f'待更新参数列表: {update_params}')
                if update_params:
                    await query_db.execute(
                        update(DetectionTask)
                        .where(DetectionTask.news_id.in_([p["news_id"] for p in update_params]))
                        .values(
                            task_status=bindparam("task_status"),
                            is_true=bindparam("is_true"),
                            task_result=bindparam("task_result")
                        )
                    )
            return CrudResponseModel(is_success=True, message="检测完成")
        
        except Exception as e:
            await query_db.rollback()
            logger.error(f"检测任务失败：{e}")
            raise e

