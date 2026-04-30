import os
import sqlite3
import joblib
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

# Set paths
base_path = 'c:/Users/Administrator/Desktop/1-4-26/Impact of Cyber Security and Forensic Accounting Techniques on Fraud Detection in Indian Businesses/SOURCE CODE/Fraud_Detection_IndianBusinesses'
model_path = os.path.join(base_path, 'Model/fraud_detection_ann.h5')
scaler_path = os.path.join(base_path, 'Model/scaler.pkl')
dataset_path = os.path.join(base_path, 'Dataset/fraud_detection_dataset.csv')

# Load dataset and pick a known fraud row
df = pd.read_csv(dataset_path)
fraud_data = df[df['Fraud_Detected'] == 'Yes'].head(5)
print(f"Found {len(fraud_data)} fraud rows to test.")

# Define mapping (same as AdminApp)
sector_map = {'IT Services': 0, 'Healthcare': 1, 'Manufacturing': 2, 'Banking': 3, 'E-commerce': 4, 'Retail': 5}
risk_map = {'High': 0, 'Medium': 1, 'Low': 2}
fac_map = {'No': 0, 'Yes': 1}
fraud_map = {'None': 0, 'Identity Theft': 1, 'Financial Statement Fraud': 2, 'Asset Misappropriation': 3, 'Corruption': 4}
csb_map = {'No': 0, 'Yes': 1}

# Convert a fraud row for testing
row = fraud_data.iloc[0]
test_input = {
    'Industry_Sector': sector_map[row['Industry_Sector']],
    'Transaction_Amount_INR': row['Transaction_Amount_INR'],
    'Cybersecurity_Risk_Level': risk_map[row['Cybersecurity_Risk_Level']],
    'Forensic_Audit_Conducted': fac_map[row['Forensic_Audit_Conducted']],
    'Fraud_Type': fraud_map[row['Fraud_Type']],
    'Anomaly_Score': row['Anomaly_Score'],
    'Cybersecurity_Breach': csb_map[row['Cybersecurity_Breach']]
}

test_df = pd.DataFrame([test_input])
print("Test Input Row (Pre-scaling):")
print(test_df)

# Scale
scaler = joblib.load(scaler_path)
test_df['Transaction_Amount_INR'] = scaler.transform(test_df[['Transaction_Amount_INR']])

# Load model and predict
model = tf.keras.models.load_model(model_path)
pred = model.predict(test_df.values.astype('float32'))
print(f"Prediction Probability: {pred[0][0]}")
if pred[0][0] > 0.5:
    print("Result: Fraud Detected")
else:
    print("Result: No Fraud Detected")
