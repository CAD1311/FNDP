import json
from langchain_community.document_loaders import Docx2txtLoader
from module_news.entity.vo.news_info_vo import News_infoModel
from module_news.service.news_info_service import News_infoService
from module_img.entity.vo.img_vo import ImgModel
from module_img.service.img_service import ImgService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
import zipfile
from config.env import UploadConfig
from CommonService.upload_service import upload_service
import csv


async def add_news(
    db_session: AsyncSession,
    title: str,
    content: str,
    user_id: int,
    platform: str = None,
    hash_tag: str = None,
    url: str = None,
    image_urls: list = None,
):
    """
    添加新闻并关联图片
    
    参数:
    - db_session: 数据库会话
    - title: 新闻标题
    - content: 新闻内容
    - user_id: 用户ID
    - platform: 平台来源
    - hash_tag: 新闻分类标签
    - url: 原始链接
    - image_urls: 图片URL列表
    
    返回:
    - 操作结果和新闻ID
    """
    try:
        # 1. 创建新闻对象
        news = News_infoModel(
            news_title=title,
            news_content=content,
            user_id=user_id,
            publish_time=datetime.now(),
            platform=platform,
            hash_tag=hash_tag,
            url=url,
            create_time=datetime.now(),
            update_time=datetime.now(),
            create_by="system",
            update_by="system"
        )
        
        news_result = await News_infoService.add_news_info_services(db_session, news)
        
        news_id = None
        if hasattr(news_result, 'result') and hasattr(news_result.result, 'news_id'):
            news_id = news_result.result.news_id
        

        if image_urls and news_id:
            for img_url in image_urls:
                img = ImgModel(
                    news_id=news_id,
                    img_data=img_url,
                    create_time=datetime.now(),
                    update_time=datetime.now(),
                    create_by="system", 
                    update_by="system"
                )
                await ImgService.add_img_services(db_session, img)
        
        return {
            "success": news_result.is_success,
            "message": news_result.message,
            "news_id": news_id
        }
        
    except Exception as e:
        await db_session.rollback()
        return {"success": False, "message": f"添加新闻失败: {str(e)}", "news_id": None} 

    """
    更新新闻的某个列
    
    参数:
    - db_session: 数据库会话
    - news_id: 要更新的新闻ID
    - column_name: 要更新的列名(news_title/news_content/platform/hash_tag等)
    - column_value: 新的列值
    
    返回:
    - 更新结果
    """
    try:
        # 创建一个只包含需要更新字段的News_infoModel对象
        news_update = News_infoModel(
            news_id=news_id,
            update_time=datetime.now(),
            update_by="system"
        )
        
        # 动态设置要更新的列
        setattr(news_update, column_name, column_value)
        
        # 调用服务方法执行更新
        result = await News_infoService.edit_news_info_services(db_session, news_update)
        return result
    except Exception as e:
        await db_session.rollback()
        return {
            "success": False,
            "message": f"更新新闻失败: {str(e)}"
        }

async def file_extract(
        path_to_file: str,
        userid: int,
        db_session: AsyncSession
) :
    function_map = {
        ".docx": docx_extract,
        ".json": json_extract,
        ".txt": txt_extract,
        ".csv": csv_extract,
        ".jpg":ocr_extract,".png":ocr_extract,".jpeg":ocr_extract,".webp":ocr_extract,
    }
    _, ext = os.path.splitext(path_to_file)

    if ext not in function_map:
        raise ValueError(f"不支持的文件类型{ext}。")

    if not os.path.exists(path_to_file):
        raise FileNotFoundError(f"{path_to_file}不存在，请检查")

    await function_map[ext](path_to_file, db_session, userid)

    return 


async def docx_extract(path_to_file: str, db_session: AsyncSession, user_id: int):
    try:
        loader = Docx2txtLoader(path_to_file)
        data = loader.load()
        file_name = os.path.basename(path_to_file)
        content = data[0].page_content if data else ""
        
        # 添加新闻内容到数据库
        news_result = await add_news(
            db_session=db_session,
            title=file_name,
            content=content,
            user_id=user_id
        )
        
        news_id = news_result.get("news_id")
        saved_images = []
        
        # 使用后端的上传路径和文件命名规则
        relative_path = f'upload/{datetime.now().strftime("%Y/%m/%d")}'
        dir_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
        os.makedirs(dir_path, exist_ok=True)
        
        with zipfile.ZipFile(path_to_file) as zf:
            # 图片通常存储在word/media/目录下
            image_files = [f for f in zf.namelist() if f.startswith('word/media/')]
            
            for i, img_path in enumerate(image_files):
                with zf.open(img_path) as img_file:
                    img_data = img_file.read()
                    # 使用系统命名规则
                    base_name = os.path.basename(img_path).rsplit(".", 1)[0]
                    ext = os.path.basename(img_path).rsplit(".", 1)[-1]
                    # 使用内建random模块替代
                    import random
                    random_number = str(random.randint(1000, 9999))
                    filename = f'{base_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}{UploadConfig.UPLOAD_MACHINE}{random_number}.{ext}'
                    
                    filepath = os.path.join(dir_path, filename)
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    
                    # 生成URL
                    url = f'{UploadConfig.UPLOAD_PREFIX}/{relative_path}/{filename}'
                    saved_images.append(url)
                    
                    # 添加图片记录到数据库
                    if news_id:
                        img = ImgModel(
                            news_id=news_id,
                            img_data=url,
                            create_time=datetime.now(),
                            update_time=datetime.now(),
                            create_by="system",
                            update_by="system"
                        )
                        img_result = await ImgService.add_img_services(db_session, img)
                    

        
        return {
            "success": True,
            "message": "文档处理成功",
            "content": content,
            "images": saved_images,
            "news_id": news_id
        }
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错: {str(e)}")



async def json_extract(path_to_file: str, db_session: AsyncSession, user_id: int):
    try:
        with open('file.json', 'r', encoding='utf-8') as f:
            data = json.load(f) 

        title = data.get("title")
        content=data.get('content')
        platform=data.get('platform')
        hash_tag=data.get('hash_tag')
        url=data.get('url')



        await add_news(
            db_session=db_session,
            title=title,
            content=content,
            platform=platform,
            hash_tag=hash_tag,
            url=url,
            user_id=user_id
        )
        return
    except json.JSONDecodeError:
        raise ValueError(f"无效的JSON文件: {path_to_file}")
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错")


async def txt_extract(path_to_file: str, db_session: AsyncSession, user_id: int):
    try:
        file_name = os.path.basename(path_to_file)
        with open(path_to_file, "r", encoding='utf-8') as f:
            data = f.read()
        await add_news(
            db_session=db_session,
            title=file_name,
            content=data,
            user_id=user_id
        )

        return
    except UnicodeDecodeError:
        try:
            with open(path_to_file, "r", encoding='gbk') as f:
                data = f.read()
            await add_news(
                db_session=db_session,
                title=file_name,
                content=data,
                user_id=user_id
            )
            return
        except Exception as e:
            raise Exception(f"无法识别文件编码: {str(e)}")
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错")




async def csv_extract(path_to_file: str, db_session: AsyncSession, user_id: int):
    try:
        with open(path_to_file, "r", encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
        
        for row in csv_reader:
            title = row.get("title")
            content=row.get('content')
            platform=row.get('platform')
            hash_tag=row.get('hash_tag')
            url=row.get('url')

            await add_news(
                db_session=db_session,
                title=title,
                content=content,
                platform=platform,
                hash_tag=hash_tag,
                url=url,
                user_id=user_id
            )
        return
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错: {str(e)}")




async def ocr_extract(path_to_file: str, db_session: AsyncSession, user_id: int)