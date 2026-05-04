#!/bin/bash
set -e

echo "========================================="
echo "  AI News App - 部署脚本"
echo "========================================="

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    echo "  Ubuntu: sudo apt install docker.io docker-compose"
    echo "  Mac:    brew install --cask docker"
    exit 1
fi

if docker info &> /dev/null; then
    SUDO=""
    echo "Docker 权限: 正常"
elif sudo docker info &> /dev/null 2>&1; then
    SUDO="sudo"
    echo "Docker 权限: 需要 sudo（当前用户不在 docker 组）"
    echo "提示: 运行 'sudo usermod -aG docker \$USER' 然后重新登录可免 sudo"
else
    echo "错误: Docker 服务未运行，请先启动 Docker"
    echo "  sudo systemctl start docker"
    exit 1
fi

if ! $SUDO docker-compose version &> /dev/null 2>&1 && ! $SUDO docker compose version &> /dev/null 2>&1; then
    echo "错误: Docker Compose 未安装"
    exit 1
fi

COMPOSE_CMD="docker-compose"
if ! $SUDO docker-compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
fi

if [ ! -f backend/.env ]; then
    echo "创建 .env 配置文件..."
    cp backend/.env.example backend/.env
    echo "请编辑 backend/.env 修改 SECRET_KEY 和 LLM 配置"
fi

echo ""
echo "1. 构建并启动后端服务..."
$SUDO $COMPOSE_CMD up -d --build

echo ""
echo "2. 等待服务启动..."
sleep 5

echo ""
echo "3. 检查服务状态..."
$SUDO $COMPOSE_CMD ps

echo ""
echo "========================================="
echo "  后端服务已启动！"
echo "========================================="
echo ""
echo "  API 地址:  http://localhost:8000"
echo "  API 文档:  http://localhost:8000/docs"
echo "  健康检查:  http://localhost:8000/health"
echo ""
echo "  停止服务:  $SUDO $COMPOSE_CMD down"
echo "  查看日志:  $SUDO $COMPOSE_CMD logs -f backend"
echo ""
