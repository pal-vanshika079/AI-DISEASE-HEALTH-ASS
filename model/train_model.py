import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../dataset/disease_dataset.csv"))

# Separate symptoms and disease
X = data.drop("Disease", axis=1)
y = data["Disease"]

# Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,stratify=y)


# Create the ML model
model = DecisionTreeClassifier(random_state=42)

# Train the model
model.fit(X_train, y_train)

# Test the model
predictions = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, predictions)

print("Model trained successfully!")
print("Model Accuracy:", accuracy)

# Save the trained model
model_path = os.path.join(os.path.dirname(__file__), "disease_model.pkl")

# Save the trained model inside the model folder
model_path = os.path.join(os.path.dirname(__file__), "disease_model.pkl")

with open(model_path, "wb") as file:
    pickle.dump(model, file)

print("Model saved successfully!")