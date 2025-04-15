import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
import numpy as np
from datasets import Dataset as HFDataset
from sklearn.model_selection import train_test_split

# 1️⃣  加载数据集
with open("labeled_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2️⃣  预处理数据
texts = [item["code"] for item in data]
labels = [item["label"] for item in data]

train_texts, val_texts, train_labels, val_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# 3️⃣  加载 CodeBERT tokenizer
tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")

def tokenize_function(texts):
    return tokenizer(texts, padding="max_length", truncation=True, max_length=256)  # 降低 max_length 以加速训练

train_encodings = tokenize_function(train_texts)
val_encodings = tokenize_function(val_texts)

# 4️⃣  创建 PyTorch Dataset
class CodeDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

train_dataset = CodeDataset(train_encodings, train_labels)
val_dataset = CodeDataset(val_encodings, val_labels)

# 5️⃣  加载 CodeBERT 模型
model = RobertaForSequenceClassification.from_pretrained("microsoft/codebert-base", num_labels=2)

# 6️⃣  训练参数
training_args = TrainingArguments(
    output_dir="./codebert_model",
    evaluation_strategy="epoch",  # 每个 epoch 后评估
    save_strategy="epoch",       # 每个 epoch 后保存模型
    per_device_train_batch_size=4,  # 降低 batch size 以减少内存使用
    per_device_eval_batch_size=4,   # 降低 batch size
    num_train_epochs=3,            # 降低 epoch 数量
    logging_dir="./logs",          # 日志保存目录
    logging_steps=500,             # 减少日志记录频率
    save_steps=1000,               # 每 1000 步保存一次模型
    load_best_model_at_end=True,   # 加载最佳模型
    fp16=True,                     # 启用混合精度训练，加速并节省显存（适用于 GPU）
    gradient_accumulation_steps=2  # 增加梯度累积，进一步减少显存消耗
)

# 7️⃣  使用 Trainer 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer
)

trainer.train()

# 8️⃣  保存模型
model.save_pretrained("fine_tuned_codebert")
tokenizer.save_pretrained("fine_tuned_codebert")
print("🎉 训练完成，模型已保存到 fine_tuned_codebert/")
