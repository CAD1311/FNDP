# BreezeGuard: Intelligent False News Detection System
# 清风知言虚假新闻检测系统

## 项目简介
这是一个基于FastAPI和Vue.js的全栈Web应用程序，集成了大语言模型，提供智能问答和虚假新闻检测功能。项目基于RuoYi框架进行开发，包含完整的前后端实现。本项目是2025年服务外包大赛A21赛题的比赛项目，可供参考。

## 项目功能
本项目主要包含以下组件和功能：
- **Web端 (`ruoyi-fastapi-frontend`)**: 提供用户界面，支持新闻管理、虚假新闻检测请求等。
- **FastAPI服务端 (`ruoyi-fastapi-backend`)**: 处理业务逻辑、数据库交互和调用大模型进行新闻检测。
- **浏览器插件 (`browser_utils`)**: 允许用户在浏览网页时直接对当前新闻内容进行检测。
- **小程序 (`miniprogram`)**: 提供移动端入口，支持输入或粘贴新闻文本进行检测。

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
前端开发服务器将启动。请检查终端输出确认访问端口（通常是 5173 或在 `vite.config.js` 中配置的端口，您之前提到可能是 8000）。

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
系统启动后，您可以通过以下方式使用虚假新闻检测功能：
1.  **Web端**: 访问前端服务地址，在管理界面提交新闻内容或链接进行检测。
2.  **浏览器插件**: 安装插件后，在浏览新闻页面时点击插件图标，对当前页面内容进行分析。
3.  **小程序**: 打开小程序，输入或粘贴新闻文本进行检测。

## 注意事项
1. 确保后端服务 `config.py` (或其他配置文件) 中的数据库连接信息正确。
2. 确保大语言模型文件 (`qwen`) 已正确放置在 `ruoyi-fastapi-backend` 目录下。
3. 确保 CUDA 和 PyTorch 版本与您的环境和模型要求匹配。
4. 运行大语言模型需要足够的 GPU 显存（例如 Qwen2.5VL-3B 建议至少 10GB）。
5. 请确保后端（9099）和前端（例如 8000 或 5173）所需端口未被其他程序占用。

<!-- ## 贡献指南
我们欢迎对本项目的贡献！如果您有任何建议或发现 Bug，请提交 Issue。
如果您想贡献代码，请遵循以下步骤：
1. Fork 本仓库
2. 创建您的 Feature 分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request -->

## 许可证
[建议添加许可证信息，例如 MIT License 或 Apache License 2.0]






