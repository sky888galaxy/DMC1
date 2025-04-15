from transformers import AutoModel, AutoTokenizer

# 选择 CodeBERT 预训练模型
model_name = "microsoft/codebert-base"

# 加载 Tokenizer 和 预训练模型（自动下载）
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

print("✅ CodeBERT 预训练模型下载完成并加载成功！")
