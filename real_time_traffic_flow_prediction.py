# -*- coding: utf-8 -*-
"""Real_Time_Traffic_Flow_Prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fcxrMmR_jaOfjEsN8qKtlwpnDtlbqE7d

Project Name: **Real Time Traffic Flow Prediction**

Prepared On: **03 Feb 2025**

### Import Libraries
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df2 = pd.read_csv('/content/Traffic.csv')
print(df2.shape)
df2.sample(5)

df1 = pd.read_csv('/content/TrafficTwoMonth.csv')
print(df1.shape)
df1.sample(5)

# To join this two dataframe, first we ensure the columns and dtype of both dataframe are same, let verify
print(df2.columns == df1.columns)
print(df2.dtypes == df1.dtypes)

# combined the two dataframe df2 and df1
df = pd.concat([df2,df1], axis=0, ignore_index=True).reset_index(drop=True)
print(df.shape)
df.sample(10)

# check for null values
df.isnull().sum()

# check for duplication
df.duplicated().sum()

df = df.drop_duplicates(keep='first')

df.duplicated().sum()

"""### Feature Engineering"""

# We will work with copy of original
df = df.copy()

# renaming
df = df.rename(columns={'Date': 'Day_of_Month'})

df.sample(2)

# Split Time into Hour, Minute, and AM/PM without adding a date
df['Hour'] = df['Time'].str.extract(r'(\d+):')[0].astype(int)  # Extract hour
df['Minute'] = df['Time'].str.extract(r':(\d+)')[0].astype(int)  # Extract minute
df['AM_PM'] = df['Time'].str.extract(r'([APM]+)')[0]  # Extract AM/PM

df.sample(2)

df = df.drop(columns=['Time'])
df.sample(2)

"""### Transformation"""

day_mapping = {
    'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
    'Friday': 5, 'Saturday': 6, 'Sunday': 7
}

df['Day_of_Week_Encoded'] = df['Day of the week'].map(day_mapping)

def convert_to_24_hour(hour, am_pm):
    if am_pm == 'AM' and hour == 12:
        return 0  # 12 AM → 00
    elif am_pm == 'PM' and hour != 12:
        return hour + 12  # Convert PM hours (except 12 PM)
    else:
        return hour  # Keep other cases unchanged

df['Hour_24'] = df.apply(lambda row: convert_to_24_hour(row['Hour'], row['AM_PM']), axis=1)

df = df.drop(columns=['AM_PM','Day of the week','Hour'])

df.sample(5)

"""### EDA"""

import matplotlib.pyplot as plt
import seaborn as sns

# Set up the subplot grid: 1 row, 4 columns
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Plot for 'Day_of_Month' vs 'Total'
sns.lineplot(x='Day_of_Month', y='Total', data=df, ax=axes[0])
axes[0].set_title('Day of Month vs Total Traffic')
axes[0].set_xlabel('Day of Month')
axes[0].set_ylabel('Total Traffic Volume')

# Plot for 'CarCount' vs 'Total'
sns.lineplot(x='Hour_24', y='Total', data=df, ax=axes[1])
axes[1].set_title('Hour-24 vs Total Traffic')
axes[1].set_xlabel('Hour')
axes[1].set_ylabel('Total Traffic Volume')

# Plot for 'BikeCount' vs 'Total'
sns.lineplot(x='Day_of_Week_Encoded', y='Total', data=df, ax=axes[2])
axes[2].set_title('Day_of_Week vs Total Traffic')
axes[2].set_xlabel('Day_of_Week')
axes[2].set_ylabel('Total Traffic Volume')

# Adjust layout for better readability
plt.tight_layout()

# Show the plots
plt.show()

# check the distribution of target variable
sns.countplot(x='Traffic Situation',data=df)
plt.title('Distribution of traffic Situation')
plt.show()

"""### Normalization & Split"""

X = df.drop(columns=['Traffic Situation']).values
y = df['Traffic Situation'].values

X

X.shape

from sklearn.preprocessing import LabelEncoder

# Encode the target variable
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(df['Traffic Situation'])

# Check the encoded classes
print("Encoded Classes:", label_encoder.classes_)

from tensorflow.keras.utils import to_categorical

# One-hot encode the target variable
y_one_hot = to_categorical(y_encoded)

# Check the shape of the one-hot encoded target
print("Shape of y_one_hot:", y_one_hot.shape)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test = train_test_split(X,y_one_hot,test_size=0.2,random_state=1)

X_train.shape, X_test.shape, y_train.shape, y_test.shape

from sklearn.preprocessing import StandardScaler
import joblib

# Initialize the scaler
scaler = StandardScaler()

# Fit the scaler on training data and transform it
X_train_scale = scaler.fit_transform(X_train)

# Transform the test data using the same scaler (without fitting)
X_test_scale = scaler.transform(X_test)

# Save the fitted scaler to a file
joblib.dump(scaler, 'scaler.pkl')

X_train_scale[0]

"""### Model Building"""

import tensorflow
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout,BatchNormalization,Input

model = Sequential()

model.add(Input(shape=(9,)))

model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.2))

model.add(Dense(32, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.3))

model.add(Dense(16, activation='relu'))

model.add(Dense(y_one_hot.shape[1], activation='softmax'))


model.compile(optimizer='Adam',loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()

# Train the model
history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.2,
)

"""### Evaluate the Model"""

# Plot training and validation loss
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Plot training and validation loss
plt.plot(history.history['accuracy'], label='Training accuracy')
plt.plot(history.history['val_accuracy'], label='Validation accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('accuracy')
plt.legend()
plt.show()

# Evaluate on Test Data
test_loss, test_accuracy = model.evaluate(X_test,y_test,verbose=0)
print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")

import numpy as np

# Convert one-hot encoded y_test and y_pred to class labels
y_true_classes = np.argmax(y_test, axis=1)
y_pred_classes = np.argmax(y_pred, axis=1)


from sklearn.metrics import confusion_matrix

# Compute the confusion matrix
cm = confusion_matrix(y_true_classes, y_pred_classes)

# Print the confusion matrix
print("Confusion Matrix:")
print(cm)

import seaborn as sns
import matplotlib.pyplot as plt

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

"""### Save The Model"""

# Save the trained model
model.save('traffic_prediction_model.keras')

"""### Make Prediction on New Data"""

from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np
from tensorflow.keras.models import load_model

# Load the saved model
loaded_model = load_model('traffic_prediction_model.keras')

# Load the saved scaler
scaler = joblib.load('scaler.pkl')

# Load the label encoder (assume it's saved earlier)
# label_encoder = joblib.load('label_encoder.pkl')  # Uncomment if you saved label encoder

# Function to get user input
def get_user_input():
    print("Enter the following traffic data:")
    car_count = int(input("Car Count: "))
    bike_count = int(input("Bike Count: "))
    bus_count = int(input("Bus Count: "))
    truck_count = int(input("Truck Count: "))
    total_count = int(input("Total Count: "))
    day_of_month = int(input("Day of Month: "))
    day_of_week_encoded = int(input("Day of Week (Encoded): "))
    minute = int(input("Minute: "))
    hour_24 = int(input("Hour (24-hour format): "))

    return np.array([[car_count, bike_count, bus_count, truck_count, total_count,
                       day_of_month, day_of_week_encoded, minute, hour_24]])

# Get user input
new_data = get_user_input()

# Normalize the new data using the loaded scaler
new_data_scaled = scaler.transform(new_data)

# Make prediction using the loaded model
prediction = loaded_model.predict(new_data_scaled)

# Convert probabilities to class labels
predicted_class = np.argmax(prediction, axis=1)

# Convert class labels to original traffic situation labels (use label_encoder if saved)
# predicted_traffic_situation = label_encoder.inverse_transform(predicted_class)

# Example: Assuming you manually map class labels to traffic situations
traffic_situations = ['low', 'normal', 'heavy', 'high']
predicted_traffic_situation = traffic_situations[predicted_class[0]]

# Output the result
print(f"Predicted Traffic Situation: {predicted_traffic_situation}")

