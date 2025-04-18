# BreezeGuard: Intelligent False News Detection System
# 清风知言虚假新闻检测系统

## 项目简介
这是一个基于FastAPI和Vue.js的全栈Web应用程序，集成了大语言模型，提供智能问答和虚假新闻检测功能。项目基于RuoYi框架进行开发，包含完整的前后端实现。本项目是2025年服务外包大赛A21赛题的比赛项目,大家可以参考

## 项目功能
本项目包含了以下组件的简单实现:
-Web端 ruoyi-fastapi-frontend
-Fastapi服务端 ruoyi-fastapi-backend
-浏览器插件端 browser_utils
-小程序 miniprogram


## 系统要求
- CUDA 11.8或更高版本
- Python 3.10
- Node.js
- MySQL数据库,运行在本地的3306端口上
- 足够的GPU显存以运行大语言模型(如本项目所使用的Qwen2.5VL-3B,最低的显存要求为10gb)

## 安装步骤

### 1. 克隆项目
```bash
git clone git@github.com:CAD1311/FNDP.git
cd FNDP
```

### 2. 后端配置
```bash
# 进入后端目录
cd ruoyi-fastapi-backend

# 安装Python依赖
pip install -r requirements.txt

# 配置大语言模型
将模型(在huggingface社区支持的)解压后重命名为qwen，放置在ruoyi-fastapi-backend目录下
```

### 3. 数据库配置
```sql
# 创建数据库
CREATE DATABASE test;

# 配置用户权限
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';

# 导入动态路由和初始用户等数据
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
web服务将会在8000端口启动

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
本项目提供多种功能:
web端


