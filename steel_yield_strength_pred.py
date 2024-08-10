import streamlit as st
import numpy as np
import pickle
from PIL import Image
import pandas as pd
from sklearn.preprocessing import StandardScaler


# Load the trained model from the pickle file
with open('predictive_steel_strength.pkl', 'rb') as f:
    model = pickle.load(f)

def predict(value_input):
    # input_df=pd.DataFrame([value_input])
    
    # Make prediction using the model
    prediction = model.predict(value_input)
    
    return prediction

st.title('STEEL YIELD STRENTH PREDICTION')
# Image path
image_path = 'maxresdefault.jpg'

# Open the image file
img = Image.open(image_path)
img1=img.resize((400,280))

# Display the image
st.image(img1, caption='Sample Image')
st.write('Please enter the following information to Get the Yield strenth of steel')

# Input fields
# Type = st.selectbox('Product type', ['H', 'M', 'L'],help='high ,medium, low')
Carbon	=st.number_input('Carbon',help='0.0- 0.4')
Manganese=st.number_input('Manganese',help='0.01-2.46')
Silicon=st.number_input('Silicon',help='0.01 -3.11')
Chromium=st.number_input('Chromium',help='0.01-17.10')
Nickel=st.number_input('Nickel',help='0.01-18.77')
Molybdenum=st.number_input('Molybdenum',help='0.02-6.791')
Vanadium=st.number_input('Vanadium',help='0.01-1.88')
Nitrogen=st.number_input('Nitrogen',help='0.0-0.1')
Niobium=st.number_input('Niobium',help='0.01-0.41')
Cobalt=st.number_input('Cobalt',help='0.01-17.0')
Tungsten=st.number_input('Tungsten',help='0.0-5.77')
Aluminum=st.number_input('Aluminum',help='0.01-1.208')
Titanium=st.number_input('Titanium',help='0.0-2.095')




input_data={'c':Carbon,'mn':Manganese,'si':Silicon,'cr':Chromium,
'ni':Nickel , 'mo':Molybdenum,'v':Vanadium, 'n':Nitrogen,'nb':Niobium, 'co':Cobalt,'w':Tungsten,'al':Aluminum,'ti':Titanium}

df=pd.DataFrame([input_data])
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)
final_df=pd.DataFrame(X_scaled,columns=df.columns)


if st.button('Predict'):
    prediction = predict(final_df)
    # if prediction[0] == 1:
    st.success('The yield strength of steel will be----'+str(prediction))
    # else:
    #     st.success('The predicted risk of diabetes is low.')



    
