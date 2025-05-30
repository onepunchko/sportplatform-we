import requests
import json

# 测试API基本URL
BASE_URL = 'http://127.0.0.1:5000'

def test_community_users_api():
    """测试社区用户API"""
    url = f"{BASE_URL}/community/users"
    
    # 模拟请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, json={})
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试社区用户API...")
    if test_community_users_api():
        print("API测试成功!")
    else:
        print("API测试失败!") 