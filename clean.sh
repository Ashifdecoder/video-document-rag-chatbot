#!/bin/bash

echo "🧹 Cleaning up containers and volumes"
echo ""

docker-compose down -v

echo "✅ Cleanup complete"
