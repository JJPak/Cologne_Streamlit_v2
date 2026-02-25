import streamlit as st
import pandas as pd
import numpy as np
import time
from Module.Transpose_Neoma import data_crunch_neoma
import io


st.set_page_config(layout = "wide")


st.title ('Crunch data from Neoma for Excel')
st.write('Export data as CSV file with Qtegra - use the "182W_cycle_export" Export scheme. Only tick "Export sample lines as rows" and "Export complete LabBook" but not the rest. Make sure you use "Semicolon" as a "Column separator" and "Point" as "Decimal symbol".')

st.header('1. Upload you data')
upload_excel = st.file_uploader('XLSX file uploader', type = ['csv','xlsx'])

if upload_excel is not None:
    df = pd.read_csv(upload_excel,sep=';',engine='python')
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
    ('W', 'Hf',))

st.write('You selected:', element)
make_calculation = st.button('Push Button to transpose Data')


buffer = io.BytesIO()

if upload_excel == None and make_calculation == True:
    st.error('You forgot to upload a file')
    time.sleep(10)
if upload_excel != None and make_calculation == True:
    
    with st.spinner('Calculating this can take a few seconds...'):
        excel_file = data_crunch_neoma (df, element)
        st.success('The data was successfully filtered and transposed')

    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        excel_file.to_excel(writer, sheet_name='Transposed Data')
        writer.close()
        
        st.download_button(
            label="Download Excel worksheet",
            data=buffer,
            file_name="transposed_neoma.xlsx"
        )
