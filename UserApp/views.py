from django.shortcuts import render
import sqlite3
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder,StandardScaler
import tensorflow as tf

# Create your views here.
def login(request):
    return render(request,'UserApp/Login.html')
def register(request):
    return render(request,'UserApp/register.html')

def Userction(request):
    username=request.POST.get('username')
    password=request.POST.get('password')
    con = sqlite3.connect("fraud.db")
    cur=con.cursor()
    cur.execute("select *  from user where username='"+username+"'and password='"+password+"'")
    data=cur.fetchone()
    if data is not None:
        request.session['user']=data[2]
        request.session['userid']=data[0]
        return render(request,'UserApp/UserHome.html')
    else:
        context={'data':'Login Failed ....!!'}
        return render(request,'UserApp/Login.html',context)
def UserHome(request):
    return render(request,'UserApp/UserHome.html')

def RegAction(request):
    name=request.POST['name']
    email=request.POST['email']
    mobile=request.POST['mobile']
    address=request.POST['address']
    username=request.POST['username']
    password=request.POST['password']

    con = sqlite3.connect("fraud.db")
    cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS user (ID INTEGER PRIMARY KEY AUTOINCREMENT,name varchar(100),email varchar(100),mobile varchar(100),address varchar(100) ,username varchar(100),password varchar(100))")
    con.commit()
    cur.execute("select * from user where email='"+email+"'")
    d=cur.fetchone()
    if d is None:
        i=cur.execute("insert into user values(null,'"+name+"','"+email+"','"+mobile+"','"+address+"','"+username+"','"+password+"')")
        con.commit()
        con.close()
        if i == 0:
            context = {'data': 'Registration Failed...!!'}
            return render(request,'UserApp/register.html',context)
        else:
            context = {'data': 'Registration Successful...!!'}
            return render(request,'UserApp/register.html',context)
    else:
        context={'data':'Email Already Exist...!!'}
        return render(request,'UserApp/register.html',context)


def DetectFraud(request):
    path = "Dataset/fraud_detection_dataset.csv"
    df2 = pd.read_csv(path)
    df2.dropna(inplace=True)

    sector_map = {'IT Services': 0, 'Healthcare': 1, 'Manufacturing': 2, 'Banking': 3, 'E-commerce': 4, 'Retail': 5}
    ind_sec = "".join([f"<option value={v}>{d}</option>" for d, v in sector_map.items()])

    risk_map = {'High': 0, 'Medium': 1, 'Low': 2}
    crl = "".join([f"<option value={v}>{s}</option>" for s, v in risk_map.items()])

    fraud_map = {'None': 0, 'Identity Theft': 1, 'Financial Statement Fraud': 2, 'Asset Misappropriation': 3, 'Corruption': 4}
    fac = "".join([f"<option value={v}>{g}</option>" for g, v in fraud_map.items()])

    context={"ind_sec":ind_sec,"crl":crl,"fac":fac}
    return render(request,'UserApp/DetectFraud.html',context)

def PredAction(request):
    try:
        g = int(request.POST['ind_sec'])
        a = float(request.POST['tai'])
        m = int(request.POST['crl'])
        d = int(request.POST['fac'])
        lt = int(request.POST['ft'])
        Lg = float(request.POST['anm_score'])
        ref = int(request.POST['csb'])

        # Create a DataFrame with the same column names and order as used in training
        # Order: Sector, Amount, Risk, Audit, Type, Anomaly, Breach
        test_data = {
            'Industry_Sector': [g],
            'Transaction_Amount_INR': [a],
            'Cybersecurity_Risk_Level': [m],
            'Forensic_Audit_Conducted': [d],
            'Fraud_Type': [lt],
            'Anomaly_Score': [Lg],
            'Cybersecurity_Breach': [ref]
        }
        test_df = pd.DataFrame(test_data)

        # Load scaler and transform only the required column
        scaler = joblib.load('Model/scaler.pkl')
        test_df['Transaction_Amount_INR'] = scaler.transform(test_df[['Transaction_Amount_INR']])

        # Ensure column order matches exactly with AdminApp's X (dropping ID, Name, Detected)
        # Correct order: Industry_Sector, Transaction_Amount_INR, Cybersecurity_Risk_Level, Forensic_Audit_Conducted, Fraud_Type, Anomaly_Score, Cybersecurity_Breach
        cols = ['Industry_Sector', 'Transaction_Amount_INR', 'Cybersecurity_Risk_Level', 'Forensic_Audit_Conducted', 'Fraud_Type', 'Anomaly_Score', 'Cybersecurity_Breach']
        test_array = test_df[cols].values.astype('float32')

        # Load model and predict
        loaded_model = tf.keras.models.load_model('Model/fraud_detection_ann.h5')
        pred = loaded_model.predict(test_array)
        
        if pred[0][0] > 0.5:
            output = "Fraud Detected in Indian Businesses"
        else:
            output = "No Fraud Detected in Indian Businesses"
    except Exception as e:
        output = f"Error during prediction: {str(e)}"
    
    context = {"data": output}
    return render(request, 'UserApp/PredictedData.html', context)


