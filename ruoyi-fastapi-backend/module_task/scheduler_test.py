from datetime import datetime
from .hot_search import *
import asyncio
import redis

def job(*args, **kwargs):
    """
    定时任务执行同步函数示例
    """
    print(args)
    print(kwargs)
    print(f'{datetime.now()}同步函数执行了')


async def async_job(*args, **kwargs):
    """
    定时任务执行异步函数示例
    """
    print(args)
    print(kwargs)
    print(f'{datetime.now()}异步函数执行了')


async def job_wrapper(func, platform_name):
    result = await func()
    return {platform_name: result}  # 添加平台标识键

async def jobs():
    tasks = [
        job_wrapper(weibo_hot_search, "weibo"),
        job_wrapper(baidu_hot_search, "baidu"),
        job_wrapper(zhihu_hot_search, "zhihu"),
        job_wrapper(douyin_hot_search, "douyin")
    ]
    results = await asyncio.gather(*tasks)
    
    # 合并为统一JSON
    merged = {}
    for item in results:
        merged.update(item)
    return json.dumps(merged, ensure_ascii=False)

def my_job():
    final_json = asyncio.run(jobs())
    print(final_json)  # 输出合并后的完整JSON