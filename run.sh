#!/bin/bash

# 设置要执行的 Python 脚本路径和参数
script_path="video_autocut.py"
# args="600 '积木素材' 30"

# 使用 GNU Parallel 执行 50 次脚本，最多同时执行 8 个任务
seq 1 20 | parallel -j 4 "python $script_path $args"
