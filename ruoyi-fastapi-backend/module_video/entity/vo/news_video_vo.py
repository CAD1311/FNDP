from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class News_videoModel(BaseModel):
    """
    新闻视频表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    video_id: Optional[int] = Field(default=None, description='视频编号')
    news_id: Optional[int] = Field(default=None, description='新闻编号')
    video_data: Optional[str] = Field(default=None, description='视频数据')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')






class News_videoQueryModel(News_videoModel):
    """
    新闻视频不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class News_videoPageQueryModel(News_videoQueryModel):
    """
    新闻视频分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteNews_videoModel(BaseModel):
    """
    删除新闻视频模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    video_ids: str = Field(description='需要删除的视频编号')
