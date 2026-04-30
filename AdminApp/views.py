from django.shortcuts import render
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from sklearn.preprocessing import LabelEncoder,StandardScaler

# Create your views here.
def index(request):
    return render(request,'index.html')

def AdminAction(request):
    uname=request.POST['username']
    passw=request.POST['password']
    if uname == 'Admin' and passw == 'Admin':
        return render(request,'AdminApp/AdminHome.html')
    else:
        context={'data':'Admin Login Failed..!!'}
        return render(request,'index.html',context)

def AdminHome(request):
    return render(request,'AdminApp/AdminHome.html')

data = None
def Upload(request):
    # global data
    # data=pd.read_csv("Dataset/sobar-72.csv", encoding='unicode_escape')
    # context={'data':data,'msg':'Dataset Loaded Successfully..!!'}
    return render(request,'AdminApp/Upload.html')


df = None

def UploadAction(request):
    global df
    if request.method == 'POST':
        file = request.FILES['dataset']
        df = pd.read_csv(file)

        # Dataset basic info
        columns = df.columns.tolist()
        rows = df.head(10).values.tolist()

        total_rows = df.shape[0]
        total_columns = df.shape[1]

        # Data types
        dtypes = df.dtypes.astype(str).to_dict()

        # Missing values
        missing_values = df.isnull().sum().to_dict()

        context = {
            'columns': columns,
            'rows': rows,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'dtypes': dtypes,
            'missing_values': missing_values
        }

        return render(request, 'AdminApp/ViewDataset.html', context)
    
X, y, X_train, X_test, y_train, y_test = None, None, None, None, None, None
def preprocess(request):
    global df,X, y, X_train, X_test, y_train, y_test

    df["Industry_Sector"]= df["Industry_Sector"].map({'IT Services':0,'Healthcare':1,'Manufacturing':2,'Banking':3,'E-commerce':4,'Retail':5})
    df["Cybersecurity_Risk_Level"] = df["Cybersecurity_Risk_Level"].map({'High': 0, 'Medium': 1, 'Low': 2})
    df["Forensic_Audit_Conducted"] = df["Forensic_Audit_Conducted"].map({'No': 0,'Yes': 1})
    df["Fraud_Detected"] = df["Fraud_Detected"].map({'No': 0,'Yes': 1})
    df["Fraud_Type"] = df["Fraud_Type"].map({'None': 0,'Identity Theft': 1,'Financial Statement Fraud': 2,'Asset Misappropriation': 3,'Corruption': 4})
    df["Cybersecurity_Breach"] = df["Cybersecurity_Breach"].map({'No': 0, 'Yes': 1})


    scaler = StandardScaler()
    df["Transaction_Amount_INR"] = scaler.fit_transform(df[["Transaction_Amount_INR"]])
    joblib.dump(scaler, 'Model/scaler.pkl')

    # Define input and output variables
    X = df.drop(columns=["Transaction_ID", "Company_Name", "Fraud_Detected"])
    y = df["Fraud_Detected"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    context={'data':str(len(df)),'train':str(len(X_train)), 'test':str(len(y_test))}
    return render(request, "AdminApp/Preprocess.html", context)

global adaacc,ada_model
def runANN(request):
    global X, y, X_train, X_test, y_train, y_test
    if X_train is None:
        return render(request, "AdminApp/AdminHome.html", {'msg': 'Please Preprocess the dataset before training the model!'})

    # Build ANN model
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')  # Binary classification (Fraud or Not Fraud)
    ])
    # Compile model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train model
    # Increasing epochs to 20 for better convergence
    history=model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), verbose=1)
    # Save model in 'Model' folder
    model.save("Model/fraud_detection_ann.h5")
    
    # Handle both 'accuracy' and 'acc' keys for compatibility
    if 'val_accuracy' in history.history:
        val_acc = history.history['val_accuracy'][-1]
    elif 'val_acc' in history.history:
        val_acc = history.history['val_acc'][-1]
    else:
        val_acc = 0
        
    print(f"Model Validation Accuracy: {val_acc * 100:.2f}%")
    context={'data':'Deep Learning Model Generated Successfully..!!', 'acc': f"Model Validation Accuracy: {val_acc * 100:.2f}%"}
    return render(request, "AdminApp/Algorithms.html", context)


