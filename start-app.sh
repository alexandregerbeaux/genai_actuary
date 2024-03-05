#!/usr/bin/env bash

echo "Starting App"

streamlit run Chat.py --server.port 8080 --runner.magicEnabled False -- --guard_model_deployment_id "658cabe55f6e3e091897d40f" --generative_model_deployment_id "658caa9a8556f2c2176dfae7"