import json
from langchain_community.document_loaders import Docx2txtLoader
import os

def file_extract(
        path_to_file: str
) -> str:
    function_map = {
        ".docx": docx_extract,
        ".json": json_extract,
        ".txt": txt_extract
    }
    _, ext = os.path.splitext(path_to_file)

    if ext not in function_map:
        supported_format=" ,".join(function_map.keys())
        raise ValueError(f"不支持的文件类型{ext}。支持的格式有{supported_format}")

    if not os.path.exists(path_to_file):
        raise FileNotFoundError(f"{path_to_file}不存在，请检查")

    return function_map[ext](path_to_file)


def docx_extract(path_to_file: str) -> str:
    try:
        loader = Docx2txtLoader(path_to_file)
        data = loader.load()
        return str(data[0])
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错")



def json_extract(path_to_file: str) -> str:
    try:
        with open(path_to_file, "r", encoding='utf-8') as f:
            data = json.load(f)
        return str(data)
    except json.JSONDecodeError:
        raise ValueError(f"无效的JSON文件: {path_to_file}")
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错")


def txt_extract(path_to_file: str) -> str:
    try:
        with open(path_to_file, "r", encoding='utf-8') as f:
            data = f.read()
        return data
    except UnicodeDecodeError:
        try:
            with open(path_to_file, "r", encoding='gbk') as f:
                data = f.read()
            return data
        except Exception as e:
            raise Exception(f"无法识别文件编码: {str(e)}")
    except Exception as e:
        raise Exception(f"处理{path_to_file}文件出错")



def 
