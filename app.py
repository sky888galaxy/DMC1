from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

import sys
import os
# 获取当前文件路径，并将 dynamic_analysis.py 的路径加入到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "website-risk-analyzer"))
from dynamic_analysis import analyze_dynamic_behavior

app = FastAPI()

# 添加 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，或者你可以指定允许的 URL 如 ["http://127.0.0.1:8000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

# 定义 URLRequest 数据模型
class URLRequest(BaseModel):
    url: str  # 确保请求体中包含 `url` 字段

# 加载模型和 tokenizer
tokenizer = RobertaTokenizer.from_pretrained("fine_tuned_codebert")
model = RobertaForSequenceClassification.from_pretrained("fine_tuned_codebert")

# 网站源码爬取
def fetch_website_code(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果状态码不是 200，抛出异常
        print("网页源码的前 500 字符：", response.text[:500])  # 打印前 500 个字符来查看
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"爬取网站 {url} 时发生错误: {e}")
        return None

# 提取 JavaScript 代码
def extract_js_code(webpage_code):
    script_tags = re.findall(r'<script.*?>(.*?)</script>', webpage_code, re.DOTALL)
    return script_tags

# 信息泄露检测
def detect_sensitive_data(webpage_code):
    sensitive_patterns = [
        r'api_key\s*=\s*["\']?[A-Za-z0-9]{32}["\']?',  # 常见的 API 密钥模式
        r'password\s*=\s*["\']?[A-Za-z0-9]{6,}["\']?'  # 常见的密码字段
    ]
    leaks = []
    for pattern in sensitive_patterns:
        if re.search(pattern, webpage_code):
            leaks.append(pattern)
    return leaks

# 漏洞检测函数（简单示例）
def detect_vulnerabilities(webpage_code):
    vulnerabilities = []
    # 检查 SQL 注入
    if "select * from" in webpage_code or "union select" in webpage_code:
        vulnerabilities.append("可能存在 SQL 注入漏洞")
    # 检查 XSS 漏洞
    if "<script>" in webpage_code or "eval(" in webpage_code:
        vulnerabilities.append("可能存在 XSS 漏洞")
    return vulnerabilities

# 预测恶意代码
def predict_code(model, tokenizer, code):
    inputs = tokenizer(code, return_tensors="pt", padding=True, truncation=True, max_length=256)
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    return "Malicious" if prediction == 1 else "Normal"

@app.post("/predict")
async def predict(request: URLRequest):
    print(f"收到的 URL 请求: {request.url}")

    # 爬取网站源码
    webpage_code = fetch_website_code(request.url)
    if not webpage_code:
        raise HTTPException(status_code=400, detail="无法爬取该网站")

    # 提取 JS 代码
    js_code = extract_js_code(webpage_code)
    if not js_code:
        return {"message": "未发现 JavaScript 代码"}

    # 信息泄露检测
    leaks = detect_sensitive_data(webpage_code)
    leaks_detected = len(leaks) > 0

    # 漏洞检测
    vulnerabilities = detect_vulnerabilities(webpage_code)

    # 动态分析
    try:
        dynamic_analysis_result = analyze_dynamic_behavior(request.url)
    except Exception as e:
        dynamic_analysis_result = {"error": str(e)}

    # 存储所有预测结果
    predictions = []

    # 遍历所有提取到的 JS 代码
    for index, code in enumerate(js_code):
        result = predict_code(model, tokenizer, code)  # 对每一段 JS 代码进行分析
        prediction_result = {"prediction": result}  # 只返回 prediction 字段

        # 如果判断为恶意代码，添加 malicious_code 字段
        if result == "Malicious":
            prediction_result["malicious_code"] = code

        predictions.append(prediction_result)

        # 可以在这里加入日志，以便调试：
        print(f"JS 代码段 {index + 1} 预测结果: {result}")

    # 返回最终的检测结果和信息泄露情况
    return {
        "predictions": predictions,
        "leaks_detected": leaks_detected,
        "leaks": leaks,
        "vulnerabilities": vulnerabilities,  # 返回漏洞信息
        "dynamic_analysis": dynamic_analysis_result,  # 返回动态分析结果
        "message": "检测完成"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
