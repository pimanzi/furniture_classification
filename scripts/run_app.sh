#!/bin/bash

echo " Starting Furniture Classification System..."

cd "$(dirname "$0")/.."

source .venv/bin/activate

streamlit run app.py --server.port 8515 --server.address 0.0.0.0
