#!/bin/bash
set -e
echo "Документоскоп: on-prem установка"
docker-compose -f docker/docker-compose-onprem.yml up -d --build
