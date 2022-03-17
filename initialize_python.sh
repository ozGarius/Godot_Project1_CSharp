#! /bin/sh
python3 -m venv venv
sed -i 's/\r$//' venv/bin/activate
source ./venv/bin/activate
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
