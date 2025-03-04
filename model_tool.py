from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info



# 下面是function calling的定义 网上偷的
qwen_functions = [
    {
        "name_for_human": "谷歌搜索",
        "name_for_model": "google_search",
        "description_for_model": "谷歌搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。"
        + " Format the arguments as a JSON object.",
        "parameters": [
            {
                "name": "search_query",
                "description": "搜索关键词或短语",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
    },
    {
        "name_for_human": "文生图",
        "name_for_model": "image_gen",
        "description_for_model": "文生图是一个AI绘画（图像生成）服务，输入文本描述，返回根据文本作画得到的图片的URL。"
        + " Format the arguments as a JSON object.",
        "parameters": [
            {
                "name": "prompt",
                "description": "英文关键词，描述了希望图像具有什么内容",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
    },
]


def generation_text(
    is_having_image: bool = False,
    title: str = "未知标题",
    content: str = "未知正文",
    category: str = "未知类别",
    date: str = "未知日期",
    platform: str = "未知平台"
) -> str:
    if is_having_image:
        text=f"这是一个在{date}{platform}发布的新闻。标题是{title}，正文是{content}，是属于{category}。<image>请你告诉我是否是谣言。"
    else:
        text = f"这是一个在{date}{platform}发布的新闻。标题是{title}，正文是{content}，是属于{category}。<image>请你告诉我是否是谣言。"
    return text


class Qwen:
    def __init__(self):
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            "qwen", torch_dtype="auto", device_map="auto"
        )

        self.processor = AutoProcessor.from_pretrained("qwen")

    def predict(self,messages_text,path_to_images=None):
        if path_to_images:
            messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": path_to_images,
                    },
                    {"type": "text", "text": messages_text},
                ],
            }
        ]
        else:
            messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": messages_text},
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True,
            function=qwen_functions,
            function_call="auto"
        )

        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        inputs = inputs.to("cuda")

        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text


'''
用法：model=qwen()  
print(model.predict(generation_text(content="一女子居然！"))

'''