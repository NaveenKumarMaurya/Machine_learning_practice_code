import streamlit as st
import numpy as np

from PIL import Image
import tensorflow as tf



# Load the trained model from the pickle file

model_pretrain = tf.keras.models.load_model("Potato_disease_detection.h5")

def prepare_image(image, target_size):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize(target_size)
    image = np.array(image)
    image = np.expand_dims(image, axis=0)
    return image

class_names=['Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy']


st.title('Potato Disease Prediction')
st.write('Please upload the potato leaf image')
# File uploader widget
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Display the uploaded image
    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

    # Preprocess the image
    prepared_image = prepare_image(image, target_size=(256, 256))  # Adjust the target size as per your model input
    
    if st.button('Predict'):
        prediction = model_pretrain.predict(prepared_image)
        acc=max(prediction[0])*100
        if acc>70:
            predicted_class = class_names[np.argmax(prediction[0])]
            st.write(f"The Model predicted Potato disease is: {predicted_class} with accuracy {acc}% ")
        else:
            st.write(f"Plaese Upload relavant image which is leaf of potato")
else:
    st.write(f"please upload the image file")