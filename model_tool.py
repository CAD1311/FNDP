from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import json
import torch
import re
from tools import *
from baidusearch.baidusearch import search

tools = [
    {
        "type": "function",
        "function": {
            "name": "IsRumours",
            "description": "当需要输出最终谣言判定结论时调用此函数，参数只能从0/1/2中选择。调用后用户将直接看到判定结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "isNewsTrue": {
                        "type": "integer",
                        "enum": [0, 1, 2],
                        "description": "谣言判定结果：0=事实，1=尚未定论，2=谣言"
                    }
                },
                "required": ["isNewsTrue"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "可以利用这个搜索函数进行搜索，搜索结果将帮助确定新闻的真实与否",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "用于搜索的关键字"
                    },
                    "num":{
                        "type": "integer",
                        "description": "搜索结果的数量，最好为3个"
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]


class Qwen:
    def __init__(self) -> None:
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            "qwen", 
            torch_dtype="auto", 
            device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained("qwen")

        self.system_prompt = """你是一个帮助专门用于伪造新闻分析的助手。
当你需要调用函数时，你必须严格使用如下格式输出:
<tool_call>
{
    "name": "函数名称",
    "arguments": {
        "参数名1": "参数值1",
        "参数名2": "参数值2"
    }
}
</tool_call>

请注意，不要使用Markdown代码块（```）来包裹JSON，而是必须使用<tool_call>标签。"""

    
    def apply_multimodal_chat_template_with_tools(self, messages, tools=None):
        """将工具信息添加到聊天模板中"""
        # 添加系统提示
        messages_with_system = [{"role": "system", "content": self.system_prompt}]
        
        # 检查第一条消息是否已经是系统消息
        if messages and messages[0].get("role") != "system":
            messages_with_system.extend(messages)
        else:
            # 如果已有系统消息，使用原始消息
            messages_with_system = messages
           
        # 使用常规方式处理对话
        text = self.processor.apply_chat_template(
            messages_with_system,
            tokenize=False,
            add_generation_prompt=True
        )
           
        # 如果提供了工具，手动添加到模板中
        if tools:
            # 查找插入工具的位置（在系统消息之后，用户消息之前）
            if "<|im_start|>user" in text:
                tools_json = json.dumps(tools, ensure_ascii=False)
                tools_section = f"<|im_start|>tools\n{tools_json}\n<|im_end|>\n"
                   
                # 找到用户消息的开始位置
                insert_pos = text.find("<|im_start|>user")
                   
                # 插入工具部分
                text = text[:insert_pos] + tools_section + text[insert_pos:]
           
        return text

    def safe_process_vision_info(self, messages):
        """安全处理视觉信息，处理没有图片或视频的情况"""
        try:
            from qwen_vl_utils import process_vision_info
            return process_vision_info(messages)
        except ValueError as e:
            # 如果是缺少图片或视频的错误
            if "image, image_url or video should in content" in str(e):
                print("警告: 没有找到图片或视频内容，将使用纯文本模式")
                return None, None
            else:
                # 其他错误仍然抛出
                raise e
    
    def generate(self, messages, tools=None, max_new_tokens=512):
        """生成响应"""
        try:
            # 处理聊天模板，包含工具
            text = self.apply_multimodal_chat_template_with_tools(messages, tools)
            
            # 安全处理视觉信息
            image_inputs, video_inputs = self.safe_process_vision_info(messages)
            
            # 准备模型输入
            if image_inputs is not None or video_inputs is not None:
                # 有多模态内容
                inputs = self.processor(
                    text=[text], 
                    images=image_inputs, 
                    videos=video_inputs,
                    padding=True, 
                    return_tensors="pt",
                )
            else:
                # 纯文本模式
                inputs = self.processor.tokenizer(
                    text=[text],
                    padding=True,
                    return_tensors="pt",
                )
            
            # 移动到GPU
            inputs = {k: v.to(self.model.device) for k, v in inputs.items() if k != "pixel_values" or v is not None}
            
            # 生成输出
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            
            # 提取生成的文本
            if "input_ids" in inputs:
                generated_ids_trimmed = [
                    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs["input_ids"], generated_ids)
                ]
            else:
                # 处理缺少 input_ids 的情况
                generated_ids_trimmed = generated_ids
                
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            
            # 处理输出格式，将markdown代码块转换为tool_call格式
            output = output_text[0]
            # 使用正则表达式查找```json...```模式
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', output, re.DOTALL)
            if json_match:
                # 提取JSON内容
                json_content = json_match.group(1)
                try:
                    # 尝试解析JSON
                    json_obj = json.loads(json_content)
                    
                    # 判断是否为IsRumours调用
                    if "isNewsTrue" in json_obj:
                        # 重新构建为正确的tool_call格式
                        tool_call = {
                            "name": "IsRumours",
                            "arguments": {
                                "isNewsTrue": json_obj["isNewsTrue"]
                            }
                        }
                        output = f"<tool_call>\n{json.dumps(tool_call, ensure_ascii=False, indent=2)}\n</tool_call>"
                    # 处理搜索调用
                    elif "keyword" in json_obj and "num" in json_obj:
                        tool_call = {
                            "name": "search",
                            "arguments": {
                                "keyword": json_obj["keyword"],
                                "num": json_obj["num"]
                            }
                        }
                        output = f"<tool_call>\n{json.dumps(tool_call, ensure_ascii=False, indent=2)}\n</tool_call>"
                except json.JSONDecodeError:
                    # JSON解析失败，保留原始输出
                    pass
                    
            return output
        
        except Exception as e:
            # 捕获并记录任何异常
            error_msg = f"生成响应时出错: {str(e)}"
            print(error_msg)
            return f"很抱歉，处理您的请求时遇到了问题: {str(e)}"




messages = [
   {"role": "user", "content": "这是一个在2020/1/1网易发布的新闻。标题是教皇方济各纪念新教改革500周年，正文是2020年11月15日 · 教皇方济各陷入'丑闻'，他为性感模特点了个赞，掀起网络狂潮."}
]

# 增加详细的调试信息
try:
    print("=== 开始处理 ===")
    model = Qwen()
    print("模型已初始化")
    
    output_text = model.generate(messages, tools)
    print("\n=== 原始模型输出 ===")
    print(output_text)
    
    parsed_message = try_parse_tool_calls(output_text)
    print("\n=== 解析后消息 ===")
    print(json.dumps(parsed_message, ensure_ascii=False, indent=2))
    
    print("\n=== 调用函数 ===")
    messages.append(parsed_message)
    result = function_calling(messages)
    print("函数调用结果:", result)
    
    # 附加原始输出，确保至少有些输出
    print("\n=== 最终输出 ===")
    print(output_text)
except Exception as e:
    import traceback
    print(f"发生错误: {str(e)}")
    print("\n=== 详细错误信息 ===")
    traceback.print_exc()