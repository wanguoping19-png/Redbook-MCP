import json
def enable_xhr_interception(driver):
    """启用 CDP 网络监听，并设置缓冲区大小以支持 response body"""
    driver.execute_cdp_cmd('Network.enable', {
        'maxTotalBufferSize': 100 * 1024 * 1024,
        'maxResourceBufferSize': 10 * 1024 * 1024,
        'maxPostDataSize': 10 * 1024 * 1024
    })


def get_xhr_logs_as_dict(driver):
    """
    获取自上次调用以来的所有 XHR/Fetch 请求日志，并组织成字典。
    返回格式：
    {
        "https://api.example.com/data": {
            "request": {
                "method": "GET",
                "headers": { ... },
                "postData": "..."  # 如果有
            },
            "response": {
                "status": 200,
                "headers": { ... },
                "body": "{...}"  # str 或 base64（如为二进制）
            }
        },
        ...
    }
    """
    raw_logs = driver.get_log("performance")
    xhr_data = {}

    # 第一步：收集所有 request 和 response 的事件，按 requestId 关联
    request_map = {}
    response_map = {}
    body_map = {}

    for entry in raw_logs:
        try:
            message = json.loads(entry["message"])["message"]
            method = message["method"]

            if method == "Network.requestWillBeSent":
                params = message["params"]
                # 判断是否为 XHR 或 Fetch
                if params.get("type") == "XHR" or params.get("initiator", {}).get("type") == "script":
                    request_id = params["requestId"]
                    request_map[request_id] = {
                        "url": params["request"]["url"],
                        "method": params["request"]["method"],
                        "headers": params["request"].get("headers", {}),
                        "postData": params["request"].get("postData", None)
                    }

            elif method == "Network.responseReceived":
                params = message["params"]
                request_id = params["requestId"]
                if request_id in request_map:  # 只处理我们关心的 XHR
                    response_map[request_id] = {
                        "status": params["response"]["status"],
                        "headers": params["response"].get("headers", {})
                    }

            elif method == "Network.loadingFinished":
                # 尝试获取响应体（必须在 loadingFinished 之后）
                request_id = message["params"]["requestId"]
                if request_id in request_map:
                    try:
                        body_info = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                        body_map[request_id] = body_info["body"] if not body_info["base64Encoded"] else body_info["body"]
                    except Exception as e:
                        # 某些响应（如重定向）可能无法获取 body
                        body_map[request_id] = "[Body not available: " + str(e) + "]"

        except Exception as e:
            # 日志解析出错，跳过
            continue

    # 第二步：合并 request + response + body
    for rid in request_map:
        req = request_map[rid]
        url = req["url"]
        resp = response_map.get(rid, {})
        body = body_map.get(rid, "[No response body captured]")

        xhr_data[url] = {
            "request": {
                "method": req["method"],
                "headers": req["headers"],
                "postData": req["postData"]
            },
            "response": {
                "status": resp.get("status", None),
                "headers": resp.get("headers", {}),
                "body": body
            }
        }

    return xhr_data