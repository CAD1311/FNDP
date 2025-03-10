from sqlalchemy import DateTime, SmallInteger, Column, BigInteger, String
from config.database import Base


class DetectionTask(Base):
    """
    新闻检测表
    """

    __tablename__ = 'detection_task'

    task_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='任务id')
    update_by = Column(String(100), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    create_by = Column(String(100), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    task_status = Column(SmallInteger, nullable=False, comment='任务状态') #0-检测中 1-检测完成 2-检测失败
    user_id = Column(BigInteger, nullable=False, comment='所属用户')
    news_id = Column(BigInteger, nullable=False, comment='涉及新闻')



