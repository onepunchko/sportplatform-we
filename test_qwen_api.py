import os
from openai import OpenAI
import json

# 配置API密钥和基础URL
api_key = "sk-93132de1224a4d4689d535c19efd47a6"  # 使用config/env.js中的API密钥
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

try:
    # 创建客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model="qwen3-8b",  # 模型名称
        messages=[
            {'role': 'system', 'content': '你是一个专业的运动教练。'},
            {'role': 'user', 'content': '你是谁？'}
        ],
        temperature=0.7,
        top_p=0.8,
        max_tokens=1500,
        stream=True  # 添加流模式参数
    )
    
    # 处理流式响应
    full_content = ""
    for chunk in completion:
        if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
            content_chunk = chunk.choices[0].delta.content
            full_content += content_chunk
            print(content_chunk, end="", flush=True)
    
    print("\n\n完整回复：")
    print(full_content)
    
except Exception as e:
    print(f"错误信息：{e}")
    print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code") 