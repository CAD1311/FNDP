from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import json


def IsRumours(
    isNewsTrue: int
    )-> None:
    if isNewsTrue==0:
        print("事实")
    elif isNewsTrue==1:
        print("尚未定论")
    elif isNewsTrue==2:
        print("谣言")

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
    }
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
            "qwen",
            torch_dtype="auto",
            device_map="auto"
        )

        self.tokenizer = AutoTokenizer.from_pretrained("qwen")
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
            text = self.processor.apply_chat_template(
            messages, 
            tools=tools, 
            add_generation_prompt=True, 
            tokenize=False
            )


        else:
            messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": messages_text},
                ],
            }
        ]
            text = self.tokenizer.apply_chat_template(
            messages, 
            tools=tools, 
            add_generation_prompt=True, 
            tokenize=False
            )


        text = self.tokenizer.apply_chat_template(
            messages, 
            tools=tools, 
            add_generation_prompt=True, 
            tokenize=False
            )

        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.tokenizer(
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
        output_text = self.tokenizer.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text


