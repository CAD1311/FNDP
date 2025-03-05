from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import json

def apply_multimodal_chat_template_with_tools(processor, messages, tools=None, system_prompt=None):
    # 自定义系统提示，明确指导模型使用工具
    if system_prompt is None:
        system_prompt = "You are a helpful assistant. When the user asks about images, analyze them carefully. If the user asks you to use a function or if the appropriate function is available, you MUST use the function by outputting a <tool_call> JSON.</tool_call> format."
    
    # 添加系统提示到消息
    messages_with_system = [{"role": "system", "content": system_prompt}] + messages
    
    # 1. 使用常规方式处理对话
    text = processor.apply_chat_template(
        messages_with_system, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    # 2. 如果提供了工具，手动添加到模板中
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

# 使用示例
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "qwen", 
    torch_dtype="auto", 
    device_map="auto"
)
processor = AutoProcessor.from_pretrained("qwen")

# 准备消息和工具 - 优化提示语，明确要求调用函数
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "blank.jpg",
            },
            {"type": "text", "text": "分析这张图片的白色程度，并使用show_white函数来评估。必须调用函数来回答。<image>"},
        ],
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "show_white",
            "description": "使用此函数评估图片的白色程度",
            "parameters": {
                "type": "object",
                "properties": {
                    "num": {
                        "type": "integer",
                        "enum": [0, 1, 2],
                        "description": "白色程度: 0=不白, 1=部分白, 2=全白",
                    }
                },
                "required": ["num"],
            },
        },
    }
]

# 添加明确的系统提示
system_prompt = "你是一个能分析图像的助手。当用户询问图像并要求使用函数时，你必须使用提供的函数回应。对于白色图像分析，你必须调用show_white函数并提供适当的值。请始终使用<tool_call>格式进行函数调用。"

# 处理模板，包含工具和系统提示
text = apply_multimodal_chat_template_with_tools(processor, messages, tools, system_prompt)

# 处理视觉信息
image_inputs, video_inputs = process_vision_info(messages)

# 准备模型输入
inputs = processor(
    text=[text], 
    images=image_inputs, 
    videos=video_inputs,
    padding=True, 
    return_tensors="pt",
)

# 移动到GPU
inputs = inputs.to("cuda")

# 生成输出 - 调整生成参数
generated_ids = model.generate(
    **inputs, 
    max_new_tokens=512,
    temperature=0.2,  # 降低温度，使回答更确定
    do_sample=True,
    top_p=0.95
)

generated_ids_trimmed = [
    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)

print(output_text[0])