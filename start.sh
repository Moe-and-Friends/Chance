#!/bin/bash

docker run -d \
    --name 'Nana_Chance' \
    -v "$(pwd)/config/:/nana/config" \
    -v "$(pwd)/data/:/nana/data" \
    --log-opt max-size=10m \
    --log-opt max-file=2 \
    nana-chance

docker logs -f "Nana_Chance"
