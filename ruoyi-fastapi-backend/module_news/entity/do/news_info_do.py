from sqlalchemy import BigInteger, Text, Column, DateTime, String
from config.database import Base


class NewsInfo(Base):
    """
    新闻信息表
    """

    __tablename__ = 'news_info'

    news_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='新闻编号')
    news_content = Column(Text, nullable=True, comment='新闻内容')
    user_id = Column(BigInteger, nullable=False, comment='用户编号')
    news_title = Column(Text, nullable=True, comment='新闻标题')
    update_by = Column(String(100), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    create_by = Column(String(100), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    publish_time = Column(DateTime, nullable=True, comment='发布时间')
    platform = Column(String(100), nullable=True, comment='平台')
    hash_tag = Column(String(100), nullable=True, comment='类别')
    url = Column(String(100), nullable=True, comment='链接')



