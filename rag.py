import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Tuple, Optional
import time


class SimpleVectorStore:
    """简单向量存储类，用于存储文档和对应的嵌入向量，支持GPU推理"""

    def __init__(self, embedding_model: str = 'shibing624/text2vec-base-chinese', model_cache_dir: str = None,
                 device: Optional[str] = None):
        # 自动检测设备
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        self.documents = []  # 存储原始文档
        self.embeddings = None  # 存储文档的嵌入向量，将使用NumPy数组

        self.model = SentenceTransformer(
            embedding_model,
            cache_folder=model_cache_dir,
            device=self.device,
            local_files_only=True
        )

        print(f"模型已加载到 {self.device} 设备")

    def add_documents(self, documents: List[str]) -> None:
        with torch.no_grad():
            embeddings = self.model.encode(documents, convert_to_tensor=True)
            embeddings_np = embeddings.cpu().numpy() if self.device == 'cuda' else embeddings.numpy()

        self.documents.extend(documents)

        if self.embeddings is None:
            self.embeddings = embeddings_np
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings_np])

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Args:
            query: 查询文本
            top_k: 返回的最相关文档数量

        Returns:
            最相关的文档及其相似度分数列表
        """
        if len(self.documents) == 0:
            return []

        # 计算查询的嵌入向量
        with torch.no_grad():
            query_embedding = self.model.encode([query], convert_to_tensor=True)

        if self.device == 'cuda':
            # 将查询嵌入保持在GPU上
            # 将存储的嵌入向量转移到GPU
            embeddings_tensor = torch.tensor(self.embeddings, device='cuda')

            # 计算余弦相似度 (点积，因为向量已归一化)
            similarities = torch.mm(query_embedding, embeddings_tensor.t()).squeeze(0)
            similarities = similarities.cpu().numpy()
        else:
            # CPU版本，使用NumPy计算
            query_embedding_np = query_embedding.numpy()
            # 计算余弦相似度 (点积，因为向量已归一化)
            similarities = np.dot(query_embedding_np, self.embeddings.T)[0]

        # 获取top_k个最相关文档的索引
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        # 返回最相关的文档及其相似度
        return [(self.documents[i], float(similarities[i])) for i in top_indices]

    def clear(self) -> None:
        """清空存储并释放GPU内存"""
        self.documents = []
        self.embeddings = None
        # 清理GPU缓存
        if self.device == 'cuda':
            torch.cuda.empty_cache()

    def save(self, save_dir: str) -> None:
        """保存向量存储到指定目录

        Args:
            save_dir: 保存目录
        """
        import os
        import json

        # 创建保存目录（如果不存在）
        os.makedirs(save_dir, exist_ok=True)

        # 保存文档到JSON文件
        with open(os.path.join(save_dir, 'documents.json'), 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

        # 保存嵌入向量到NumPy文件
        if self.embeddings is not None:
            np.save(os.path.join(save_dir, 'embeddings.npy'), self.embeddings)

        print(f"向量存储已保存到 {save_dir}，包含 {len(self.documents)} 个文档")

    @classmethod
    def load(cls, save_dir: str, embedding_model: str = 'shibing624/text2vec-base-chinese',
             model_cache_dir: str = None, device: Optional[str] = None) -> 'SimpleVectorStore':
        """从指定目录加载向量存储

        Args:
            save_dir: 保存目录
            embedding_model: 嵌入模型名称
            model_cache_dir: 模型缓存目录
            device: 设备类型，None表示自动检测

        Returns:
            加载的向量存储对象
        """
        import os
        import json

        # 创建新实例
        instance = cls(embedding_model=embedding_model, model_cache_dir=model_cache_dir, device=device)

        # 加载文档
        documents_path = os.path.join(save_dir, 'documents.json')
        if os.path.exists(documents_path):
            with open(documents_path, 'r', encoding='utf-8') as f:
                instance.documents = json.load(f)
        else:
            raise FileNotFoundError(f"无法找到文档文件: {documents_path}")

        # 加载嵌入向量
        embeddings_path = os.path.join(save_dir, 'embeddings.npy')
        if os.path.exists(embeddings_path):
            instance.embeddings = np.load(embeddings_path)
        else:
            raise FileNotFoundError(f"无法找到嵌入向量文件: {embeddings_path}")

        print(f"向量存储已从 {save_dir} 加载，包含 {len(instance.documents)} 个文档")
        return instance

    @classmethod
    def load(cls, save_dir: str, embedding_model: str = 'shibing624/text2vec-base-chinese',
             model_cache_dir: str = None, device: Optional[str] = None) -> 'SimpleVectorStore':
        """从指定目录加载向量存储

        Args:
            save_dir: 保存目录
            embedding_model: 嵌入模型名称
            model_cache_dir: 模型缓存目录
            device: 设备类型，None表示自动检测

        Returns:
            加载的向量存储对象
        """
        import os
        import json

        # 创建新实例
        instance = cls(embedding_model=embedding_model, model_cache_dir=model_cache_dir, device=device)

        # 加载文档
        documents_path = os.path.join(save_dir, 'documents.json')
        if os.path.exists(documents_path):
            with open(documents_path, 'r', encoding='utf-8') as f:
                instance.documents = json.load(f)
        else:
            raise FileNotFoundError(f"无法找到文档文件: {documents_path}")

        # 加载嵌入向量
        embeddings_path = os.path.join(save_dir, 'embeddings.npy')
        if os.path.exists(embeddings_path):
            instance.embeddings = np.load(embeddings_path)
        else:
            raise FileNotFoundError(f"无法找到嵌入向量文件: {embeddings_path}")

        print(f"向量存储已从 {save_dir} 加载，包含 {len(instance.documents)} 个文档")
        return instance


class SimpleRAG:
    """简单的检索增强生成 (RAG) 实现，支持GPU加速"""

    def __init__(self, vector_store: SimpleVectorStore, prompt_template: str = None):
        """
        Args:
            vector_store: 向量存储对象
            prompt_template: 用于生成的提示模板
        """
        self.vector_store = vector_store

        # 默认提示模板
        self.prompt_template = prompt_template or """
        基于以下信息回答问题:
        相关文档:
        {context}
        问题: {query}
        回答:
        """

    def generate(self, query: str, top_k: int = 3) -> str:
        """根据查询生成回答
        Args:
            query: 用户查询
            top_k: 检索的文档数量
        Returns:
            生成的回答
        """
        # 检索相关文档
        relevant_docs = self.vector_store.search(query, top_k)

        # 组合检索到的文档
        context = "\n\n".join([f"文档 {i + 1} (相似度: {score:.4f}):\n{doc}"
                               for i, (doc, score) in enumerate(relevant_docs)])

        # 准备输入提示
        prompt = self.prompt_template.format(context=context, query=query)
        return prompt


def load_documents_from_folder(folder_path: str) -> List[str]:
    """从文件夹中加载文档"""
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                documents.append(f.read())
    return documents


def main():
    # 指定模型下载目录和向量存储保存目录
    model_cache_dir = "./models"
    save_dir = "./vector_store"

    # 检查GPU是否可用
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")

    # 尝试加载现有向量存储，如果不存在则创建新的
    if os.path.exists(save_dir) and os.path.isfile(os.path.join(save_dir, 'documents.json')):
        print("加载现有向量存储...")
        vector_store = SimpleVectorStore.load(
            save_dir=save_dir,
            embedding_model='shibing624/text2vec-base-chinese',
            model_cache_dir=model_cache_dir,
            device=device
        )
    else:
        print("创建新的向量存储...")
        vector_store = SimpleVectorStore(
            embedding_model='shibing624/text2vec-base-chinese',
            model_cache_dir=model_cache_dir,
            device=device
        )

        # 加载示例文档
        documents = load_documents_from_folder('output')
        print(f"从文件夹加载了 {len(documents)} 个文档")

        # 添加文档到向量存储
        start_time = time.perf_counter()
        vector_store.add_documents(documents)
        print(f"文档嵌入耗时: {time.perf_counter() - start_time:.2f}秒")

        # 保存向量存储
        vector_store.save(save_dir)

    # 初始化RAG系统
    rag = SimpleRAG(vector_store)

    # 测试查询
    query = "马云"
    start_time = time.perf_counter()
    result = rag.generate(query)
    print(f"查询时间: {time.perf_counter() - start_time:.4f}秒")

    print(f"查询: {query}")
    print("\n" + result)

    # 清理资源
    vector_store.clear()


if __name__ == "__main__":
    main()