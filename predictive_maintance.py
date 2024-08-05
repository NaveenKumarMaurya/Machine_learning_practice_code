import streamlit as st
import numpy as np
import pickle
from PIL import Image
import pandas as pd
from sklearn.preprocessing import StandardScaler,MinMaxScaler

# Load the trained model from the pickle file
with open('predictive_maintainance_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict(value_input):
    # Format input data into array for prediction
    # value_input=np.array([p['Type'],p['Air temperature [K]'],p['Process temperature [K]'],p['Rotational speed [rpm]'],p['Torque [Nm]'],p['Tool wear [min]']
    # ,p['TWF'],p['HDF'],p['PWF'],p['OSF'],p['RNF']]).reshape(1,-1)
   
    # Make prediction using the model
    prediction = model.predict_proba(value_input)[0][1]
    return prediction

st.title('Predictive Maintenance of Machine')
# Image path
image_path = 'Metalworking2.jpg'

# Open the image file
img = Image.open(image_path)
img1=img.resize((400,280))

# Display the image
st.image(img1, caption='Sample Image')
st.write('Please enter the following information to predict machine failure')

# Input fields
Type = st.selectbox('Product type', ['H', 'M', 'L'],help='high ,medium, low')
Air_temperature=st.number_input('Air_temperature',help='Measured in Kelvin (K), generated using a random walk process and normalized to a standard deviation of 2 K around 300 K')
Process_temperature=st.number_input('Process_temperature',help='Measured in Kelvin (K), generated using a random walk process normalized to a standard deviation of 1 K, added to the air temperature plus 10 K')
Rotational_speed=st.number_input('Rotational_speed',help='Measured in revolutions per minute (rpm), calculated from a power of 2860 W with normally distributed noise')
Torque=st.number_input('Torque',help='Measured in Newton meters (Nm), normally distributed around 40 Nm with a standard deviation of 10 Nm, and no negative values')
Tool_wear=st.number_input('Tool_wear',help=' Measured in minutes (min), varies by product quality ')
TWF=st.selectbox('Tool wear failure',['Yes', 'No'],help='Tool failure or replacement between 200-240 mins, randomly assigned')
HDF=st.selectbox('Heat dissipation failure',['Yes', 'No'],help='Failure if temperature difference is below 8.6 K and rotational speed is below 1380 rpm')
PWF=st.selectbox('Power failure',['Yes', 'No'],help='Failure if power (torque * rotational speed in rad/s) is below 3500 W or above 9000 W')
OSF=st.selectbox('Overstrain failure ',['Yes', 'No'],help='Failure if product of tool wear and torque exceeds thresholds (11,000 minNm for L, 12,000 for M, 13,000 for H)')
RNF=st.selectbox('Random failures',['Yes', 'No'],help='Each process has a 0.1% chance of failure regardless of parameters')

type_mapping = {'H': 5, 'M': 3, 'L': 2}
failure_maping={'Yes':1,'No':0}
input_data={'Type':type_mapping[Type],'Air temperature [K]':Air_temperature,'Process temperature [K]':Process_temperature,'Rotational speed [rpm]':Rotational_speed,
'Torque [Nm]':Torque ,'Tool wear [min]':Tool_wear, 'TWF':failure_maping[TWF],'HDF':failure_maping[HDF] ,'PWF':failure_maping[PWF], 'OSF' :failure_maping[OSF],'RNF':failure_maping[RNF]    }
 # ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
# Predict button
input_df=pd.DataFrame([input_data])
col_to_scale=['Type', 'Air temperature [K]', 'Process temperature [K]',
       'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']


# StandardScaler()
scaler = MinMaxScaler()
col_scaled = scaler.fit_transform(input_df[col_to_scale])
df1=pd.DataFrame(col_scaled,columns=col_to_scale)
col2=['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
df2=input_df[col2]
final_df=pd.concat([df1,df2],axis=1)

if st.button('Predict'):
    prediction = predict(final_df)*100
    # if prediction[0] == 1:
    st.success('The probability of machine failure is :'+str(prediction)+ '%')
    # else:
    #     st.success('The predicted risk of diabetes is low.')


