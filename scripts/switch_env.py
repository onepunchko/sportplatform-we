#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境切换脚本
用于在开发和生产环境之间切换
"""

import os
import sys
import shutil
import argparse

def switch_env(env):
    """
    切换环境配置
    
    Args:
        env: 目标环境，development或production
    """
    if env not in ['development', 'production']:
        print(f"错误：不支持的环境 '{env}'。请使用 'development' 或 'production'")
        return False
    
    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 环境配置文件路径
    env_file = os.path.join(root_dir, '.env')
    env_template = os.path.join(root_dir, f'.env.{env}')
    
    # 检查目标环境配置文件是否存在
    if not os.path.exists(env_template):
        print(f"错误：环境配置文件 '.env.{env}' 不存在")
        return False
    
    # 备份当前环境配置（如果存在）
    if os.path.exists(env_file):
        # 读取当前环境
        current_env = None
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('FLASK_ENV='):
                    current_env = line.split('=')[1].strip()
                    break
        
        if current_env:
            backup_file = os.path.join(root_dir, f'.env.{current_env}')
            shutil.copy2(env_file, backup_file)
            print(f"已备份当前环境配置到 '.env.{current_env}'")
    
    # 复制目标环境配置
    shutil.copy2(env_template, env_file)
    print(f"已切换到{env}环境")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='环境配置切换工具')
    parser.add_argument('env', choices=['development', 'production'], help='目标环境')
    
    args = parser.parse_args()
    switch_env(args.env)

if __name__ == '__main__':
    main() 