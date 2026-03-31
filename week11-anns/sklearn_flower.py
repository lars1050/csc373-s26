import csv
import random
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix, accuracy_score

random.seed(42)

# read the data
rows = []
with open('data/flowers_nonseparable.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append([float(row['petal_length']), float(row['petal_width']), int(row['species'])])

random.shuffle(rows)

# split 80/20
split = int(len(rows) * 0.8)
train = rows[:split]
test  = rows[split:]

X_train = np.array([r[:2] for r in train])
y_train = np.array([r[2]  for r in train])
X_test  = np.array([r[:2] for r in test])
y_test  = np.array([r[2]  for r in test])

# train
model = MLPClassifier(hidden_layer_sizes=(10,), max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# test accuracy
train_predictions = model.predict(X_train)
test_predictions  = model.predict(X_test)

print(f"Training Accuracy: {accuracy_score(y_train, train_predictions):.2%}")
print(f"Test Accuracy:     {accuracy_score(y_test, test_predictions):.2%}")

print(f"\nConfusion Matrix (test set):")
print(confusion_matrix(y_test, test_predictions))
print("Row = actual, Column = predicted")
