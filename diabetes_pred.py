import streamlit as st
import numpy as np
import pickle

# Load the trained model from the pickle file
with open('diabetes_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict(p):
    # Format input data into array for prediction
    value_input=np.array([p['Pregnancies'],p['Glucose'],p['BloodPressure'],p['SkinThickness'],p['Insulin'],p['BMI']
    ,p['DiabetesPedigreeFunction'],p['Age']]).reshape(1,-1)

    # Make prediction using the model
    prediction = model.predict(value_input)
    return prediction

st.title('Diabetes Prediction')
st.write('Please enter the following information to predict the risk of Diabetes')

# Input fields
Pregnancies = st.slider('Pregnancie in month', 0,9,1)
Glucose=st.number_input('Glucose level',help='44.0 -200.0')
BloodPressure=st.number_input('BloodPressure',help='30.0- 114.0')
SkinThickness=st.number_input('SkinThickness',help='8.0 - 99.0')
Insulin=st.number_input('Insulin',help='14.0 - 744.0')
BMI=st.number_input('BMI',help='18.2 - 59.4')
DiabetesPedigreeFunction=st.number_input('DiabetesPedigreeFunction',help='0.078 - 2.42')
Age=st.number_input('Age',help='21 - 81')

input_data={'Pregnancies':Pregnancies,'Glucose':Glucose,'BloodPressure':BloodPressure,'SkinThickness':SkinThickness,
'Insulin':Insulin ,'BMI':BMI, 'DiabetesPedigreeFunction':DiabetesPedigreeFunction,'Age':Age       }

# Predict button
if st.button('Predict'):
    prediction = predict(input_data)
    if prediction[0] == 1:
        st.success('The predicted risk of diabetes is high.')
    else:
        st.success('The predicted risk of diabetes is low.')


