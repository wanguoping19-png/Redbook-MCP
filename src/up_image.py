import requests
from setting import QR_IMAGES
def upload_image(file_name):
    url = "https://imgurl.org/api/v3/upload"  # 将“基础域名”替换为实际的域名
    headers = {
        'Authorization': 'Bearer sk-x8kNKtvk9A4CMoGTo6w5irdNmQT2Bgjk44ZSXWEQJyfAWLsx8Niyv6pcCgK9h',  # 替换为实际的token
    }
    file_path = f'{QR_IMAGES}/{file_name}'  # 替换为实际文件路径

    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
    # 输出响应内容和状态码
    print(response.status_code)
    print(response.text)
    return response.json()