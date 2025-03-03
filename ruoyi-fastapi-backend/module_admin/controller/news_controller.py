from fastapi import APIRouter
from utils.response_util import ResponseUtil

newsController = APIRouter(prefix="/tool/news")

@newsController.get("")
async def get_news():
    return ResponseUtil.success(data = {"code": 20000, "data": "This is news get page."})

@newsController.post("/")
async def add_news():
    return {"code": 20000, "data": "This is news add page."}

@newsController.put("/")
async def update_news():
    return {"code": 20000, "data": "This is news update page."}

@newsController.delete("/")
async def delete_news():
    return {"code": 20000, "data": "This is news delete page."}