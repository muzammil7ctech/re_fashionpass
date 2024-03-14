#!/bin/bash

# Run individual Python scripts

echo "$(date +"%Y-%m-%d %T") run the pythons main file"
python3 main.py 
echo "$(date +"%Y-%m-%d %T")run the pythons training scripts"
python3 train.py 
echo "$(date +"%Y-%m-%d %T")run the pythons validation scripts"
python3 val.py 
echo "$(date +"%Y-%m-%d %T")run the pythons uploading scripts"
python3 upload.py 
