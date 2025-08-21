from sklearn.metrics import classification_report, accuracy_score
import numpy as np
from tqdm import tqdm
import torch
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,AutoConfig)
import json
from NER_model import SimpleNERDataset
from seqeval.metrics import classification_report as seqeval_report
from seqeval.metrics import accuracy_score as seqeval_accuracy

def evaluate_model(model_path="C:/Users/HP/PycharmProjects/Havelsan/simple_ner_model", test_path="test.jsonl"):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = AutoConfig.from_pretrained(model_path, local_files_only=True)
    label_to_id = config.label2id
    id_to_label = {int(k): v for k, v in config.id2label.items()}

    # Tokenizer ve model
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForTokenClassification.from_pretrained(model_path, local_files_only=True)
    model.to(device)
    model.eval()

    # Etiket haritası yükle
    with open(f"{model_path}/label_map.json", "r", encoding="utf-8") as f:
        label_to_id = json.load(f)
    id_to_label = {int(v): k for k, v in label_to_id.items()}

    # Dataset
    test_dataset = SimpleNERDataset("C:/Users/HP/PycharmProjects/Havelsan/simple_ner_model/test.jsonl", tokenizer, label_to_id=label_to_id)

    true_labels = []
    pred_labels = []

    with torch.no_grad():
        for item in tqdm(test_dataset, desc="Evaluating"):
            input_ids = item['input_ids'].unsqueeze(0).to(device)
            attention_mask = item['attention_mask'].unsqueeze(0).to(device)
            labels = item['labels'].numpy()

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = torch.argmax(outputs.logits, dim=2).squeeze().cpu().numpy()

            valid_tokens = attention_mask.squeeze().cpu().numpy() == 1
            true = labels[valid_tokens]
            pred = predictions[valid_tokens]

            true_labels.extend(true)
            pred_labels.extend(pred)

    true_tags = [id_to_label[i] for i in true_labels]
    pred_tags = [id_to_label[i] for i in pred_labels]

    print("\nClassification Report:")
    print(classification_report(true_tags, pred_tags, digits=4))
    print(f"\nAccuracy: {accuracy_score(true_tags, pred_tags):.4f}")

    # Dönüştürülmüş: her cümle bir liste → [ ["B-sirket", "I-sirket", "O", ...], [...], ... ]
    true_entities = []
    pred_entities = []

    sentence_true = []
    sentence_pred = []

    for t, p in zip(true_tags, pred_tags):
        sentence_true.append(t)
        sentence_pred.append(p)

        if t == 'O' and p == 'O':
            true_entities.append(sentence_true)
            pred_entities.append(sentence_pred)
            sentence_true = []
            sentence_pred = []

    # Eğer son cümle kaldıysa
    if sentence_true:
        true_entities.append(sentence_true)
        pred_entities.append(sentence_pred)

    # Raporu yazdır
    print("\nEntity-Level (seqeval) Classification Report:")
    print(seqeval_report(true_entities, pred_entities, digits=4))
    print(f"\nEntity-Level Accuracy: {seqeval_accuracy(true_entities, pred_entities):.4f}")

    return true_tags, pred_tags

if __name__ == "__main__":
    true_tags, pred_tags = evaluate_model()


from seqeval.metrics import classification_report as seqeval_classification_report
from seqeval.metrics import accuracy_score as seqeval_accuracy_score

# Entity-level için true/pred tag listesi zaten mevcut olmalı
# Eğer yoksa, model tahminlerinden token -> entity dönüşümü yapan blokta bu listeler oluşmalı
# Örnek olarak seqeval için:
entity_level_acc = seqeval_accuracy_score(true_tags, pred_tags)
entity_count = sum([len(seq) for seq in true_tags])
correct_entities = int(entity_level_acc * entity_count)

print("\nEntity-Level Doğruluk Özeti:")
print(f"Test Veri Setindeki Toplam Entity Sayısı: {entity_count}")
print(f"Doğru Tahmin Edilen Entity Sayısı: {correct_entities}")
print(f"Entity Doğruluk Oranı: {entity_level_acc:.4f}")


from sklearn.metrics import accuracy_score

# y_true, y_pred -> düzleştirilmiş etiket listeleri
# Bunlar classification_report()'ta kullandığın listeyle aynı olmalı

token_accuracy = accuracy_score(y_true, y_pred)
print("\nToken Bazlı Doğruluk (Accuracy)")
print(f"Toplam Token Sayısı: {len(y_true)}")
print(f"Doğru Tahmin Edilen Token Sayısı: {(token_accuracy * len(y_true)):.0f}")
print(f"Accuracy: {token_accuracy:.4f}")
