import asyncio
import logging
import time
import json
import random
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Qwen:
    """
    A mock implementation of the Qwen model for testing purposes.
    Simulates the same interface but doesn't require actual model resources.
    """

    def __init__(self, max_batch_size=4, max_concurrent_requests=8) -> None:
        """
        Initialize the mock Qwen model

        Args:
            max_batch_size: Maximum number of requests to process in a single batch
            max_concurrent_requests: Maximum number of concurrent requests to process
        """
        logger.info("Initializing Mock Qwen model...")

        # Batch processing configuration
        self.max_batch_size = max_batch_size
        self.max_concurrent_requests = max_concurrent_requests
        self.request_queue = asyncio.Queue()

        # Control flags
        self.is_running = True
        self.batch_task = None

        # Mock generation config (for reference only)
        self.generation_config = {
            "max_new_tokens": 256,
            "num_beams": 1,
            "do_sample": True,
            "top_p": 0.92,
            "temperature": 0.8,
            "repetition_penalty": 1.1,
        }

        logger.info("Mock Qwen model initialization complete")

    async def start(self):
        """Start the batch processing loop"""
        if self.batch_task is None:
            self.batch_task = asyncio.create_task(self._batch_process_loop())
            logger.info("-------------------------------Batch processing loop started---------------------------------")

    async def stop(self):
        """Stop the batch processing loop"""
        if self.batch_task:
            self.is_running = False
            
            # 清空队列并取消所有等待中的future
            while not self.request_queue.empty():
                future, _ = await self.request_queue.get()
                if not future.done():
                    future.set_exception(asyncio.CancelledError("Service stopped"))
                self.request_queue.task_done()

            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
            finally:
                self.batch_task = None
                logger.info("Batch processing loop stopped")

    async def _process_request(self, text: str, path_to_image: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare mock model input (simulates the preprocessing step)

        Args:
            text: The input text
            path_to_image: Optional path to an image

        Returns:
            Dictionary containing mock preprocessed inputs
        """
        logger.info(f"Processing request: text='{text[:30]}...' image={'Yes' if path_to_image else 'No'}")


        # Create mock inputs structure
        mock_inputs = {
            "inputs": {
                "input_ids": "mock_tensor",
                "attention_mask": "mock_tensor"
            },
            "original_length": len(text) + random.randint(50, 100),  # Simulate tokenized length
            "has_image": path_to_image is not None
        }

        logger.info("------------------------------1-----------------------------------")
        if path_to_image:
            mock_inputs["inputs"]["image_features"] = "mock_image_tensor"

        return mock_inputs

    async def _batch_process_loop(self):
        """Main batch processing loop"""
        while self.is_running:
            try:
                # Collect batch requests
                batch = []
                future_list = []

                # Get first request (blocking)
                future, data = await self.request_queue.get()
                batch.append(data)
                future_list.append(future)

                # Try to collect more requests (non-blocking) until max batch size
                batch_timeout = 0.01  # 10ms batch collection window
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
                    # Process batch
                    logger.info(f"Processing batch, batch size: {len(batch)}")
                    results = await self._process_batch(batch)

                    # Set results for futures
                    for i, future in enumerate(future_list):
                        if not future.cancelled():
                            logger.info(f"Setting result for future {i}: {results[i][:50]}")
                            future.set_result(results[i])

                    # Mark tasks as done
                    for _ in range(len(batch)):
                        self.request_queue.task_done()
                        logger.info(f"Batch completed: {len(batch)} requests processed")

            except asyncio.CancelledError:
                logger.info("Batch processing loop cancelled")
                break
            except Exception as e:
                logger.error("Batch processing error:", exc_info=True)
                logger.error(f"Batch processing loop error: {e}", exc_info=True)
                # Set exceptions for all waiting futures
                for future in future_list:
                    if not future.done():
                       logger.error(f"Setting exception for future: {str(e)}")
                       future.set_exception(e)

                # Mark tasks as done
                for _ in range(len(batch)):
                    self.request_queue.task_done()

                # Brief pause to prevent error loops consuming resources
                await asyncio.sleep(0.1)

    async def _process_batch(self, batch: List[Dict[str, Any]]) -> List[str]:
        """
        Process a batch of requests

        Args:
            batch: List of preprocessed request data

        Returns:
            List of mock results
        """
        # Simulate batch processing time (proportional to batch size but with some optimization)
        process_time = 0.2 + (0.1 * len(batch))

        # Randomly vary the processing time a bit to simulate realistic behavior
        process_time *= random.uniform(0.8, 1.2)

        start_time = time.perf_counter()
        await asyncio.sleep(process_time)
        end_time = time.perf_counter()

        logger.info(
            f"Batch generation complete, processing time: {end_time - start_time:.2f}s, batch size: {len(batch)}")

        # Generate mock results
        results = []
        for item in batch:
            # Generate a mock JSON response similar to what the real model would produce
            has_image = item.get("has_image", False)

            # Randomize the IsNewsTrue value with a bias toward 0 for longer text
            is_true = random.choice([0, 1, 0])

            # Randomize the number of reasons based on item properties
            num_reasons = random.randint(1, 5)

            # Create mock response
            mock_result = self._generate_mock_response(is_true, num_reasons, has_image)
            results.append(mock_result)

        return results

    def _generate_mock_response(self, is_true: int, num_reasons: int, has_image: bool) -> str:
        """
        Generate a mock JSON response similar to what the real model would produce

        Args:
            is_true: 0 for false information, 1 for true
            num_reasons: Number of reasons to include
            has_image: Whether the request included an image

        Returns:
            Mock JSON response as a string
        """
        image_context = "图像显示" if has_image else ""

        # Define possible reasons for true and false information
        true_reasons = [
            f"信息来源可靠，{image_context}内容由官方权威机构发布",
            "内容符合科学常识和基本逻辑，没有明显的矛盾之处",
            "文本中包含可验证的具体事实和数据",
            "叙述方式客观中立，没有情绪化和煽动性语言",
            "信息已被多个权威来源证实"
        ]

        false_reasons = [
            f"信息来源不明，{image_context}没有提供官方或权威渠道的证据",
            "内容存在逻辑矛盾，违背基本科学常识",
            "包含明显的情绪化和煽动性语言，目的可能是引起恐慌",
            "文中的数据和声明缺乏具体来源和背景",
            "已有官方辟谣或权威机构否认相关信息"
        ]

        # Select reasons based on true/false status
        if is_true == 1:
            selected_reasons = random.sample(true_reasons, min(num_reasons, len(true_reasons)))
            recommendation = "这条信息可信度较高，可以参考，但建议同时查阅其他官方来源进行验证。"
        else:
            selected_reasons = random.sample(false_reasons, min(num_reasons, len(false_reasons)))
            recommendation = "建议对此信息保持谨慎，不要轻信或传播，可查询官方渠道获取准确信息。"

        # Create response object
        response = {
            "IsNewsTrue": is_true,
            "reasons": selected_reasons,
            "recommendation": recommendation
        }

        # Convert to JSON string
        return json.dumps(response, ensure_ascii=False, indent=2)

    async def predict(self, text: str, path_to_image: Optional[str] = None) -> str:
        """
        Async predict function - main entry point for model inference

        Args:
            text: Input text
            path_to_image: Optional path to image

        Returns:
            Prediction result
        """
        # Prepare request data
        data = await self._process_request(text, path_to_image)
        logger.info("------------------------------2-----------------------------------")
        # Create future object
        future = asyncio.Future()
        logger.info("------------------------------3-")
        # Submit to request queue
        await self.request_queue.put((future, data))
        logger.info("------------------------------4-")
        # Wait for result
        result = await future
  
        return result