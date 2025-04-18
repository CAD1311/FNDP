# 智能问答系统

## 项目简介
这是一个基于FastAPI和Vue.js的全栈Web应用程序，集成了大语言模型，提供智能问答功能。项目基于RuoYi框架进行开发，包含完整的前后端实现。

## 技术栈
### 后端
- Python 3.x
- FastAPI
- MySQL
- PyTorch 2.23.1
- CUDA 11.8+
- Qwen大语言模型

### 前端
- Vue.js
- Node.js
- Vite

## 系统要求
- CUDA 11.8或更高版本
- Python 3.x
- Node.js
- MySQL数据库
- 足够的GPU显存以运行大语言模型

## 安装步骤

### 1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

### 2. 后端配置
```bash
# 进入后端目录
cd ruoyi-fastapi-backend

# 安装Python依赖
pip install -r requirements.txt

# 配置大语言模型
# 将final.zip解压后重命名为qwen，放置在ruoyi-fastapi-backend目录下
```

### 3. 数据库配置
```sql
# 创建数据库
CREATE DATABASE test;

# 配置用户权限
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';

# 导入数据
mysql -u root -p test < dump-test.sql
```

### 4. 前端配置
```bash
# 进入前端目录
cd ruoyi-fastapi-frontend

# 安装依赖
npm install

# 安装Vite
npm install vite
```

## 启动服务

### 启动后端服务
```bash
cd ruoyi-fastapi-backend
python app.py
```
后端服务将在9099端口启动

### 启动前端服务
```bash
cd ruoyi-fastapi-frontend
npm run dev
```

## 项目结构
```
├── ruoyi-fastapi-backend/    # 后端项目目录
├── ruoyi-fastapi-frontend/   # 前端项目目录
├── miniprogram/              # 小程序目录
├── models/                   # 模型目录
├── vector_store/            # 向量存储目录
└── start_services.bat       # 服务启动脚本
```

## 使用说明
[在这里添加系统的主要功能和使用方法说明]

## 注意事项
1. 确保CUDA和PyTorch版本匹配
2. 运行大语言模型需要足够的GPU显存
3. 请确保所有必要的端口未被占用

## 贡献指南
[如何贡献代码，提交Issue等说明]

## 许可证
[添加许可证信息]