#!/usr/bin/env bash
set -euo pipefail

# =============================================================
# Beijing News Pipeline — 阿里云 ECS 一键部署脚本
#
# 适用: 阿里云 Ubuntu 22.04 / 24.04
# 用法:
#   bash scripts/deploy-aliyun.sh                      # HTTP 模式
#   bash scripts/deploy-aliyun.sh --ssl your-domain.com  # HTTPS + 自动证书
#   bash scripts/deploy-aliyun.sh --ssl your-domain.com --profile metabase
# =============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[..]${NC} $*"; }
err()  { echo -e "${RED}[!!]${NC} $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

USE_SSL=false
DOMAIN=""
PROFILES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ssl)
      USE_SSL=true
      DOMAIN="$2"
      shift 2
      ;;
    --profile)
      PROFILES="--profile $2"
      shift 2
      ;;
    *)
      echo "用法: $0 [--ssl your-domain.com] [--profile metabase]"
      exit 1
      ;;
  esac
done

echo ""
echo "========================================="
echo "  Beijing News Pipeline — 阿里云部署"
echo "========================================="
echo ""

# ===========================================
# 1. 检查/安装 Docker（使用阿里云镜像源）
# ===========================================
if ! command -v docker &>/dev/null; then
  warn "安装 Docker..."

  # 用阿里云的 Docker 安装源（国内速度飞快）
  curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun 2>/dev/null || {
    err "Docker 安装失败，手动安装: curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun"
    exit 1
  }

  # 配置阿里云 Docker 镜像加速器
  warn "配置阿里云 Docker 镜像加速器..."
  mkdir -p /etc/docker
  cat > /etc/docker/daemon.json << 'DAEMON'
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://dockerhub.icu"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
DAEMON

  systemctl enable docker
  systemctl restart docker

  # 把当前用户加入 docker 组
  if [ "$(whoami)" != "root" ]; then
    usermod -aG docker "$(whoami)"
  fi

  log "Docker 已安装"
else
  log "Docker $(docker --version 2>/dev/null)"
fi

if ! docker compose version &>/dev/null 2>&1; then
  warn "安装 Docker Compose 插件..."
  apt-get update -qq && apt-get install -y -qq docker-compose-plugin 2>/dev/null || {
    err "Docker Compose 安装失败"
    exit 1
  }
fi
log "Docker Compose $(docker compose version 2>/dev/null)"

# ===========================================
# 2. 检查/安装 Node.js（构建前端用）
# ===========================================
if ! command -v node &>/dev/null; then
  warn "安装 Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
  log "Node.js $(node --version) 已安装"
else
  log "Node.js $(node --version)"
fi

if ! command -v npm &>/dev/null; then
  err "npm 未安装，请手动安装"
  exit 1
fi

# ===========================================
# 3. 创建 .env（找不到则用默认值）
# ===========================================
if [ ! -f .env ]; then
  warn ".env 不存在，使用默认配置创建"
  cat > .env << 'ENVEOF'
# Beijing News Pipeline - Production Environment
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ENDPOINT=http://minio:9000
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/airflow
AIRFLOW_CONN_NEWS_POSTGRES=postgres://postgres:postgres@postgres:5432/airflow
AIRFLOW_CONN_NEWS_MINIO=aws://minioadmin:minioadmin123@minio:9000
TZ=Asia/Shanghai
ENVEOF
  warn "===================================================="
  warn "  警告: 正在使用默认密码！"
  warn "  部署完成后请修改 .env 和 docker-compose.prod.yml 中的密码"
  warn "===================================================="
else
  log ".env 已存在，跳过创建"
fi

# ===========================================
# 4. 构建前端
# ===========================================
warn "构建前端..."
cd "$SCRIPT_DIR/frontend"
npm ci --omit=dev 2>/dev/null || npm install
npm run build
cd "$SCRIPT_DIR"
log "前端构建完成 ($(du -sh frontend/dist | cut -f1))"

# ===========================================
# 5. 登录阿里云 Docker Registry（提升镜像拉取成功率）
# ===========================================
# 拉取基础镜像（如果还没拉过的话）
warn "拉取 Docker 镜像..."
docker compose -f docker-compose.prod.yml pull 2>&1 || {
  warn "部分镜像拉取失败，稍后启动时会自动重试"
}

# ===========================================
# 6. 启动所有服务（先不启 Nginx，让 SSL 配置有机会插入）
# ===========================================
if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
  warn "先启动后端服务（Nginx 稍后启动）..."
  docker compose -f docker-compose.prod.yml up -d postgres minio airflow-webserver airflow-scheduler news-api

  # 启动临时 Nginx（HTTP 模式，供 certbot 验证）
  warn "临时启动 Nginx（HTTP 验证）..."
  docker compose -f docker-compose.prod.yml up -d nginx
  sleep 5

  # 安装 certbot
  if ! command -v certbot &>/dev/null; then
    warn "安装 certbot..."
    apt-get update -qq && apt-get install -y -qq certbot 2>/dev/null || {
      err "certbot 安装失败，继续 HTTP 模式"
    }
  fi

  # 运行 certbot
  if command -v certbot &>/dev/null; then
    warn "申请 SSL 证书 ($DOMAIN)..."
    certbot certonly --webroot \
      -w /usr/share/nginx/html \
      -d "$DOMAIN" \
      --non-interactive --agree-tos \
      --email "admin@$DOMAIN" \
      --keep-until-expiring 2>&1 || {
      err "证书申请失败，检查: 1) 域名 DNS 已解析到本机 2) 80 端口外网可达"
      err "继续 HTTP 模式..."
      USE_SSL=false
    }
  fi

  # 如果证书申请成功，配置 Nginx SSL
  if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    warn "配置 Nginx SSL..."

    # 拷贝证书到 nginx_ssl 卷
    docker run --rm \
      -v nginx_ssl:/ssl \
      -v "/etc/letsencrypt/live/$DOMAIN:/certs:ro" \
      alpine sh -c "cp /certs/fullchain.pem /ssl/ && cp /certs/privkey.pem /ssl/" 2>/dev/null || true

    # 生成 SSL Nginx 配置
    cat > nginx/default-ssl.conf << NGINXSSL
# HTTPS server（由 certbot 自动生成）
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;
    gzip_min_length 256;
    gzip_vary on;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        rewrite ^/api/(.*) /\$1 break;
        proxy_pass http://news-api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }

    location /airflow/ {
        rewrite ^/airflow/(.*) /\$1 break;
        proxy_pass http://airflow-webserver:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}
NGINXSSL

    # 重新加载 Nginx
    docker compose -f docker-compose.prod.yml restart nginx
    log "SSL 配置完成"
  fi
else
  # 无 SSL，直接全部启动
  warn "启动所有服务..."
  docker compose -f docker-compose.prod.yml up -d $PROFILES
fi

# 如果启动过程中有未启动的服务，再补启动一次
if [ "$(docker compose -f docker-compose.prod.yml ps -q --status paused --status exited 2>/dev/null | wc -l)" -gt 0 ]; then
  warn "有服务未就绪，等待重试..."
  sleep 5
  docker compose -f docker-compose.prod.yml up -d $PROFILES 2>/dev/null || true
fi

# ===========================================
# 7. 等待所有服务就绪
# ===========================================
warn "等待服务就绪..."

# PostgreSQL
echo -n "  PostgreSQL ... "
for i in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml exec -T postgres pg_isready -U postgres &>/dev/null; then
    echo "OK"
    break
  fi
  if [ "$i" -eq 30 ]; then echo "TIMEOUT"; fi
  sleep 2
done

# News API
echo -n "  News API ... "
for i in $(seq 1 20); do
  if curl -sf http://localhost:8000/health &>/dev/null; then
    echo "OK"
    break
  fi
  if [ "$i" -eq 20 ]; then echo "TIMEOUT（查看日志: docker compose logs news-api）"; fi
  sleep 3
done

# MinIO
echo -n "  MinIO ... "
for i in $(seq 1 15); do
  if curl -sf http://localhost:9000/minio/health/live &>/dev/null; then
    echo "OK"
    break
  fi
  if [ "$i" -eq 15 ]; then echo "TIMEOUT"; fi
  sleep 2
done

# Airflow
echo -n "  Airflow ... "
for i in $(seq 1 20); do
  if curl -sf http://localhost:8080/health &>/dev/null; then
    echo "OK"
    break
  fi
  if [ "$i" -eq 20 ]; then echo "TIMEOUT（查看日志: docker compose logs airflow-webserver）"; fi
  sleep 3
done

# ===========================================
# 8. 输出结果
# ===========================================
echo ""
echo "========================================="
echo "  部署完成"
echo "========================================="
echo ""

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "服务器IP")

if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
  PROTO="https"
  HOST="$DOMAIN"
else
  PROTO="http"
  HOST="$PUBLIC_IP"
fi

echo "  首页:    ${PROTO}://${HOST}/"
echo "  API 文档: ${PROTO}://${HOST}/api/docs"
echo "  Airflow:  ${PROTO}://${HOST}/airflow/  (用户名: admin, 密码: admin)"
echo "  MinIO:    http://${PUBLIC_IP}:9001  (minioadmin / minioadmin123)"
echo ""
echo "========================================="
echo "  常用命令"
echo "========================================="
echo "  查看日志:     docker compose -f docker-compose.prod.yml logs -f [服务名]"
echo "  停止:         docker compose -f docker-compose.prod.yml down"
echo "  重启单个服务: docker compose -f docker-compose.prod.yml restart news-api"
echo "  更新前端:     cd frontend && npm run build"
echo "  更新全部:     git pull && docker compose -f docker-compose.prod.yml up -d --build"
echo "  SSL 续期:     certbot renew --quiet"
echo ""

docker compose -f docker-compose.prod.yml ps
