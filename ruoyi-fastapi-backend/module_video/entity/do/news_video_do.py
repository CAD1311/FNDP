from sqlalchemy import DateTime, Text, String, Integer, Column, BigInteger
from config.database import Base


class NewsVideo(Base):
    """
    新闻视频表
    """

    __tablename__ = 'news_video'

    video_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, comment='视频编号')
    news_id = Column(BigInteger, nullable=True, comment='新闻编号')
    video_data = Column(Text, nullable=True, comment='视频数据')
    create_by = Column(String(100), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(100), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')



