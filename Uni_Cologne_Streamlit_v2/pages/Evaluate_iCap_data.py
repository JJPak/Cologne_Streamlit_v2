import streamlit as st
import pandas as pd
import io
import os
import numpy as np
from PIL import Image
from math import floor, log10
from Module.iCap_eval import del_ycps, subsheets, calc_background_cps, filter_for_qualitiy_data


path = os.path.dirname(__file__)

# ---------------------------------------------------------------- Page layout


# ---------------------------------------------------------------- Introduction
st.title(' Evaluate iCap data ')
st.subheader('A constant method for iCap evaluation at the UoC')

text_1 = """ If you just finished you iCap trace element measurement and already looked at the calibrations
of the individual elements you are at the right place. Else look at step 0.
The underlying program of this site will upload your 
iCap data and evaluate it as recommended by the AG Geo- and Cosmochemistry of the University of Cologne."""
st.markdown(text_1)

# ---------------------------------------------------------------- Step - check your calibrations

st.header('0. Evaluation in Qtegra - skip if finished')
text_0 = """Before you use the underlying code to evaluate your data you should look at the goodness of
the calibrations of your individual elements. This can be done within Qtegra. If you need help here ask
JP or FWo. In general you look at the calibrations that can be found if you look on the left side of Qtegra
where you can see "iCap" unfold the "iCap folder and click on "Concentrations". You should now see a table
where all concentrations can be seen. Click on the row with "Standard/Calibration" you can now see the different
calibrations. Enlarge the calibrations by clicking on the calibration. You can now see the calibration curve,
the datapoints of the reference materials and the error of the calibration.\n
- If you see an obvious outlier in the calibration, make a right click on the datapoint of the outlier
  and choose "exclude standard". \n
- The outlier will be excluded and the concentration based on the calibration will be calculated again.\n
- Make notes which reference material you deleted from the calibration for which elements. \n 
- If you measu#ED6363 a calibration multiple times during a measurement session do not forget to 
  delete the reference material for the specific element as well for the other calibrations. \n 
- If you are finished export your data. Make sure you export at least the Intensity, the concentration
  the concentration RSD and the calibration coeficient. These values are needed for the evaluation"""
st.markdown(text_0)


# ---------------------------------------------------------------- Show image as question
st.header(' 1. Check Excel File ')
text_2 = """ First check if your Excel file is in the right format"""
st.markdown(text_2)
# image1 = Image.open(path+'/images/icap_eval_plot.png')
st.image(path+'/images/icap_eval_plot.png')

text_3 = """ It is important that the first row of the Excel table is still the type of the data below (e.g. RAW.Average,
ExtCal.Average, etc.). Furthermore do ***NOT*** delete or change the second (row with zeros), the third  (row with element name, measurement mode),
or the fourth row (row with Y (unit)). ***To evaluate the data the Intensity in cps, the concentration in ugg, as well as the relative standard deviation (RSD)
of the concentration is needed in the Excel table***. This can be downloaded via the Qtegra Software. """
st.markdown(text_3)

# ----------------------------------------------------------------- Upload data

st.header(' 2. Upload you Excel file')

input_file_marker_1 = '<span style="color:#21E6C1"> ---------------------------------------------------------------Input field-------------------------------------------------------------- </style>'
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
upload_excel = st.file_uploader(
    'XLS / XLSX file uploader', type=['xlsx', 'xls'])
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

if upload_excel is not None:
    df = pd.read_excel(upload_excel)
    st.success('Upload was successful')
if upload_excel == None:
    text_3 = '<span style="color:#ED6363"> You did not upload a file yet. </style>'
    st.markdown(text_3, unsafe_allow_html=True)
#  File preview
st.subheader(' 2.1 File preview')
if upload_excel is not None:
    st.table(df.head(15))

# ---------------------------------------------------------------- Check if 'Order' and 'Sample' is in column
try:
    if upload_excel is not None:
        if df.loc[1, 'SampleList'] != 'Order':
            df.loc[1, 'SampleList'] = 'Order'
        if df.loc[1, 'SampleList.1'] != 'Sample':
            df.loc[1, 'SampleList.1'] = 'Sample'
except Exception:
    text_3 = """<span style="color:#ED6363"> 
    And datatable check was not successful	
    </style> """

    st.markdown(text_3, unsafe_allow_html=True)

# ---------------------------------------------------------------- Name of BG, Name of HNO3, z_score outlier

st.header(' 3. Define your Background and HNO3 measurement ')

text_4 = """ Background measurements and HNO3 measurements are used to calculate the Background of you measurement session.
The Background is the sample where you added the RhRe standard to the clean beaker. Some people measure 0.28 HNO3 to clean the introduction system
of the iCap from sticky elements. These HNO3 measurements can as well be used to calculate the Background."""
st.markdown(text_4)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
BG_name = st.text_input('Name of the BG in the measurement file: ', placeholder='BG',
                        help='Here you have to add the name of the Background. The name has to be exactly the same as in the Excel file')

HNO3_name = st.text_input('Name of the HNO3 in the measurement file: ', placeholder='HNO3',
                          help='Here you have to add the name of the HNO3 measurement. The name has to be exactly the same as in the Excel file')
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker


# ---------------------------------------------------------------- Filter Background add additional data

st.header(' 4. Background')

# Filter Background
st.subheader('4.1 Filter your Background data')
text_5 = """ Within Background and HNO3 measurements outliers can be present. Outliers are in general filte#ED6363 out by deleting data that fall outside a specific range.
This range is defined by two boundaries. An upper (UB) and a lower boundary (LB). The boundaries are defined by the mean value (M) of a dataset as well as the standard deviation (sd) multiplied
by a factor "a"."""
st.markdown(text_5)

col1, col2, col3 = st.columns([1, 2, 1])
col1.latex(r'\mathrm{LB = M - a * sd}')
col2.image(path+'/images/Dichteverteilung.png',
           caption=r'Source: https://www.geothermie.de/bibliothek/lexikon-der-geothermie/g/gauss-verteilung.html')
col3.latex(r'\mathrm{UB = M + a * sd}')

text_6 = """ How should your Background measurements be filtered. It is reccomended to set a = 2 if you have not prefilte#ED6363 the dataset for obvious outliers. If
you already filter you dataset for obvious outliers set 'a' to a higher value (e.g. a = 3)"""
st.markdown(text_6)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
BG_outlier_num = st.number_input('Factor a = ', value=2)
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker



################################ DONT USE ##########################

### Intensities can be different from day to day using old measurements for LOQ of new data might over or underestimate the LOQ'''



# Add additional background data 
#input_file_marker_2 = """<span style="color:#FF004D"> ############_______________________!DEPRECATED USE NOT RECOMMENDED!________________________############ </style>"""
#st.markdown(input_file_marker_2, unsafe_allow_html=True)

# st.subheader(' 4.2 Add more Background data ')
# text_7 = """ However especially if only few amounts of Background and HNO3 measurements are available outliers can have a large effect on the standard deviation. One possibility is to add more data
# for this case an additional dataset can be added to the Background provided from this website. This has the advantage that a more precise intermediate Background and standard deviation of 
# the machine rather than from one measurement run can be determined. If you do have enough Background measurements you should not use this additional dataset"""
# st.markdown(text_7)

# text_8 = """ If you want to use this increased dataset, check the Box below:"""
# st.markdown(text_8)

# st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
# col4, col5 = st.columns([1, 3])
# with col4:
#     checkbox_additional_BG_mes = st.checkbox(
#         'Add more BG measurements?', help='If you want to add more Background and HNO3 measurements to get a more precise machine Background tick the checkbox')

# if checkbox_additional_BG_mes == True and upload_excel is not None:
#     add_BG_mes = pd.read_excel(r'pages\additional_files\BG.xlsx')
#     del add_BG_mes['Messfile'], add_BG_mes['Messdatum']
#     st.success('More Background measurements will be added')
# st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

#st.markdown(input_file_marker_2, unsafe_allow_html=True)

# ---------------------------------------------------------------- Calculate Limit of Quantification

st.header(' 5. Limit of quantification ')

text9 = """ The limit of quantification (LOQ) is expressed as the smallest measurement that can be detected with 
reasonable certainty [IUPAC. Compendium of Chemical Terminology, 2nd ed. (the "Gold Book")]. This measurement is 
accepted to be the mean value (M) of the blank measuremnts or in our case the mean value of the BG and HNO3 where
the standard deviation (sd) multiplied by a factor is added. This factor is the confidence level (CL) that one wants to
achieve.
"""
st.markdown(text9)

st.latex(r'\mathrm{LOQ = M + CL * sd}')

text10 = """ For the calculation of the LOQ we use the intensity of the measurements. For every element that has
been measu#ED6363 we calculate the LOQ. If the intensity for the respective element of a sample is below the LOQ it won't
be used anymore. Consequently the concentration of the respective element of that specific sample will be discarded.
It is recommended to set the confidence level to the value of 6 but you can choose the confidence level freely.
"""
st.markdown(text10)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
confidence_level = st.number_input(
    'What value should the confidence level be', value=6)
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

# ---------------------------------------------------------------- Choose you Calibration

st.header('6. Calibration')

# text
text11 = """ Which calibraiton did you use? \n
- Standard calibration : BIR-1, BHVO-2, AGV-2, JB-2, BCR-2 \n
- Artificial calibration : Calib1, Calib2, Calib3, Calib4, Calib5, Calib6, Calib7, Calib8 \n
- Neither \n
If the reference materials or the names of the reference materials differ in your measurement session choose "Neither" \n \n
As you did by eye in the Qtegra software, the program now looks at the goodness of your calibraiton. Every calibration with
a calibration coefficient below 0.995 is conside#ED6363 as possible critical and every calibration coefficient below 0.990 as critical.
Especially major elements can have calibration coefficients below 0.990. Even though major element concentraitons at the University of Cologne
within low errors (~5%) equal to XRF-measurements, it shows that iCap soution measurements are not ideal to measure major element concentrations.
At least for trace element measurements recommend to discard calculated concentraitions that have calibrations coeffiecients belwo 0.990
and be careful with calibration that have coefficients between 0.995 and 0.990 (check reference materials). You can find the affected
calibrations after you download the Excel-file in the sheet "Evaluation".
"""
st.markdown(text11)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
# choose calib - input
choose_standard = st.radio('Which calibration did you use? Please choose one:',
                           ('Standard calibration', 'Artificial calibration', 'Neither'))
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

# what if choose standard
if choose_standard == 'Neither':

    text_11 = """<span style="color:#ECBC55"> 
    You choose neither. Please specify the names of the calibration that you used.
    Make sure that the names you add here, are the same as in the file. Separate the standards in the input box
    by a comma. \n Example: Standard1, Standard2, Standard3
    </style>"""
    st.markdown(text_11, unsafe_allow_html=True)
    calibration = st.text_input(
        'Add the name of the standards here', placeholder='Standard1, Standard2, Standard3')
    calibration = calibration.split(',')

elif choose_standard == 'Standard calibration':
    calibration = ['BIR-1', 'BHVO-2', 'AGV-2', 'JB-2', 'BCR-2']

elif choose_standard == 'Artificial calibration':
    calibration = ['Calib1', 'Calib2', 'Calib3',
                   'Calib4', 'Calib5', 'Calib6', 'Calib7', 'Calib8']

text_12 = f"""<span style="color:#ECBC55"> 
    You choose {choose_standard} = {calibration}.
    </style>"""
st.markdown(text_12, unsafe_allow_html=True)

if len(calibration) != 0:
    one_calib = calibration[0]


# ---------------------------------------------------------------- Blank
st.header('7. Name of the blank')

text12 = """ Add the name of ***one*** of your blanks. The blank that will find in the Excel sheet under "recommended concentrations" after the calculation in this program.
Is divided by 20.  <span style="color:#ECBC55"> Therefore the unit of the blank is in [ug].</style>"""

st.markdown(text12, unsafe_allow_html=True)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

blank_name = st.text_input('The name of the blank is:',
                           placeholder='Add blank name here')
text12 = f""" <span style="color:#ECBC55"> Your blank is: {blank_name} </style>"""
st.markdown(text12, unsafe_allow_html=True)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker


# ---------------------------------------------------------------- Relative Standard Deviation
st.header('8. Relative standard deviation of the concentration')

text14 = """ The concentrations of the iCap measurements are corrected to the intensity of the internal standard that you added to the sample. During intensity drift
of the iCap the internal standard elements and the analyte elements are shifted by the same amount. Therefore even though the total intensities changed relative to the 
calibration, by using a correction that adjusts the internal standard element intensity a sample to the internal standard element intensity of the calibration, it is still
possible to calulate the correct concentration of a analyte element. Consequently, large RSD of an analyte element means that the intensity of the analyte element
changed relative to the intensity of the internal standard element during the individual measurement cycles. Therefore the calculated cocentrations of the different measurement
cycles differ and subsequently the standard deviation and as well the relative standard deviation. This can happen especially when the concentration of the analyte element
is very low within on sample, leading to a larger error in the analyte element intensity relative the higher-concentrated internal standard element intensity.
Therefore it is advised to delete concentration calculations of samples that have high RSD. It is recommended to delete concentration with RSD higher than 10%.
You can set the cut-off value to lower values. However this can as well lead to the possiblity that sampels with lower concentrations, that have a tendency to
have higher RSD (6-10%) are not conside#ED6363 as "recommended values". """

st.markdown(text14, unsafe_allow_html=True)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
RSD_cutoff = st.number_input('What is your RSD-cutoff percentage?', value=10)
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

text15 = """ <span style="color:#ECBC55"> 
Word of advise: \n
Check independtly from this recommendation if elements where low concentrations are often observed (In, Cd, Tl, W, Ta) if RSD might be produced by 
a single measurement cycle within a sample measurement. These can be deleted as well in Qtegra. Alternatively, check if your referece material
with similar low concentratrions is similar to the accepted reference values.
</style>"""

st.markdown(text15, unsafe_allow_html=True)


# ---------------------------------------------------------------- Too low concentrations
st.header('9. Very low concentrations')

text16 = """ Even though with the RSD_cutoff most of the samples with very low concentrations will be filte#ED6363 out, it can happen that some samples will persist in the
data table. One reason might be that the value was correctly measu#ED6363 another might be that the sample was repeatedly measu#ED6363 at the same conditions. This does not
mean that the calculated concentration is necessarily correct, it just means that there was no change of the intensity of the analyte element relative to the 
internal standard element. However, it is known and often observed that low-abundance elements (W,Th,HSE,Tl,In,Cd) are problematic to measure even more if they
are exceptionally deplteded in some samples (see examples below). It is therefore recommended to discard measurements of samples belwo a certain concentraton.
Here we recommend 15 ng/g (=15 ppb). However you can choose freely where to set the concentration-cutoff. If you do not want to filter for low concentrations,
set the concentration-cutoff = 0"""
st.markdown(text16, unsafe_allow_html=True)

st.image(path +'/images/plots.png', caption="MORB data from Jenner and O'Neill 2012 (G-Cubed). Differences in W/Th and Nb/Ta ratios are espcecially observed for very low W and Ta concentrations")

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
ppb_cutoff = st.number_input('Concentration-cut off in ng/g (=ppb):', value=15)
st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker

text17 = """ <span style="color:#ECBC55"> 
Word of advise: \n
Keep in mind that low concentration tend to be erronous at ICP-MS measurements but to not have to. You should check with reference materials that have
similar enrichments
</style>"""

st.markdown(text17, unsafe_allow_html=True)

# ---------------------------------------------------------------- Round to significant digits
st.header('10. Round to significant digits')


st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker
significant_dig_quest = st.checkbox('Should we round the concentration to significant digits?', value=True)
if significant_dig_quest == True:
    significant_digits = st.number_input('How many significant digits do you want', value=3, step=1)

st.markdown(input_file_marker_1, unsafe_allow_html=True)  # input field marker


# ---------------------------------------------------------------- Filter and download
st.header('10. Calculation and download')
text18 = """ To evaluate the data click the "Evaluation" button. If there are no problems with the file or your inputs you should be able to download
your evaluted file. In that fill you will find multiple sheets:
- ***Recommended concentration*** : The recommended concentrations for your samples after filtering with your input
- ***Evaluation*** : All the samples and elements that were not used in the "Reccomended concentration" file and the reason as well as the evalution of the calibration coefficients
- ***Intensity cps*** : Intensity of the elements in cps
- ***Intensity RSD*** : RSD of the uncorrected intensity in % (optional, based on the input file)
- ***Concentration ppm*** : Concentration of the corrected intensities in ug/g (=ppm)
- ***Concentration sd*** : Standard deviation of the corrected concentration in ug/g (=ppm) (optional, based on the input file)
- ***Concentration RSD*** : Relative standard deviation of the corrected concentration in %
- ***Calibration coefficient*** : Calibration coefficient of the individal calibrations
"""
st.markdown(text18, unsafe_allow_html=True)

st.subheader('10.1 Evaluation')
 
evaluate_quest = st.button('To evaluate your file click here', help='If you filled out all the input fields you can evaluate your datafram by clickgin')

if evaluate_quest == True:
    if upload_excel == None:
        st.error('You forgot to upload a file')
    elif BG_name == "": # check BG_names
        st.error('You forgot to add your Background name')
    elif calibration == [""]: # check calibrations
        st.error('You forgot to add your calibrations')
    elif blank_name == "": # check calibrations
        st.error('You forgot to add your blank. If you dont have a blank write "None"')
    else:
        df = del_ycps(df)
        df_cps, df_cps_RSD, df_conc, df_ugg_SD, df_conc_RSD, df_calib_coef = subsheets(df)
        # DEPRECATED REASON SEE ABOVE
        # if checkbox_additional_BG_mes == True:
        #     df_cps = pd.concat([df_cps, add_BG_mes]).reset_index(drop=True)
        #     st.success('Additional Backgrounds were added successfully')
        
        df_cps_raw = df_cps.copy() # df cps with all dasta
        mean_val_BG_df, clean_df_cps = calc_background_cps(df_cps, name_of_BG = BG_name, name_of_wash = HNO3_name, Z_score_outlier = BG_outlier_num)
        
        calibration.append(BG_name)
        calibration.append(HNO3_name)
        df_ugg_recomend, problem_df, df_cps_raw, df_conc, df_conc_RSD = filter_for_qualitiy_data (df_cps_raw, mean_val_BG_df, df_conc_RSD, df_conc, df_calib_coef, blank_name, one_calib, multiplicity_BG = confidence_level, cut_off_RSD = RSD_cutoff, cut_off_ppb = ppb_cutoff, calib_BG_HNO3_names=calibration)
        st.success('Calculation was successful - prepare file for download')
        
                # round digits
        
        if significant_dig_quest == True:
            with st.spinner('Rounding digits and prepare for download - this can take few minutes'):

                # round to decimal
                df_cps_raw = df_cps.round(0)
                df_background = clean_df_cps.round(0)

                
                # Simple round not working because of float64 - use improved rounding
                for i in df_conc_RSD.drop(columns = ['Order', 'Sample']):
                    df_conc_RSD[i] = df_conc_RSD[i].astype(float).round(1)
                for i in df_cps_RSD.drop(columns = ['Order', 'Sample']):
                    df_cps_RSD[i] = df_cps_RSD[i].astype(float).round(1)
                    
                    
                # round to significant digits
                for i in df_conc.drop(columns=['Order', 'Sample']):
                    for j in range(len(df_conc[i])):
                        if np.isnan(df_conc[i][j]) == False:
                            df_conc[i][j] = round(df_conc[i][j], (significant_digits - 1) - int(floor(log10(abs(df_conc[i][j])))))
                        else:
                            pass
                for i in df_ugg_SD.drop(columns=['Order', 'Sample']):
                    for j in range(len(df_ugg_SD[i])):
                        if np.isnan(df_ugg_SD[i][j]) == False:
                            df_ugg_SD[i][j] = round(df_ugg_SD[i][j], (significant_digits - 1) - int(floor(log10(abs(df_ugg_SD[i][j])))))
                        else:
                            pass
                for i in df_ugg_recomend.drop(columns=['Order', 'Sample']):
                    for j in range(len(df_ugg_recomend[i])):
                        if np.isnan(df_ugg_recomend[i][j]) == False:
                            df_ugg_recomend[i][j] = round(df_ugg_recomend[i][j], (significant_digits - 1) - int(floor(log10(abs(df_ugg_recomend[i][j])))))
                        else:
                            pass
        else:
            pass
        
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            
            df_ugg_recomend.to_excel(writer, sheet_name='Recommended data')
            problem_df.to_excel(writer, sheet_name='Evaluation')
            clean_df_cps.to_excel(writer, sheet_name='BG_HNO3_only')
            df_cps_raw.to_excel(writer, sheet_name='Intensity cps')
            df_cps_RSD.to_excel(writer, sheet_name='Intensity RSD')
            df_conc.to_excel(writer, sheet_name='Concentrations ppm')
            df_ugg_SD.to_excel(writer, sheet_name='Concentration sd ppm')
            df_conc_RSD.to_excel(writer, sheet_name='Concentration RSD')
            df_calib_coef.to_excel(writer, sheet_name='Calibration coef')       

            writer.close()
            
            st.download_button(
                label="Download Excel worksheet",
                data=buffer,
                file_name="Evaluated_iCap_data.xlsx"
            )        


# Variables:

# col7 - last column
# blank_name - name of the blank as str
# RSD_cutoff - percentage
# calibration = list with calibration names
# one_calib = first calibration
# confidence_level - factor to calculate Limit of quantification
# BG_name - name of the Background
# HNO3_name - name of the HNO3
# add_BG_mes - additional background measurements to precisely measure Background
# BG_otlier_num - every BG below mean +- BG_otlier_num * sd will be deleted



# ---------------------------------------------------------------- Add BG from file to sto#ED6363 BG file - UNIFINISHED
#
# text_8 = """ To further improve this dataset we would like to add the Background and HNO3 measurements of your dataset to this large Background dataset.
# If it is okay for you to add your Background data to the combined Background dataset please tick the Box below. Only your the data with the BG and HNO3 names
# that you stated above will be added to this dataset not any other data!"""
# st.markdown(text_8)
#
# SHOW df where only BG and HNO3 measurements are shown - which is later added to the other background measurements
#
# checkbox_export_BG = st.checkbox('Export your BG/HNO3 data to the large datset?', help='If you want to add your Background and HNO3 measurements to the big BG/HNO3 dataset tick the checkbox')
#
# build filter for Background data that is already in the dataframe
# Add a column where the name of the Excel file is sto#ED6363 next to the BG measurement
# MAKE SURE THAT BEFORE YOU ADD THE LARGE STO#ED6363 DATASET TO THE SMALL DATASET TO CALCULATE THE ICAP MEASUREMENTS DELETE COLUMN WITH THE NAME OF THE EXCEL FILE
# ALSO MAKE SURE THAT BEFORE YOU ADD THE MEASUREMENT DATASET TO THE LARGE DATASET DELETE OUTLIER AND ADD THE COLUMN WITH THE NAME OF THE EXCEL FILE



# ---------------------------------------------------------------- Last advies
st.header('11. Last advises')

text19 = """ Even after the calculation of the recommended values you should consider further evaluating your file the following way:

- ***Multiple measuremnts***: If you did multiple measurements of the same samples during one measurement session, 
    compare the relative difference in % for the same samples. Offsets higher than 6-8% show a systematic problem during measurement.
    ***You should remeasure the samples*** to find out which concentration is correct. Until then don't use the concentrations or at least
    use the mean value of the measurement.
    
- ***Reference materials***: As above, calculate the relative offset in % for you measurement and the accepted reference values.
    Offsets higher than 6-8% might indicate a measurement problem or a problem during digestion. For now don't worry. If you as well see
    offsets for the multiple measurements (see above) for the same elements you should consider discarding the element. There might be a 
    systematic error during measurement. Alternatively, remeasure your samples and see if the offset persists. If the offset is higher than
    15% it is recommended to find out if the offset is due to a digestion or measurement problem. Remeasure some of the accessible reference
    materials and see if the offset only occurs in your or in all measurements. If the offset only occurs in your measurement, it is likely
    a digestion problem of your reference material else you should consider not to use the calculated element concentrations for you samples
    ***You should remasure the samples*** to find out which concentration is correct. Until then don't use the concentrations or at least
    use the mean value of the measurement.

- ***Mean values - for multiple measurement***: If you did multiple measurements on single samples and you carefully screened for possible
    false values, you can now calulate mean values of your measurements.

"""
st.markdown(text19, unsafe_allow_html=True)



