from sqlalchemy import String, Column, BigInteger, Text
from config.database import Base


class NewsImg(Base):
    """
    新闻图片表
    """

    __tablename__ = 'news_img'

    img_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='')
    img_title = Column(String(100), nullable=True, comment='图片标题')
    img_dis = Column(Text, nullable=True, comment='图片描述')
    img_url = Column(String(100), nullable=False, comment='图片路径')
    news_id = Column(BigInteger, nullable=False, comment='所属新闻')



