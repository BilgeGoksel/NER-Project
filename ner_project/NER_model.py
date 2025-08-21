import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    TrainingArguments, Trainer, DataCollatorForTokenClassification,
    EarlyStoppingCallback
)
from sklearn.metrics import classification_report, f1_score
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# BERTurk modelini yükleme
model_name = "dbmdz/bert-base-turkish-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def check_data_format(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            try:
                data = json.loads(line.strip())
                print(f"Satır {i+1}:")
                print(f"  Text: {data['text'][:100]}...")
                print(f"  Entities: {len(data['entities'])} adet")
                for entity in data['entities'][:3]:
                    print(f"    - {entity}")
                print()
            except Exception as e:
                print(f"Hata satır {i+1}: {e}")

def simple_test():
    text = "Trendyol şirketi 15 Haziran'da İstanbul'da açılış yaptı."

    # Manuel olarak entity'leri tanımlama (örnek)
    entities = [
        {"start": 0, "end": 8, "label": "sirket"},
        {"start": 17, "end": 28, "label": "tarih"},
        {"start": 31, "end": 39, "label": "adres"}
    ]

    print("Test metni:", text)
    print("Test entities:", entities)

    # Maskeleme testi
    masked = text
    for entity in sorted(entities, key=lambda x: x['start'], reverse=True):
        mask = "*" * (entity['end'] - entity['start'])
        masked = masked[:entity['start']] + mask + masked[entity['end']:]

    print("Maskelenmiş:", masked)


if __name__ == "__main__":
    print("=== VERİ FORMATI KONTROLÜ ===")
    check_data_format("C:/Users/HP/PycharmProjects/Havelsan/.venv/data.jsonl")

    print("\n=== BASİT TEST ===")
    simple_test()

from collections import Counter
def analyze_data(file_path):
    entity_counts = Counter()
    text_lengths = []
    total_entities = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                text_lengths.append(len(data['text']))
                entities = data.get('entities', [])
                total_entities += len(entities)

                for entity in entities:
                    entity_counts[entity['label']] += 1

            except Exception as e:
                print(f"Hata satır {line_num}: {e}")

    print(f"Toplam satır: {line_num}")
    print(f"Toplam entity: {total_entities}")
    print(f"Ortalama metin uzunluğu: {sum(text_lengths)/len(text_lengths):.0f}")
    print(f"En uzun metin: {max(text_lengths)}")

    print("\nEntity türleri ve sayıları:")
    for label, count in entity_counts.most_common():
        print(f"  {label}: {count}")

    return entity_counts

def split_data(input_file, train_file, test_file, train_ratio=0.8):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Filter out empty lines
    lines = [line.strip() for line in lines if line.strip()]

    import random
    random.shuffle(lines)

    split_point = int(len(lines) * train_ratio)

    with open(train_file, 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in lines[:split_point])

    with open(test_file, 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in lines[split_point:])


    print(f"Eğitim seti: {split_point} örnek")
    print(f"Test seti: {len(lines) - split_point} örnek")

if __name__ == "__main__":
    print("=== VERİ ANALİZİ ===")
    analyze_data(".venv/data.jsonl")

    print("\n=== VERİ BÖLME ===")
    split_data(".venv/data.jsonl", "train.jsonl", "test.jsonl")


import os
print("Aktif çalışma dizini:", os.getcwd())

class SimpleNERDataset(Dataset):
    def __init__(self, file_path, tokenizer, label_to_id, max_length=256):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.label_to_id = label_to_id
        self.id_to_label = {v: k for k, v in self.label_to_id.items()}

        # Veri yükleme
        self.data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line:
                    self.data.append(json.loads(line))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item['text']
        entities = item['entities']

        # Tokenize et
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt',
            return_offsets_mapping=True
        )
        [0,4 ,7 ,22 ,15]

        labels = self.create_labels(entities, encoding['offset_mapping'][0])
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(labels, dtype=torch.long)
        }

    def create_labels(self, entities, offset_mapping):
        labels = [self.label_to_id['O']] * len(offset_mapping)

        for ent in entities:
            start, end = ent['start'], ent['end']
            label_type = ent['label']

            matched = []
            for i, (token_start, token_end) in enumerate(offset_mapping):
                if token_start == 0 and token_end == 0:
                    continue
                if token_start < end and token_end > start:
                    matched.append(i)

            if matched:
                labels[matched[0]] = self.label_to_id.get(f"B-{label_type}", self.label_to_id['O'])
                for i in matched[1:]:
                    labels[i] = self.label_to_id.get(f"I-{label_type}", self.label_to_id['O'])

        return labels

def train_simple_model():
    # Model ve tokenizer
    model_name = "dbmdz/bert-base-turkish-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Dataset
    train_dataset = SimpleNERDataset("train.jsonl", tokenizer)

    # Model
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(train_dataset.label_to_id),
        id2label=train_dataset.id_to_label,
        label2id=train_dataset.label_to_id
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./simple_ner_model",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_steps=50,
        save_steps=500,
        report_to=None
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer)
    )

    # Eğit
    print("Eğitim başlıyor...")
    trainer.train()

    # Kaydet
    trainer.save_model()
    tokenizer.save_pretrained("./simple_ner_model")
    print("Model kaydedildi: ./simple_ner_model")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Kullanılan cihaz:", device)

if __name__ == "__main__":
    train_simple_model()

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

def load_and_test():
    # Model ve tokenizer yükleniyor
    model_path = r"C:\Users\HP\PycharmProjects\Havelsan\.venv\vol2\simple_ner_model"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForTokenClassification.from_pretrained(model_path)
    except Exception as e:
        print("Model veya tokenizer yüklenemedi:", str(e))
        return

    # NER pipeline oluşturuluyor
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    while True:
        text = input("Bir cümle girin (çıkmak için 'q'): ")
        if text.lower() == 'q':
            break

        results = ner_pipeline(text)

        if not results:
            print("Hiçbir varlık bulunamadı.")
        else:
            print("\nTespit edilen varlıklar:")
            for entity in results:
                word = entity['word']
                label = entity['entity_group']
                score = entity['score']
                print(f"  - {word}: {label} ({score:.2f})")
        print("-" * 40)

if __name__ == "__main__":
    load_and_test()