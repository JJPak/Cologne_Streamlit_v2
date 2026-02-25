import streamlit as st
import pandas as pd
import numpy as np
import time
from Module.Transpose_neptune import transpose_Neptune_To_Excel
import io


st.set_page_config(layout = "wide")


st.title ('Transpose Data from Neptune for Excel')


st.header('1. Upload you data')
upload_excel = st.file_uploader('XLSX file uploader', type = ['xlsx','xls'])

if upload_excel is not None:
    df = pd.read_excel(upload_excel)
    st.success('Upload was successful')
if upload_excel == None:
    text_3 = '<span style="color:red"> You did not upload a file yet. </style>' 
    st.markdown(text_3, unsafe_allow_html=True)
    
#  File preview
st.subheader(' 2.1 File preview')

if upload_excel is not None:
    Table_checkbox = st.checkbox('Do you want to see the table')

if upload_excel is not None and Table_checkbox == True:
    st.table(df.head(60))


# Transpose data

st.header('3. Transpose data')

st.subheader('3.1. Choose the element')

element = st.selectbox(
    'Which element do you choose',
    ('W','Mo'))

st.write('You selected:', element)

make_calculation = st.button('Push Button to transpose Data')


buffer = io.BytesIO()

if upload_excel == None and make_calculation == True:
    st.error('You forgot to upload a file')
    time.sleep(10)
if upload_excel != None and make_calculation == True:
    
    with st.spinner('Calculating this can take a few seconds...'):
        excel_file = transpose_Neptune_To_Excel(df,element,'Transposed_Filtere_Neptune_File')
        st.success('The data was successfully filtered and transposed')
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        excel_file.to_excel(writer, sheet_name='Transposed Data')
        writer.close()
        
        st.download_button(
            label="Download Excel worksheet",
            data=buffer,
            file_name="transposed_neptune.xlsx"
        )

