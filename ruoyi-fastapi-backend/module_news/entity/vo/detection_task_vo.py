from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class Detection_taskModel(BaseModel):
    """
    新闻检测表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    task_id: Optional[int] = Field(default=None, description='任务id')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    task_status: Optional[int] = Field(default=None, description='任务状态')
    user_id: Optional[int] = Field(default=None, description='所属用户')
    news_id: Optional[int] = Field(default=None, description='涉及新闻')
    task_result: Optional[str] = Field(default=None, description='检测结果')
    is_true: Optional[int] = Field(default=None, description='属实')

    @NotBlank(field_name='task_status', message='任务状态不能为空')
    def get_task_status(self):
        return self.task_status

    @NotBlank(field_name='user_id', message='所属用户不能为空')
    def get_user_id(self):
        return self.user_id

    @NotBlank(field_name='news_id', message='涉及新闻不能为空')
    def get_news_id(self):
        return self.news_id

    def validate_fields(self):
        self.get_task_status()
        self.get_user_id()
        self.get_news_id()




class Detection_taskQueryModel(Detection_taskModel):
    """
    新闻检测不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class Detection_taskPageQueryModel(Detection_taskQueryModel):
    """
    新闻检测分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteDetection_taskModel(BaseModel):
    """
    删除新闻检测模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    task_ids: str = Field(description='需要删除的任务id')
