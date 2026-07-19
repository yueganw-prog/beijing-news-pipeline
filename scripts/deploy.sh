#!/usr/bin/env bash
set -euo pipefail

# =============================================================
# Beijing News Pipeline — 一键生产部署脚本
# 目标: 在 Linux 云服务器上拉起全部服务
# 用法:
#   bash scripts/deploy.sh [--ssl your-domain.com] [--profile metabase]
# =============================================================

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
      echo "Usage: $0 [--ssl your-domain.com] [--profile metabase]"
      exit 1
      ;;
  esac
done

echo "======================================="
echo "  Beijing News Pipeline 部署"
echo "======================================="

# 1. 检查 Docker
if ! command -v docker &>/dev/null; then
  echo "[..] 安装 Docker..."
  curl -fsSL https://get.docker.com | bash
  sudo usermod -aG docker "$USER"
  echo "[OK] Docker 已安装. 请重新登录后再运行此脚本以使用 docker 命令."
  exit 0
fi
echo "[OK] Docker $(docker --version)"

if ! command -v docker compose &>/dev/null; then
  echo "[..] 安装 Docker Compose plugin..."
  sudo apt-get update && sudo apt-get install -y docker-compose-plugin
fi
echo "[OK] Docker Compose $(docker compose version)"

# 2. 创建 .env（如果不存在）
if [ ! -f .env ]; then
  echo "[..] 创建 .env 文件（默认值）..."
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
  echo "[OK] .env 已创建"
fi

# 3. 拉取镜像 & 启动服务
echo "[..] 拉取镜像 & 启动服务..."
docker compose -f docker-compose.prod.yml pull

if [ "$USE_SSL" = true ] && [ -n "$DOMAIN" ]; then
  echo "[..] 配置 SSL 证书 ($DOMAIN)..."

  # 临时启动 Nginx（HTTP 模式）用于 certbot 验证
  docker compose -f docker-compose.prod.yml up -d nginx
  sleep 3

  # 安装并运行 certbot
  if ! command -v certbot &>/dev/null; then
    sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx
  fi

  sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" --redirect || {
    echo "[!] certbot 失败，继续 HTTP 模式..."
  }

  # 复制证书到 nginx ssl 数据卷
  if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    docker run --rm -v nginx_ssl:/ssl -v "/etc/letsencrypt/live/$DOMAIN:/certs:ro" \
      alpine sh -c "cp /certs/fullchain.pem /ssl/ && cp /certs/privkey.pem /ssl/"

    # 重启 Nginx 加载 SSL
    docker compose -f docker-compose.prod.yml restart nginx
    echo "[OK] SSL 已配置"
  fi
fi

echo "[..] 启动所有服务..."
docker compose -f docker-compose.prod.yml up -d $PROFILES

# 4. 等待服务就绪
echo "[..] 等待服务就绪..."
echo "  - PostgreSQL..."
for i in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml exec postgres pg_isready -U postgres &>/dev/null; then
    echo "  [OK]"
    break
  fi
  sleep 2
done

echo "  - News API..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/health &>/dev/null; then
    echo "  [OK]"
    break
  fi
  sleep 2
done

# 5. 输出状态
echo ""
echo "======================================="
echo "  部署完成"
echo "======================================="
echo "  Frontend : http://localhost/"
echo "  API      : http://localhost:8000/docs"
echo "  Airflow  : http://localhost:8080 (admin / admin)"
echo "  MinIO    : http://localhost:9001 (minioadmin / minioadmin123)"
echo "======================================="
docker compose -f docker-compose.prod.yml ps
echo ""
echo "查看日志: docker compose -f docker-compose.prod.yml logs -f [service]"
echo "停止:     docker compose -f docker-compose.prod.yml down"
echo "更新:     git pull && docker compose -f docker-compose.prod.yml up -d --build"
echo "SSL 续期: sudo certbot renew"
