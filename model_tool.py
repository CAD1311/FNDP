from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import time
import torch


class Qwen():
    def __init__(self) -> None:

        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            "qwen",
            torch_dtype=torch.bfloat16,  # 使用bfloat16以平衡性能和精度
            attn_implementation="flash_attention_2",  # 使用flash attention提高效率
            device_map="auto",  # 自动处理模型的分布
            use_cache=True,  # 启用KV缓存
            low_cpu_mem_usage=True,  # 降低CPU内存使用
        )

        self.processor = AutoProcessor.from_pretrained("qwen")
        self.processor.tokenizer = AutoTokenizer.from_pretrained(
            "qwen",
            use_fast=True,  # 使用快速tokenizer
            model_max_length=2048,  # 指定最大长度以优化内存使用
        )

        self.generation_config = {
            "max_new_tokens": 256,
            "num_beams": 1,  # 减少beam search以提高速度
            "do_sample": True,  # 启用采样以加速生成
            "top_p": 0.92,  # 使用nucleus sampling
            "temperature": 0.8,  # 适当降低温度以提高速度
            "repetition_penalty": 1.1,  # 轻微的重复惩罚
            "pad_token_id": self.processor.tokenizer.pad_token_id,
            "eos_token_id": self.processor.tokenizer.eos_token_id,
        }

    def predict(self,text,path_to_image):

        if path_to_image:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": """你是一个判别模型是否是谣言的助手，请你以json格式输出你的结果，格式：
                        IsNewsTrue：0      (0即为谣言，1即为事实)
                        reasons：       (传入一个list，里面是你的分析原因，分点)         
                        """},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": path_to_image,
                        },
                        {"type": "text", "text": text
                        },
                    ],
                }
            ]

        else:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": """你是一个判别模型是否是谣言的助手，请你以json格式输出你的结果，格式：
                        IsNewsTrue：0      (0即为谣言，1即为事实)
                        reasons：       (传入一个list，里面是你的分析原因，分点)         
                        """},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text
                        },
                    ],
                }
            ]
        text_with_messages = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
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

        with torch.cuda.amp.autocast():  
            generated_ids = self.model.generate(**inputs, **self.generation_config)

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

