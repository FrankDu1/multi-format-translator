#!/bin/bash
# Docker Compose 快捷脚本 - 自动使用 docker-compose.ghcr.yml

COMPOSE_FILE="docker-compose.ghcr.yml"

case "$1" in
    up)
        docker compose -f $COMPOSE_FILE up -d "${@:2}"
        ;;
    down)
        docker compose -f $COMPOSE_FILE down "${@:2}"
        ;;
    restart)
        docker compose -f $COMPOSE_FILE restart "${@:2}"
        ;;
    logs)
        docker compose -f $COMPOSE_FILE logs "${@:2}"
        ;;
    ps)
        docker compose -f $COMPOSE_FILE ps "${@:2}"
        ;;
    pull)
        docker compose -f $COMPOSE_FILE pull "${@:2}"
        ;;
    *)
        docker compose -f $COMPOSE_FILE "$@"
        ;;
esac
