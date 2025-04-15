import requests
from bs4 import BeautifulSoup
import re
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

# 1️⃣ 加载训练好的 CodeBERT 模型和 Tokenizer
tokenizer = RobertaTokenizer.from_pretrained("fine_tuned_codebert")
model = RobertaForSequenceClassification.from_pretrained("fine_tuned_codebert")


# 2️⃣ 爬取网站源码
def fetch_website_code(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


# 3️⃣ 提取潜在的恶意代码（JavaScript）
def extract_js_code(webpage_code):
    # 匹配网页中的 <script> 标签并提取内容
    script_tags = re.findall(r'<script.*?>(.*?)</script>', webpage_code, re.DOTALL)
    return script_tags


# 4️⃣ 分析代码并进行恶意代码预测
def predict_code(model, tokenizer, code):
    inputs = tokenizer(code, return_tensors="pt", padding=True, truncation=True, max_length=256)
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    return "Malicious" if prediction == 1 else "Normal"


# 5️⃣ 自动分析网站
def analyze_website(url):
    print(f"正在分析 {url} ...")

    # 获取网站源码
    webpage_code = fetch_website_code(url)
    if not webpage_code:
        return {"error": "无法爬取该网站"}

    # 提取 JavaScript 代码
    js_code = extract_js_code(webpage_code)
    if not js_code:
        return {"message": "未发现 JavaScript 代码"}

    # 使用 CodeBERT 进行恶意代码分析
    result = predict_code(model, tokenizer, js_code[0])  # 这里只分析第一个 <script> 标签中的代码
    return {"prediction": result, "malicious_code": js_code[0]}


# 示例：分析一个网站
url = "https://example.com"
result = analyze_website(url)
print(result)
