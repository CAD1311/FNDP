from sqlalchemy import ForeignKey, Column, String, Text, BigInteger
from sqlalchemy.orm import relationship
from config.database import Base


class NewsInfo(Base):
    """
    新闻信息表
    """

    __tablename__ = 'news_info'

    news_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='')
    news_content = Column(Text, nullable=True, comment='新闻内容')
    user_id = Column(BigInteger, nullable=False, comment='')
    img_id = Column(BigInteger, nullable=True, comment='')

    newsimg_list = relationship('NewsImg', back_populates='news_info')


class NewsImg(Base):
    """
    新闻图片表
    """

    __tablename__ = 'news_img'

    img_id = Column(BigInteger, ForeignKey('news_info.img_id'), primary_key=True, autoincrement=True, nullable=False, comment='')
    img_title = Column(String(100), nullable=False, comment='图片标题')
    img_dis = Column(Text, nullable=False, comment='图片描述')
    img_url = Column(String(100), nullable=True, comment='图片路径')

    news_info = relationship('NewsInfo', back_populates='newsimg_list')
