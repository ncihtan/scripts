#!/bin/bash -euf -o pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"

curl -sL "https://github.com/ncihtan/htan-portal/raw/master/data/htapp_release1.tsv" \
    > "htapp_release1.tsv"

curl -sL "https://github.com/ncihtan/htan-portal/raw/master/data/config-htan.yml" \
    > "config-htan.yml"

curl -sL "https://github.com/ncihtan/htan-portal/raw/master/data/image-release-1-synapse-ids.json" \
    > "image-release-1-synapse-ids.json"

python3 -m venv "venv"

source "venv/bin/activate"

python3 -m pip install --upgrade pip

python3 -m pip install -r "requirements.txt"

python3 "get_syn_data.py"

python3 "generate_manifest.py" "cds_manifest.synids.txt" \
    "cds_manifest.all.csv" "cds_manifest.nohandle.txt"

grep -e "file name" -e "s3://" "cds_manifest.all.csv" > "cds_manifest.s3.csv"
grep -e "file name" -e "gs://" "cds_manifest.all.csv" > "cds_manifest.gs.csv"
