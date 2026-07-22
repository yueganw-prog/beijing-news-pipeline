# Beijing News Pipeline

新闻聚合管道 — 自动化采集北京地区科技、财经、本地类新闻，经数据质量检查后入库，提供 REST API 查询服务和可视化仪表盘。

![仪表盘](screenshots/dashboard.png)

## 概览

本项目是一个**完整的数据工程管道**，涵盖数据采集、质量检查、存储归档、API 服务和前端可视化五个环节。适合作为数据工程 / 后端开发求职作品集。

### 核心能力

| 环节 | 实现 | 技术 |
|------|------|------|
| **采集** | 9 个新闻源爬虫，RSS / API / HTML 三种方式 | Python, BeautifulSoup, requests |
| **调度** | DAG 任务编排，定时抓取 + 失败重试 | Apache Airflow |
| **质量** | 空值/重复/长度检测，综合评分 | SQL, Python |
| **存储** | PostgreSQL 业务库 + MinIO 对象存储归档 | PostgreSQL 15, MinIO |
| **服务** | RESTful 查询 API，全文搜索，Swagger 文档 | FastAPI, asyncpg, gunicorn |
| **可视化** | 仪表盘统计 + 文章列表 + 详情面板 | Vue 3, Vite |
| **部署** | Docker Compose 一键部署，Nginx 反代 | Docker, Nginx |

---

## 截图

### 仪表盘
![仪表盘](screenshots/dashboard.png)

### 文章列表
![文章列表](screenshots/articles.png)

### API 文档 (Swagger)
![Swagger](screenshots/swagger.png)

---

## 新闻源

| 分类 | 来源 | 采集方式 |
|------|------|----------|
| 科技 | 36氪、虎嗅、IT之家 | RSS Feed |
| 财经 | 新浪财经、第一财经、经济观察报 | JSON API / HTML |
| 本地 | 新京报、北京日报、北京商报 | HTML 解析 |

---

## 项目结构

```
beijing-news-pipeline/
├── dags/                          # Airflow DAG 定义
│   ├── beijing_news_pipeline.py   # 主 DAG：采集 → DQ → 归档
│   └── scrapers/                  # 新闻源爬虫
│       ├── base.py                # 基类（请求、解析、清洗）
│       ├── kr36.py                # 36氪爬虫
│       ├── huxiu.py               # 虎嗅爬虫
│       ├── ithome.py              # IT之家爬虫
│       ├── sina_finance.py        # 新浪财经爬虫
│       ├── yicai.py               # 第一财经爬虫
│       ├── eeo.py                 # 经济观察报爬虫
│       ├── bjnews.py              # 新京报爬虫
│       ├── bjdaily.py             # 北京日报爬虫
│       └── bjbusiness.py          # 北京商报爬虫
│
├── api/                           # FastAPI 查询服务
│   ├── main.py                    # 应用入口：路由、模型、中间件
│   ├── Dockerfile                 # API 容器镜像
│   ├── requirements.txt           # Python 依赖
│   ├── test_main.py               # 23 个 API 单元测试
│   └── pytest.ini                 # Pytest 配置
│
├── frontend/                      # Vue 3 前端
│   ├── index.html                 # HTML 入口
│   ├── package.json               # npm 依赖与脚本
│   ├── vite.config.js             # Vite 构建配置
│   ├── styles.css                 # 全局样式（暗色主题）
│   └── scripts/
│       ├── app.js                 # Vue 应用初始化
│       ├── components.js          # 组件：Sidebar、Dashboard、Articles
│       └── api.js                 # API 请求封装
│
├── sql/
│   └── init.sql                   # 数据库初始化（表、索引、触发器、视图）
│
├── nginx/
│   └── default.conf               # Nginx 反代配置（前端 + API + Airflow）
│
├── scripts/
│   ├── deploy.sh                  # 生产环境一键部署脚本
│   ├── seed_articles.py           # 测试数据填充脚本
│   └── run_pipeline.py            # 手动触发采集管道
│
├── docker-compose.yml             # 本地开发 Docker 编排
├── docker-compose.prod.yml        # 生产环境 Docker 编排（日志限制、内网绑定）
├── .github/workflows/ci.yml       # GitHub Actions CI（自动运行测试）
└── .env                           # 环境变量（本地开发用，不入库）
```

---

## 数据表

### articles — 文章主表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL | 主键 |
| source | VARCHAR(128) | 来源标识（如 36kr、huxiu） |
| category | VARCHAR(64) | 分类：tech / finance / local |
| title | TEXT | 标题 |
| url | TEXT | 文章 URL（唯一索引） |
| author | VARCHAR(256) | 作者 |
| summary | TEXT | 摘要 |
| content_raw | TEXT | 原始正文（Markdown / HTML） |
| content_clean | TEXT | 清洗后纯文本 |
| published_at | TIMESTAMPTZ | 发布时间 |
| fetched_at | TIMESTAMPTZ | 抓取时间 |
| minio_bucket / minio_key | VARCHAR | MinIO 归档路径 |
| metadata | JSONB | 扩展字段（阅读量、标签等） |

### dq_results — 数据质量结果
每次 DAG 运行记录各来源的 DQ 指标：总行数、空值数、重复 URL 数、内容长度 min/avg、综合评分 (0-100)。

### pipeline_runs — 管道运行追踪
记录每次 DAG 执行的状态（running / success / failed）、成功来源数、采集文章数、平均 DQ 分、耗时。

### 预置视图
- `v_source_stats` — 按来源/分类统计
- `v_articles_last_7d` — 最近 7 天文章摘要
- `v_pipeline_summary` — 管道运行概览（含耗时）

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查（含数据库连接状态） |
| GET | `/articles` | 文章列表，支持 `source`、`category`、`limit`、`offset` 过滤 |
| GET | `/articles/search?q=` | 全文搜索（标题 + 摘要 + 正文），PostgreSQL `ts_rank` 排序 |
| GET | `/articles/{id}` | 单篇文章详情 |
| GET | `/stats/by-source` | 按来源统计文章数 |
| GET | `/dq-results` | DQ 检查结果，支持 `dag_run_id` 过滤 |
| GET | `/pipeline-runs` | 管道运行记录，支持 `status` 过滤 |

Swagger 文档：`http://localhost:8000/docs`

### 鉴权

API 支持可选的 API Key 鉴权。设置环境变量 `API_KEY` 后，除 `/health` 外的所有端点都要求在请求头中携带 `X-API-Key`。

```bash
# 不设置 API_KEY 时完全兼容原有行为（无鉴权）
export API_KEY="your-secret-key"

# 请求时携带
curl -H "X-API-Key: your-secret-key" http://localhost:8000/articles
```

---

## 本地开发

### 前置条件
- Python 3.11+
- PostgreSQL 17+
- Node.js 20+

### 1. 初始化数据库

```powershell
$env:PGPASSWORD='postgres'
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE airflow;"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d airflow -f sql\init.sql
```

### 2. 安装 API 依赖

```bash
cd api
pip install -r requirements.txt
```

### 3. 启动 API

```bash
cd api
$env:DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/airflow'
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 启动前端开发服务器

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器默认在 `http://localhost:5173`，自动代理 `/api` 请求到 `localhost:8000`。

### 5. 运行测试

```bash
cd api
pytest test_main.py -v    # 23 个测试，覆盖全部端点
```

### 6. 启动 Airflow（可选）

```powershell
.\run.ps1
```

---

## Docker 部署

### 本地开发环境

```bash
# 启动基础服务（PostgreSQL + MinIO + Airflow + API）
docker compose up -d

# 启动含 Metabase 仪表盘
docker compose --profile metabase up -d
```

### 生产环境

```bash
# 一键部署（HTTP 模式）
bash scripts/deploy.sh

# 一键部署（HTTPS 模式，自动申请 Let's Encrypt 证书）
bash scripts/deploy.sh --ssl your-domain.com

# 含 Metabase
bash scripts/deploy.sh --profile metabase
```

部署脚本自动完成：检查/安装 Docker → 创建 `.env` → 拉取镜像 → 构建 API → 启动全部服务 → 等待就绪。

### 服务端口

| 服务 | 端口 | 凭证 |
|------|------|------|
| Nginx（前端 + API 代理） | 80 / 443 | - |
| PostgreSQL | 5432 (仅内网) | postgres / postgres |
| MinIO API | 9000 (仅内网) | minioadmin / minioadmin123 |
| MinIO Console | 9001 | minioadmin / minioadmin123 |
| Airflow | 8080 (仅内网) | admin / admin |
| News API | 8000 (仅内网) | - |
| Metabase | 3000 | 首次访问时设置 |

> 生产环境所有服务端口绑定到 127.0.0.1，仅通过 Nginx 80/443 对外暴露。

### 更新服务

```bash
cd /opt/beijing-news-pipeline
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 获取新闻

本项目是**定时批处理管道**，不是实时流。新闻数据需要主动触发采集才能入库。

### 方式一：命令行一键运行（推荐）

`scripts/run_pipeline.py` 一次执行完整流程：**采集 → 入库 → DQ → 归档 → 记录**。

```bash
python scripts/run_pipeline.py
```

输出示例：

```
[36kr] 30 篇采集, 30 篇新入库
[huxiu] 49 篇采集, 49 篇新入库
[ithome] 60 篇采集, 60 篇新入库
...
入库完成，共 280 篇新文章
DQ: score=84.1 rows=280 null_title=0 dup=0
归档 280 篇到 MinIO
=== 管道完成 ===
```

> **注意**：Airflow DAG（`beijing_news_pipeline`）只负责调度采集和归档，不写入 `articles` 表。始终用 `run_pipeline.py` 来入库文章。

### 方式二：Airflow 定时调度

打开 `http://localhost:8080`（admin / admin），找到 `beijing_news_pipeline` DAG：

- **手动触发**：点击右侧 ▶ 按钮 → Trigger DAG
- **定时执行**：默认每天 8:00 和 18:00 自动运行

> 如果 Airflow 触发后前端看不到新数据，再运行一次 `python scripts/run_pipeline.py` 入库即可。

### 修改采集频率

编辑 `dags/beijing_news_pipeline.py` 中的 `schedule` 参数：

```python
schedule="0 8,18 * * *"    # 默认：每天 8 点和 18 点
schedule="0 * * * *"       # 每小时
schedule="*/30 * * * *"    # 每 30 分钟
```

修改后重启 Airflow 容器使配置生效：

```bash
docker compose restart airflow-scheduler
```

---

## 添加新闻源

1. 在 `dags/scrapers/` 创建爬虫文件，继承 `BaseScraper`，实现 `fetch()` 方法
2. 在 `__init__.py` 的 `_SCRAPER_REGISTRY` 注册
3. 在 DAG 文件 `DEFAULT_SOURCES` 中添加条目

示例：
```python
# dags/scrapers/my_source.py
from .base import BaseScraper

class MySourceScraper(BaseScraper):
    name = "my_source"
    category = "tech"

    def fetch(self):
        # 返回 list[dict]，每个 dict 包含 title, url, summary 等字段
        return self._parse_rss("https://example.com/feed.xml")
```

---

## 生产版 vs 本地版

| 区别 | 本地版 (docker-compose.yml) | 生产版 (docker-compose.prod.yml) |
|------|---------------------------|----------------------------------|
| 端口绑定 | `0.0.0.0` 直接暴露 | `127.0.0.1` 仅 Nginx 对外 |
| Nginx 反代 | 无 | 前端 + API + Airflow 统一入口 |
| API 数据库连接 | `host.docker.internal` | 容器内服务名 `postgres` |
| API 运行方式 | `uvicorn` 单 worker | `gunicorn + uvicorn` 4 workers |
| 日志 | 无限制 | `max-size: 10m, max-file: 3` |
| 前端 | 源文件 | Vite 构建产物 (dist/) |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.12 |
| 爬虫 | requests, BeautifulSoup4, lxml |
| 调度 | Apache Airflow 2.10 |
| 数据库 | PostgreSQL 15 |
| 对象存储 | MinIO |
| API 框架 | FastAPI, Pydantic V2 |
| API 服务器 | gunicorn + uvicorn |
| 前端 | Vue 3, Vite |
| 容器化 | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| 反代 | Nginx |
| 测试 | pytest, pytest-asyncio, httpx |

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://postgres:postgres@localhost:5432/airflow` |
| `MINIO_ENDPOINT` | MinIO 地址 | `http://localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO 访问密钥 | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO 密钥 | `minioadmin123` |
| `API_KEY` | API 鉴权密钥（空 = 关闭鉴权） | (空) |
| `TZ` | 时区 | `Asia/Shanghai` |
