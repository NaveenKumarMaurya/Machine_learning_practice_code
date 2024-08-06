import streamlit as st
import numpy as np
import pickle
from PIL import Image
import pandas as pd


# Load the trained model from the pickle file
with open('crop_recommendation_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict(value_input):
    # Format input data into array for prediction
    # value_input=np.array([p['Type'],p['Air temperature [K]'],p['Process temperature [K]'],p['Rotational speed [rpm]'],p['Torque [Nm]'],p['Tool wear [min]']
    # ,p['TWF'],p['HDF'],p['PWF'],p['OSF'],p['RNF']]).reshape(1,-1)
   
    # Make prediction using the model
    prediction = model.predict_proba(value_input)
    x=prediction>0.80
    x1=x>.80
    result=model.classes_[x1[0]][0]
    return result

st.title('Crop Prediction and Recommendation')
# Image path
image_path = 'Image-Crop-Recommendation@1x-1.png'

# Open the image file
img = Image.open(image_path)
img1=img.resize((400,280))

# Display the image
st.image(img1, caption='Sample Image')
st.write('Please enter the following information to Get the Crop Recommendation')

# Input fields
# Type = st.selectbox('Product type', ['H', 'M', 'L'],help='high ,medium, low')
Nitrogen=st.number_input('Nitrogen',help='10-140')
Phosphorous=st.number_input('Phosphorous',help='5-145')
Potassium=st.number_input('Potassium',help='5-205')
temperature	=st.number_input('temperature',help='8-43')
humidity=st.number_input('humidity',help='14-100')
ph=st.number_input('ph',help='3-10')
rainfall=st.number_input('rainfall',help='20-300')

# type_mapping = {'H': 5, 'M': 3, 'L': 2}
# failure_maping={'Yes':1,'No':0}
input_data={'Nitrogen':Nitrogen,'Phosphorous':Phosphorous,' Potassium':Potassium,'temperature':temperature,
'humidity':humidity ,'ph':ph, 'rainfall':rainfall}

final_df=pd.DataFrame([input_data])


if st.button('Predict'):
    prediction = predict(final_df)
    # if prediction[0] == 1:
    st.success('The crops Which could be good to grow on given condition is ----'+str(prediction))
    # else:
    #     st.success('The predicted risk of diabetes is low.')


