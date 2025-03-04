from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import json
from baidusearch.baidusearch import search
from function_calling_tool import tools,IsRumours,try_parse_tool_calls,function_map,function_calling




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
        text = f"这是一个在{date}{platform}发布的新闻。标题是{title}，正文是{content}，是属于{category}。请你告诉我是否是谣言。"
    return text


class Qwen:
    def __init__(self):
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            "qwen",
            torch_dtype="auto",
            device_map="auto"
        )

        self.Processor = AutoProcessor.from_pretrained("qwen")

    def predict(self,messages_text,path_to_images=None):
        if path_to_images:
            messages = [
                {"role": "system", 
                "content": {
                        "type": "text", 
                        "text": "你是千问，帮助用户分析新闻是否是谣言，可以调用适当的函数，给用户提供合理的分析"
                        }
                },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": path_to_images,
                        },
                    {
                        "type": "text", 
                        "text": messages_text
                        },
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

        text = self.Processor.apply_chat_template(
            messages, 
            tools=tools, 
            add_generation_prompt=True, 
            tokenize=False
            )

        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.Processor(
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
        output_text = self.Processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        messages.append(try_parse_tool_calls(output_text))
        function_calling(messages)





        return output_text


