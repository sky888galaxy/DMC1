import os

# 原始数据 & 清理后数据目录
RAW_DIR = "raw_samples"
CLEAN_DIR = "clean_samples"

# 代码文件扩展名
CODE_EXTENSIONS = {".js", ".php", ".py", ".java", ".c"}

# 确保清理后的目录存在
os.makedirs(CLEAN_DIR, exist_ok=True)

def clean_code(file_path, output_filename):
    """清理代码：去除空行和注释"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//") or line.startswith("/*"):
                continue
            cleaned_lines.append(line)

        if cleaned_lines:
            new_path = os.path.join(CLEAN_DIR, output_filename)
            with open(new_path, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned_lines))
            print(f"✅ 清理完成: {new_path}")
            return True
        else:
            print(f"⚠️ 跳过空文件: {file_path}")
            return False
    except Exception as e:
        print(f"❌ 处理失败: {file_path}，错误: {e}")
        return False

# 遍历 raw_samples 目录的所有子文件夹
for root, _, files in os.walk(RAW_DIR):
    for file in files:
        file_path = os.path.join(root, file)

        # 过滤出符合扩展名的代码文件
        if CODE_EXTENSIONS and not any(file.endswith(ext) for ext in CODE_EXTENSIONS):
            print(f"🚫 跳过不匹配的文件: {file}")
            continue

        # 生成唯一文件名（避免不同语言的相同文件名冲突）
        relative_path = os.path.relpath(file_path, RAW_DIR).replace("/", "_").replace("\\", "_")
        clean_code(file_path, relative_path)

print("🎉 数据清理完成！")
