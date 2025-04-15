import os
import json
import re

# 目录设置
CLEAN_DIR = "clean_samples"
LABELLED_FILE = "labeled_dataset.json"

# 恶意代码关键字（你可以增加更多）
MALICIOUS_PATTERNS = {
    "XSS": [r"<script>.*?</script>", r"document\.cookie", r"onerror\s*="],
    "SQLi": [r"SELECT .*? FROM", r"UNION SELECT", r"INSERT INTO .*? VALUES"],
    "RCE": [r"os\.system\(", r"subprocess\.Popen\(", r"eval\("],
    "Backdoor": [r"base64_decode\(", r"exec\(", r"shell_exec\("],
    "CSRF": [r"fetch\(", r"XMLHttpRequest\("],
}

def check_malicious(code):
    """检测代码是否包含恶意模式"""
    labels = []
    for category, patterns in MALICIOUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                labels.append(category)
                break  # 发现一个就停止，避免重复

    return labels

labeled_data = []

for file in os.listdir(CLEAN_DIR):
    file_path = os.path.join(CLEAN_DIR, file)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        labels = check_malicious(code)
        labeled_data.append({
            "filename": file,
            "code": code,
            "label": 1 if labels else 0,
            "malicious_types": labels
        })

        print(f"✅ 标注完成: {file} - {'恶意' if labels else '安全'} ({labels})")

    except Exception as e:
        print(f"❌ 处理失败: {file}，错误: {e}")

# 保存为 JSON 格式
with open(LABELLED_FILE, "w", encoding="utf-8") as f:
    json.dump(labeled_data, f, indent=4, ensure_ascii=False)

print(f"🎉 数据标注完成！已保存到 {LABELLED_FILE}，共 {len(labeled_data)} 个样本")
