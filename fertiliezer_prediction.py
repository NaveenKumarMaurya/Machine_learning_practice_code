import streamlit as st
import numpy as np
import pickle
from PIL import Image
import pandas as pd


# Load the trained model from the pickle file
with open('fertiliezer_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict(value_input):
    input_df=pd.DataFrame([value_input])
    dummy_df=pd.get_dummies(input_df, columns=['Soil','Crop'],dtype='int')
    dummy_var=['Soil_alluvial', 'Soil_Clayey','Soil_clay loam', 'Soil_coastal', 'Soil_laterite','Soil_sandy', 'Soil_silty clay','Crop_Coconut', 'Crop_rice']
    dic={}
    for k in dummy_var:
        if k not in list(dummy_df.columns):
            dic.update({k:0})
    dummy_df2=pd.DataFrame([dic])
    final_df=pd.concat([dummy_df,dummy_df2],axis=1)
    column_order=['Temperature', 'Humidity', 'Rainfall', 'pH', 'N', 'P', 'K',
       'Soil_Clayey', 'Soil_alluvial', 'Soil_clay loam', 'Soil_coastal',
       'Soil_laterite', 'Soil_sandy', 'Soil_silty clay', 'Crop_Coconut',
       'Crop_rice']
    x=final_df[column_order]
    
    
    # Make prediction using the model
    prediction = model.predict(x)
    
    return prediction

st.title('FERTILIZER PREDICTION')
# Image path
image_path = 'shutterstock_301313486.jpg'

# Open the image file
img = Image.open(image_path)
img1=img.resize((400,280))

# Display the image
st.image(img1, caption='Sample Image')
st.write('Please enter the following information to Get the Fertiliezer')

# Input fields
# Type = st.selectbox('Product type', ['H', 'M', 'L'],help='high ,medium, low')
Temperature	=st.number_input('Temperature',help='8-43')
Humidity=st.number_input('Humidity',help='14-100')
Rainfall=st.number_input('Rainfall',help='20-300')
pH=st.number_input('ph',help='3-10')
Nitrogen=st.number_input('Nitrogen',help='2-5')
Phosphorous=st.number_input('Phosphorous',help='2-4')
Potassium=st.number_input('Potassium',help='1.9-4')
Soil = st.selectbox('Soil', ['silty clay', 'Clayey', 'sandy', 'coastal', 'clay loam', 'laterite','alluvial'])
Crop = st.selectbox('Crop', ['rice', 'Coconut'])

# type_mapping = {'H': 5, 'M': 3, 'L': 2}
# failure_maping={'Yes':1,'No':0}
input_data={'Temperature':Temperature,'Humidity':Humidity,'Rainfall':Rainfall,'pH':pH,
'N':Nitrogen , 'P':Phosphorous,'K':Potassium, 'Soil':Soil,'Crop':Crop}

# final_df=pd.DataFrame([input_data])


if st.button('Predict'):
    prediction = predict(input_data)
    # if prediction[0] == 1:
    st.success('The fertiliezer which could be the best for you crop at given condition is ----'+str(prediction))
    # else:
    #     st.success('The predicted risk of diabetes is low.')


