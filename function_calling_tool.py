from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer
from qwen_vl_utils import process_vision_info
from baidusearch.baidusearch import search
from tools import try_parse_tool_calls, function_calling
from multimodal_tool import MultimodalProcessor
import time



model_name_or_path = "qwen"
multimodal_processor = MultimodalProcessor(model_name_or_path)

def process_messages(messages, image_path=None):
    """处理消息，支持多模态输入"""
    return multimodal_processor.run_conversation(messages, image_path, tools=tools)

# 示例使用
messages = [
   {"role": "system", "content": "你是千问，帮助用户分析新闻是否是谣言，只能说是或者不是谣言，并且要调用适当的函数，还有给用户提供合理的分析，得到结果后调用IsRumours告诉用户是否是谣言"},
   {"role": "user", "content": "这是一个在2020/1/1网易发布的新闻。标题是教皇方济各纪念新教改革500周年，正文是2020年11月15日 · 教皇方济各陷入“丑闻”，他为性感模特点了个赞，掀起网络狂潮."}
]

# 处理文本消息
# messages = process_messages(messages)

# 如果有图片，可以这样处理
messages = process_messages(messages, image_path="blank.jpg")