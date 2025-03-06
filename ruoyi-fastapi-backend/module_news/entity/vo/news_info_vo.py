from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class News_infoModel(BaseModel):
    """
    新闻信息表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    news_id: Optional[int] = Field(default=None, description='新闻编号')
    news_content: Optional[str] = Field(default=None, description='新闻内容')
    user_id: Optional[int] = Field(default=None, description='用户编号')
    news_title: Optional[str] = Field(default=None, description='新闻标题')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    publish_time: Optional[datetime] = Field(default=None, description='发布时间')
    platform: Optional[str] = Field(default=None, description='平台')
    hash_tag: Optional[str] = Field(default=None, description='类别')
    url: Optional[str] = Field(default=None, description='链接')

    @NotBlank(field_name='user_id', message='用户编号不能为空')
    def get_user_id(self):
        return self.user_id


    def validate_fields(self):
        self.get_user_id()




class News_infoQueryModel(News_infoModel):
    """
    新闻信息不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class News_infoPageQueryModel(News_infoQueryModel):
    """
    新闻信息分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteNews_infoModel(BaseModel):
    """
    删除新闻信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    news_ids: str = Field(description='需要删除的新闻编号')
