from fastapi import APIRouter, Depends,  Request
from module_news.service.detection_task_service import Detection_taskService
from pydantic import BaseModel


quick_detectionController = APIRouter(prefix='/quick', dependencies=[])


def get_detection_service(request: Request) -> Detection_taskService:
    return request.app.state.detection_service

class textDetectionRequest(BaseModel):
    text : str

@quick_detectionController.post('/detection')
async def quick_detect_news_news_info(
    params: textDetectionRequest,
    service: Detection_taskService = Depends(get_detection_service),
):
    text = params.text
    return service.quick_start_services(text)