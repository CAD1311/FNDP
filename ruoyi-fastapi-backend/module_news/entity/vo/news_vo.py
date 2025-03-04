from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import List, Optional
from module_admin.annotation.pydantic_annotation import as_query


class NewsBaseModel(BaseModel):
    """
    新闻信息表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    news_id: Optional[int] = Field(default=None, description='')
    news_content: Optional[str] = Field(default=None, description='新闻内容')
    user_id: Optional[int] = Field(default=None, description='关联用户')

    @NotBlank(field_name='user_id', message='关联用户不能为空')
    def get_user_id(self):
        return self.user_id

    def validate_fields(self):
        self.get_user_id()


class NewsModel(NewsBaseModel):
    """
    新闻信息表对应pydantic模型
    """
    newsimg_list: Optional[List['News_imgModel']] = Field(default=None, description='子表列信息')



class News_imgModel(BaseModel):
    """
    新闻图片表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    img_id: Optional[int] = Field(default=None, description='')
    img_title: Optional[str] = Field(default=None, description='图片标题')
    img_dis: Optional[str] = Field(default=None, description='图片描述')
    img_url: Optional[str] = Field(default=None, description='图片路径')
    news_id: Optional[int] = Field(default=None, description='所属新闻')

    @NotBlank(field_name='img_url', message='图片路径不能为空')
    def get_img_url(self):
        return self.img_url

    @NotBlank(field_name='news_id', message='所属新闻不能为空')
    def get_news_id(self):
        return self.news_id

    def validate_fields(self):
        self.get_img_url()
        self.get_news_id()


class NewsQueryModel(NewsBaseModel):
    """
    新闻信息不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class NewsPageQueryModel(NewsQueryModel):
    """
    新闻信息分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteNewsModel(BaseModel):
    """
    删除新闻信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    news_ids: str = Field(description='需要删除的')
