# RSS Reader 部署文档

## 项目简介

这是一个基于 Vue 3 + FastAPI 的 RSS 阅读器应用，支持 AI 智能问答功能。

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 前端 | Vue 3 + Vite + TailwindCSS | Vue 3.4, Vite 5 |
| 后端 | FastAPI + Python | FastAPI 0.100+ |
| 数据库 | PostgreSQL | 15 |
| 向量库 | Milvus | 2.3.0 |
| AI | Google Gemini | - |

---

## 环境要求

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Node.js** >= 18 (仅本地开发)
- **Python** >= 3.10 (仅本地开发)

---

## 一、Docker Compose 部署 (推荐)

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd rssReader
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

> [!IMPORTANT]
> 请将 `your-gemini-api-key-here` 替换为你的实际 Gemini API Key。
> 获取地址：https://aistudio.google.com/app/apikey

### 3. 启动所有服务

```bash
docker-compose up -d --build
```

### 4. 访问应用

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://localhost:8021 |
| API 文档 | http://localhost:8021/docs |
| MinIO 控制台 | http://localhost:9001 |

### 5. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 6. 停止服务

```bash
docker-compose down

# 如需清除数据卷
docker-compose down -v
```

---

## 二、本地开发部署

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (编辑 .env 文件)

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8021
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

---

## 三、服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Frontend | 5173 | Vue 前端应用 |
| Backend | 8021 | FastAPI 后端服务 |
| PostgreSQL | 54321 (外部映射) | 关系型数据库 |
| Milvus | 19530 | 向量数据库 |
| MinIO | 9000, 9001 | 对象存储 (Milvus 依赖) |

---

## 四、数据库配置

### PostgreSQL

- **用户名**: `postgres`
- **密码**: `postgres`
- **数据库**: `rss_reader`
- **本地连接**: `postgresql://postgres:postgres@localhost:54321/rss_reader`

### Milvus

- **Host**: `localhost` (本地) / `milvus-standalone` (Docker)
- **Port**: `19530`

---

## 五、常见问题

### Q: Milvus 启动失败

确保 Docker 有足够的内存分配（建议至少 4GB）。

### Q: 后端无法连接数据库

检查 `.env` 文件中的 `DATABASE_URL` 配置是否正确。Docker 环境下使用服务名 `db`，本地开发使用 `localhost:54321`。

### Q: AI 功能不可用

确保已正确配置 `GEMINI_API_KEY` 环境变量。

---

## 六、生产部署建议

1. **安全性**
   - 修改默认数据库密码
   - 设置强 `SECRET_KEY`
   - 配置 HTTPS

2. **性能**
   - 配置 Nginx 反向代理
   - 启用 Gzip 压缩
   - 配置 Redis 缓存（可选）

3. **监控**
   - 配置日志收集
   - 设置健康检查告警
