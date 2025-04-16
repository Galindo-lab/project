#!/bin/bash
BUILD=false

# Verificar si se pasó el flag --build
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --build) BUILD=true ;;
        *) echo "Opción desconocida: $1"; exit 1 ;;
    esac
    shift
done

if [ "$BUILD" = true ]; then
    sudo docker compose -f docker-compose.yml up --build
else
    sudo docker compose -f docker-compose.yml up
fi