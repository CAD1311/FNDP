from fastapi import APIRouter, Depends,  Request
from module_news.service.detection_task_service import Detection_taskService



quick_detectionController = APIRouter(prefix='/quick', dependencies=[])


def get_detection_service(request: Request) -> Detection_taskService:
    return request.app.state.detection_service

@quick_detectionController.post('/detection')
async def quick_detect_news_news_info(
    text: str,
    service: Detection_taskService = Depends(get_detection_service),
):
    return service.quick_start_services(text)