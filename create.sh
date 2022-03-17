#! /bin/sh
sed -i 's/\r$//' activate
source .venv/Scripts/activate
python3 create.py
