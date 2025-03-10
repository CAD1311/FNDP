from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import time
import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Qwen:
    def __init__(self, max_batch_size=4, max_concurrent_requests=8) -> None:
        """
        初始化异步 Qwen 模型

        Args:
            max_batch_size: 单次批处理的最大请求数
            max_concurrent_requests: 并行处理的最大请求数
        """
        logger.info("正在初始化 Qwen 模型...")
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            "qwen",
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device_map="auto",
            use_cache=True,
            low_cpu_mem_usage=True,
        )

        self.processor = AutoProcessor.from_pretrained("qwen")
        self.processor.tokenizer = AutoTokenizer.from_pretrained(
            "qwen",
            use_fast=True,
            model_max_length=4096,
        )

        self.generation_config = {
            "max_new_tokens": 256,
            "num_beams": 1,
            "do_sample": True,
            "top_p": 0.92,
            "temperature": 0.8,
            "repetition_penalty": 1.1,
            "pad_token_id": self.processor.tokenizer.pad_token_id,
            "eos_token_id": self.processor.tokenizer.eos_token_id,
        }

        # 批处理相关配置
        self.max_batch_size = max_batch_size
        self.max_concurrent_requests = max_concurrent_requests
        self.request_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=2)  # 用于执行CPU密集型预处理

        # 启动批处理循环
        self.is_running = True
        self.batch_task = None
        logger.info("Qwen 模型初始化完成")

    async def start(self):
        """启动批处理循环"""
        if self.batch_task is None:
            self.batch_task = asyncio.create_task(self._batch_process_loop())
            logger.info("批处理循环已启动")

    async def stop(self):
        """停止批处理循环"""
        if self.batch_task:
            self.is_running = False
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
            self.batch_task = None
            logger.info("批处理循环已停止")

        # 清理资源
        self.executor.shutdown(wait=False)

    async def _process_request(self, text, path_to_image=None):
        """准备模型输入"""
        if path_to_image:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "你是一个专业的谣言分析助手，擅长运用批判性思维和专业知识评估信息真实性。分析后，请以JSON格式输出结果：\n\n{\n  \"IsNewsTrue\": 0或1,  // 0表示谣言，1表示可信事实\n  \"reasons\": [  // 列出你分析的具体理由，请至少提供3-5点关键理由\n    \"理由1\",\n    \"理由2\",\n    \"...\"\n  ],\n  \"recommendation\": \"用户行动建议\"  // 针对此信息，给用户的建议\n}\n\n分析时请考虑以下关键因素：\n- 信息来源的可靠性和权威性\n- 逻辑一致性和证据支持\n- 是否有相互矛盾之处\n- 符合已知科学规律和常识的程度\n- 是否包含情绪化语言或煽动性内容\n- 是否有官方辟谣或权威机构确认"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": path_to_image,
                        },
                        {"type": "text", "text": text + "<image>"
                         },
                    ],
                }
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"type": "text",
                         "text": "你是一个专业的谣言分析助手，擅长运用批判性思维和专业知识评估信息真实性。分析后，请以JSON格式输出结果：\n\n{\n  \"IsNewsTrue\": 0或1,  // 0表示谣言，1表示可信事实\n  \"reasons\": [  // 列出你分析的具体理由，请至少提供3-5点关键理由\n    \"理由1\",\n    \"理由2\",\n    \"...\"\n  ],\n  \"recommendation\": \"用户行动建议\"  // 针对此信息，给用户的建议\n}\n\n分析时请考虑以下关键因素：\n- 信息来源的可靠性和权威性\n- 逻辑一致性和证据支持\n- 是否有相互矛盾之处\n- 符合已知科学规律和常识的程度\n- 是否包含情绪化语言或煽动性内容\n- 是否有官方辟谣或权威机构确认"
                         },
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

        # 使用线程池执行CPU密集型的处理操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._prepare_inputs,
            messages
        )

        return result

    def _prepare_inputs(self, messages):
        """准备模型输入 (CPU密集型处理)"""
        text_with_messages = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.processor(
            text=[text_with_messages],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        return {
            "inputs": inputs,
            "original_length": len(inputs.input_ids[0])
        }

    async def _batch_process_loop(self):
        """批处理主循环"""
        while self.is_running:
            try:
                # 收集请求批次
                batch = []
                future_list = []

                # 获取第一个请求（阻塞）
                future, data = await self.request_queue.get()
                batch.append(data)
                future_list.append(future)

                # 尝试获取更多请求（非阻塞）直到达到最大批处理大小
                batch_timeout = 0.01  # 10毫秒的批处理收集窗口
                batch_start = time.time()

                while (len(batch) < self.max_batch_size and
                       time.time() - batch_start < batch_timeout):
                    try:
                        future, data = self.request_queue.get_nowait()
                        batch.append(data)
                        future_list.append(future)
                    except asyncio.QueueEmpty:
                        await asyncio.sleep(0.001)

                if batch:
                    # 处理批次
                    logger.info(f"处理批次，批次大小: {len(batch)}")
                    results = await self._process_batch(batch)

                    # 设置结果
                    for i, future in enumerate(future_list):
                        if not future.cancelled():
                            future.set_result(results[i])

                    # 通知队列任务完成
                    for _ in range(len(batch)):
                        self.request_queue.task_done()

            except asyncio.CancelledError:
                logger.info("批处理循环被取消")
                break
            except Exception as e:
                logger.error(f"批处理循环错误: {e}", exc_info=True)
                # 为所有等待的future设置异常
                for future in future_list:
                    if not future.done():
                        future.set_exception(e)

                # 通知队列任务完成
                for _ in range(len(batch)):
                    self.request_queue.task_done()

                # 短暂暂停以防止错误循环消耗资源
                await asyncio.sleep(0.1)

    async def _process_batch(self, batch):
        """处理一批请求"""
        # 将所有输入合并为一个批处理
        all_inputs = []
        original_lengths = []

        for item in batch:
            all_inputs.append(item["inputs"])
            original_lengths.append(item["original_length"])

        # 批处理输入合并
        batch_inputs = {
            "input_ids": torch.cat([inp["input_ids"] for inp in all_inputs], dim=0),
            "attention_mask": torch.cat([inp["attention_mask"] for inp in all_inputs], dim=0),
        }

        # 如果有图像特征，也需要合并
        if "image_features" in all_inputs[0]:
            batch_inputs["image_features"] = torch.cat([inp["image_features"] for inp in all_inputs], dim=0)

        # 移动到GPU
        batch_inputs = {k: v.to("cuda") for k, v in batch_inputs.items()}

        # 执行生成
        start_time = time.perf_counter()

        with torch.cuda.amp.autocast():
            generated_ids = self.model.generate(**batch_inputs, **self.generation_config)

        end_time = time.perf_counter()
        logger.info(f"批处理生成完成，处理时间: {end_time - start_time:.2f}秒，批次大小: {len(batch)}")

        # 解码并返回每个请求的输出
        results = []
        for i, orig_len in enumerate(original_lengths):
            # 只保留生成的新token
            generated_ids_trimmed = generated_ids[i][orig_len:]

            # 解码生成的文本
            output_text = self.processor.batch_decode(
                [generated_ids_trimmed],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]

            results.append(output_text)

        return results

    async def predict(self, text, path_to_image=None):
        """异步预测函数"""
        # 准备请求数据
        data = await self._process_request(text, path_to_image)

        # 创建future对象
        future = asyncio.Future()

        # 提交到请求队列
        await self.request_queue.put((future, data))

        # 等待结果
        result = await future
        return result

