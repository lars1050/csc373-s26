import csv
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

random.seed(42)
torch.manual_seed(42)

# --- Load data ---
rows = []
with open('data/flowers_nonseparable.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append([float(row['petal_length']), float(row['petal_width']), int(row['species'])])

random.shuffle(rows)

# --- Split 80/20 ---
split = int(len(rows) * 0.8)
train = rows[:split]
test  = rows[split:]

X_train = torch.tensor([r[:2] for r in train], dtype=torch.float32)
y_train = torch.tensor([r[2]  for r in train], dtype=torch.long)
X_test  = torch.tensor([r[:2] for r in test],  dtype=torch.float32)
y_test  = torch.tensor([r[2]  for r in test],  dtype=torch.long)

# --- Define the network ---
class FlowerNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(2, 10)   # 2 inputs -> 10 hidden neurons
        self.fc2 = nn.Linear(10, 3)   # 10 hidden -> 3 output classes

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)               # no activation here, CrossEntropyLoss handles it
        return x

model = nn.Module() if False else FlowerNet()

# --- Loss and optimizer ---
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# --- Train ---
epochs = 1000
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")

# --- Test ---
model.eval()
with torch.no_grad():
    train_preds = model(X_train).argmax(dim=1)
    test_preds  = model(X_test).argmax(dim=1)

train_acc = (train_preds == y_train).float().mean()
test_acc  = (test_preds  == y_test).float().mean()

print(f"\nTraining Accuracy: {train_acc:.2%}")
print(f"Test Accuracy:     {test_acc:.2%}")

# --- Confusion matrix ---
from sklearn.metrics import confusion_matrix
print("\nConfusion Matrix (test set):")
print(confusion_matrix(y_test.numpy(), test_preds.numpy()))
print("Row = actual, Column = predicted")
