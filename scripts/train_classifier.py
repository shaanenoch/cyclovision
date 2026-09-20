"""Train MobileNetV3 on explicitly separated satellite train/validation data.

Expected layout:
  DATA/train/<IMD class name>/*.png
  DATA/val/<IMD class name>/*.png

Keep every cyclone in only one split. The script refuses to create a random
image split because adjacent frames from one storm would leak information.
"""
from __future__ import annotations

import argparse
import copy
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

from backend.config import MODELS_DIR


def loaders(root: Path, batch_size: int):
    train_dir, val_dir = root / "train", root / "val"
    if not train_dir.is_dir() or not val_dir.is_dir():
        raise SystemExit("Dataset must contain separate train/ and val/ class folders")
    weights = MobileNet_V3_Small_Weights.DEFAULT
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(), transforms.RandomRotation(12),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_transform = weights.transforms()
    train_set = datasets.ImageFolder(train_dir, train_transform)
    val_set = datasets.ImageFolder(val_dir, val_transform)
    if train_set.classes != val_set.classes:
        raise SystemExit("train/ and val/ must contain the same class folders")
    return (
        DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=2),
        DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=2),
        train_set.classes,
    )


def evaluate(model, loader, device):
    model.eval(); labels, predictions, losses = [], [], []
    criterion = nn.CrossEntropyLoss()
    with torch.inference_mode():
        for images, target in loader:
            images, target = images.to(device), target.to(device)
            logits = model(images)
            losses.append(float(criterion(logits, target)))
            labels.extend(target.cpu().tolist())
            predictions.extend(logits.argmax(dim=1).cpu().tolist())
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="weighted", zero_division=0
    )
    return {
        "loss": float(np.mean(losses)), "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision), "recall": float(recall), "f1": float(f1),
        "labels": labels, "predictions": predictions,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output", type=Path, default=MODELS_DIR / "classification" / "cyclone_classifier_v2.pt")
    args = parser.parse_args()
    train_loader, val_loader, class_names = loaders(args.data, args.batch_size)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.DEFAULT)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(class_names))
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    best_state, best_accuracy, loss_history, accuracy_history = None, -1.0, [], []

    for epoch in range(1, args.epochs + 1):
        model.train(); train_losses, correct, count = [], 0, 0
        for images, target in train_loader:
            images, target = images.to(device), target.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(images); loss = criterion(logits, target)
            loss.backward(); optimizer.step()
            train_losses.append(float(loss)); correct += int((logits.argmax(1) == target).sum()); count += len(target)
        validation = evaluate(model, val_loader, device)
        train_loss, train_accuracy = float(np.mean(train_losses)), correct / count
        loss_history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": validation["loss"]})
        accuracy_history.append({"epoch": epoch, "train_acc": train_accuracy, "val_acc": validation["accuracy"]})
        if validation["accuracy"] > best_accuracy:
            best_accuracy, best_state = validation["accuracy"], copy.deepcopy(model.state_dict())
        print(f"Epoch {epoch}/{args.epochs}: train={train_accuracy:.3f}, val={validation['accuracy']:.3f}")

    model.load_state_dict(best_state)
    validation = evaluate(model, val_loader, device)
    matrix = confusion_matrix(validation["labels"], validation["predictions"], labels=list(range(len(class_names))))
    metadata = {
        "model_name": "MobileNetV3 Satellite Intensity Classifier", "model_version": "classifier-v2.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_samples": len(train_loader.dataset), "validation_samples": len(val_loader.dataset),
        "split_method": "pre-separated cyclone-wise train/val directories",
        "training_accuracy": accuracy_history[-1]["train_acc"],
        "validation_accuracy": validation["accuracy"], "precision": validation["precision"],
        "recall": validation["recall"], "f1_score": validation["f1"],
        "confusion_matrix": {"labels": class_names, "matrix": matrix.tolist()},
        "training_loss_history": loss_history, "accuracy_history": accuracy_history,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": best_state, "class_names": class_names, "metadata": metadata}, args.output)
    print(f"Saved verified checkpoint to {args.output}")


if __name__ == "__main__":
    main()
