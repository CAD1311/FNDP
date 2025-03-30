from sqlalchemy import Text, String, Column, BigInteger, DateTime
from config.database import Base


class NewsImg(Base):
    """
    news_img表
    """

    __tablename__ = 'news_img'

    img_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='图片编号')
    news_id = Column(BigInteger, nullable=True, comment='新闻编号')
    img_data = Column(Text, nullable=True, comment='图片数据')
    update_by = Column(String(100), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    create_by = Column(String(100), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')



