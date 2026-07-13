#!/bin/bash
set -e

# Very basic health check (since curl is installed, check if the server answers)
curl -f http://localhost:8000/health/ || exit 1
