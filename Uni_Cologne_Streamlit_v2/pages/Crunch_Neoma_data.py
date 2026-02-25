import streamlit as st
import pandas as pd
import numpy as np
import time
from Module.Crunch_Neoma_Data import crunch_neoma_data
import io


st.set_page_config(layout = "wide")


st.title ('Crunch data from Neoma for Excel')

st.header('1 Crunch your Neoma Data')
st.subheader('1.1. Instructions')

st.write('Please export your data in the described way, else the crunching algorithm may not work')
st.write('1. Open the lab book you want to export')
st.write('2. Click on the export button which looks like a small book with an arrow pointing to the right. It can be found in the top of the left side below the "Home page" header')
st.write('3. A window will pop up for exporting your data. To export your data choose "CSV Export" for your Exporter. You can adjust this in the first drop down menu')
st.write('4. In the second drop down menu use "Average Data Export" for your Export scheme')
st.write('5. On the right side you can tick multiple boxes. Only choose "Export complete LabBook". Everything else should not be chosen!')
st.write('6. Choose "Semicolon" as "Column separator" and choose "Point" as "Decimal Symbol"')
st.write('7. Choose your export Path and your Filename')
st.write('8. Export your data')
st.write('9. Drag and Drop the CSV file into the area below')
st.write('10. Follow further instruction within the website')
st.write()
st.write('CRUNCHING FOR NEW ELEMENTS NEEDED? - CONTACT JP')
         

st.header('2. Upload you data')
upload_excel = st.file_uploader('CSV file uploader', type = ['csv','xlsx'])
try:
         if upload_excel is not None:
             df = pd.read_csv(upload_excel,sep=';',engine='python')
             st.success('Upload was successful')
except: 
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


# Choose the element needed         
st.subheader('3.1. Choose the element')

element = st.selectbox(
    'Which element do you choose', ('Hf','Nd', 'Cd'))

st.write('You selected:', element)

make_calculation = st.button('Push Button to Crunch your data')


buffer = io.BytesIO()

if upload_excel == None and make_calculation == True:
    st.error('You forgot to upload a file')
    time.sleep(10)
if upload_excel != None and make_calculation == True:
    
    with st.spinner('Calculating this can take a few seconds...'):
        excel_file = crunch_neoma_data (df, element)
        st.success('The data was successfully filtered and transposed')
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        excel_file.to_excel(writer, sheet_name='Transposed Data')
        writer.close()
        
        st.download_button(
            label="Download Excel worksheet",
            data=buffer,
            file_name= element+"_crunched_neoma.xlsx"
        )
