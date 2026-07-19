# Beijing News Pipeline

新闻聚合管道：自动化采集北京地区科技、财经、本地类新闻，经质量检查后入库并提供查询 API。

**架构:** Python + Airflow + PostgreSQL + MinIO + FastAPI

## 新闻源

| 分类 | 来源 | 方式 |
|------|------|------|
| 科技 | 36氪、虎嗅、IT之家 | RSS Feed |
| 财经 | 新浪财经、第一财经、经济观察报 | JSON API / HTML |
| 本地 | 新京报、北京日报、北京商报 | HTML |

## 目录结构

```
beijing-news-pipeline/
  dags/                        # Airflow DAG 与爬虫
    scrapers/                  # 9 个新闻源爬虫 (base.py + 实现)
    beijing_news_pipeline.py   # 主 DAG: 采集 -> DQ -> 归档
  api/                         # FastAPI 查询服务
    main.py
  sql/                         # 数据库初始化
    init.sql
  docker-compose.yml           # 容器化部署
  run.ps1                      # 本地一键启动
  .env                         # 环境变量
```

## 快速开始

**前置:** PostgreSQL 17+ 已安装并运行。

```powershell
# 1. 初始化数据库
$env:PGPASSWORD='postgres'
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE airflow;"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d airflow -f sql\init.sql

# 2. 安装 API 依赖
.local\airflow-venv\Scripts\pip.exe install -r api\requirements.txt

# 3. 一键启动所有服务
.\run.ps1

# 或单独启动 API
$env:DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/airflow'
.local\airflow-venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker 部署

```powershell
docker compose up -d                     # 基础服务
docker compose --profile metabase up -d  # 含 Metabase 仪表盘
```

服务端口:

| 服务 | 端口 | 凭证 |
|------|------|------|
| PostgreSQL | 5432 | postgres / postgres |
| MinIO API | 9000 | minioadmin / minioadmin123 |
| MinIO Console | 9001 | minioadmin / minioadmin123 |
| Airflow | 8080 | admin / admin |
| API | 8000 | - |
| Metabase | 3000 | - |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/articles` | 文章列表 (source/category/limit/offset) |
| GET | `/articles/{id}` | 单篇文章详情 |
| GET | `/stats/by-source` | 按来源统计 |
| GET | `/dq-results` | DQ 检查结果 |
| GET | `/pipeline-runs` | 管道运行记录 |

Swagger 文档: `http://localhost:8000/docs`

## 添加新闻源

1. 在 `dags/scrapers/` 创建爬虫文件，继承 `BaseScraper`，实现 `fetch()` 方法
2. 在 `__init__.py` 注册 `_SCRAPER_REGISTRY`
3. 在 DAG 的 `DEFAULT_SOURCES` 中添加条目

## 数据表

- `articles` — 文章主表 (url 唯一索引，含 published_at, fetched_at 等 17 个字段)
- `dq_results` — DQ 打分 (每次运行记录 null/dup/min/avg/score)
- `pipeline_runs` — 管道运行状态追踪
- 预置视图: `v_source_stats`, `v_articles_last_7d`, `v_pipeline_summary`


## 生产部署

项目包含专门的生产配置，通过 Nginx 统一对外暴露服务：

### 前置条件

- 一台 **Linux 云服务器**（推荐 2C4G，Ubuntu 22.04 或 Debian 12）
- 一个**域名**（如需 HTTPS）

### 快速部署（推荐）

`ash
# 1. SSH 到服务器后，克隆项目
git clone <your-repo-url> /opt/beijing-news-pipeline
cd /opt/beijing-news-pipeline

# 2. 一键部署（HTTP 模式）
bash scripts/deploy.sh

# 或 HTTPS 模式（自动申请 Let's Encrypt 证书）
bash scripts/deploy.sh --ssl your-domain.com

# 如需 Metabase 仪表盘
bash scripts/deploy.sh --profile metabase
`

部署后访问：

| 入口 | 地址 |
|------|------|
| 前端首页 | http://your-domain.com/ |
| API 文档 | http://your-domain.com/api/docs |
| Airflow | http://your-domain.com/airflow/ (admin / admin) |
| MinIO | http://your-domain.com:9001 (minioadmin / minioadmin123) |

### 手动部署

`ash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | bash

# 2. 启动全部服务
docker compose -f docker-compose.prod.yml up -d

# 3. 查看状态
docker compose -f docker-compose.prod.yml ps
`

### SSL 证书自动续期

`ash
# 手动续期
sudo certbot renew

# 设置定时任务自动续期（certbot 安装时默认已添加）
sudo crontab -l | grep certbot
`

### 更新服务

`ash
cd /opt/beijing-news-pipeline
git pull
docker compose -f docker-compose.prod.yml up -d --build
`

### 文件说明

| 文件 | 作用 |
|------|------|
| docker-compose.prod.yml | 生产编排（log 限制、restart 策略、内网端口绑定） |
| nginx/default.conf | Nginx 反代配置（前端 + API + Airflow） |
| scripts/deploy.sh | 一键部署脚本（含 SSL 配置） |
| .gitignore | 忽略本地缓存与凭据 |

生产版与本地版的区别：

- 所有服务端口绑定到 127.0.0.1，只通过 Nginx 80/443 对外暴露
- 固定 news-api 的数据库连接为容器内服务名 postgres（不再依赖 host.docker.internal）
- 日志限制 max-size: 10m，防止磁盘写满
- API 使用 gunicorn + uvicorn 多 worker 运行
- 前端通过 Nginx 直接托管，API 请求走 /api 路径反代
