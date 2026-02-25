import pandas as pd
import numpy as np
import traceback
import warnings
from math import floor, log10
import streamlit as st



# ----------------------------------------------------------------  delete row where "Y (cps)" and similar ist written
def del_ycps(df):

    try:
        row_nums = df.shape[0]
        l = 0

        # find location with row you want to delete by searching for element
        for i in range(1, row_nums):

            if 'Y (cps)' in df.iloc[i-1: i].values or 'Y (%)' in df.iloc[i-1: i].values or 'Y (µg/g)' in df.iloc[i-1: i].values:
                df = df.drop(i-1).reset_index(drop=True)
                st.success("""Y(cps) row was deleted""")
                return df  # return dataframe
            else:
                pass


    except Exception:
        st.error(""" An error occured during function "iCap_Mes_Evaluation""")
        traceback.print_exc()

# ----------------------------------------------------------------  Preparep subsheets and clean from uneccesary strings, zeros, and colums

def subsheets(df):
    cps = ['SampleList', 'SampleList.1']
    cps_RSD = ['SampleList', 'SampleList.1']
    ugg = ['SampleList', 'SampleList.1']
    ugg_SD = ['SampleList', 'SampleList.1']
    ugg_RSD = ['SampleList', 'SampleList.1']
    calib_coef = ['SampleList', 'SampleList.1']

    try:
        # make subsheets
        for i in df:
            if 'Raw.Average' in str(i):
                cps.append(i)
            elif 'Raw.RSD' in i:
                cps_RSD.append(i)
            elif 'ExtCal.Average' in i:
                ugg.append(i)
            elif 'ExtCal.STD' in i:
                ugg_SD.append(i)
            elif 'ExtCal.RSD' in i:
                ugg_RSD.append(i)
            elif 'ExtCal.CorrelationCoefficient' in i:
                calib_coef.append(i)
            else:
                pass

        df_cps = df[cps]
        df_cps_RSD = df[cps_RSD]
        df_ugg = df[ugg]
        df_ugg_SD = df[ugg_SD]
        df_ugg_RSD = df[ugg_RSD]
        df_calib_coef = df[calib_coef]

        name_list = ['CPS', 'CPS RSD', 'ugg', 'ugg sd',
                        'ugg RSD', 'Calibration coefficient']
        sheet_list = [df_cps, df_cps_RSD, df_ugg,
                        df_ugg_SD, df_ugg_RSD, df_calib_coef]

        for i in range(len(sheet_list)):
            if sheet_list[i].shape[1] == 2:

                st.error(f"""{name_list[i]} cannot be evaluated. There is no {name_list[i]} data in the file""")

        # adjust subsheets
        # adjust names
        # delete columns that are not needed
        for i in range(len(sheet_list)):

            sheet_list[i].columns = sheet_list[i].iloc[1]
            sheet_list[i] = sheet_list[i].drop(
                [0, 1]).reset_index(drop=True)
            sheet_list[i] = sheet_list[i].replace(0, np.nan)
            sheet_list[i] = sheet_list[i].replace('N/A', np.nan)
            sheet_list[i] = sheet_list[i].replace('#ZAHL!', np.nan)
            if '103Rh (mp_KED-He)' in sheet_list[i]:
                sheet_list[i] = sheet_list[i].drop(
                    columns=['103Rh (mp_KED-He)'])
            if '103Rh (mp_STD)' in sheet_list[i]:
                sheet_list[i] = sheet_list[i].drop(
                    columns=['103Rh (mp_STD)'])
            if '187Re (mp_KED-He)' in sheet_list[i]:
                sheet_list[i] = sheet_list[i].drop(
                    columns=['187Re (mp_KED-He)'])
                # delete 206Pb and 207Pb in cps frames, is okay since 208 has highest abundance from the others
            if '206Pb (mp_KED-He)' in sheet_list[i]:
                sheet_list[i] = sheet_list[i].drop(
                    columns=['206Pb (mp_KED-He)'])
            if '207Pb (mp_KED-He)' in sheet_list[i]:
                sheet_list[i] = sheet_list[i].drop(
                    columns=['207Pb (mp_KED-He)'])

        sheet_list[5] = sheet_list[5].dropna()

        st.success(f"""                    
                    Subsheets were created, strings and zeros were transformed to np.nan.
                    Collumns with 103Rh (mp_KED-He), 103Rh (mp_STD), 187Re (mp_KED-He),
                    206Pb (mp_KED-He), 207Pb (mp_KED-He) are not needed for evaluation and therefore deleted.
                    """)
        return sheet_list

    except Exception:
        st.error(f"""An error occured during function "subsheets" """)
        traceback.print_exc()

# ---------------------------------------------------------------- calc background cps 
def calc_background_cps(df_cps, name_of_BG : str = 'BG', name_of_wash : str= 'HNO3', Z_score_outlier : float = 1.5):
    
    if name_of_BG not in list(df_cps['Sample']):

        return st.error(f"""ERROR: An error occured during function "calc_background_cps", the name "{name_of_BG}" is not in the Excel sheet'""")
    else:
        pass
    
    if name_of_wash not in list(df_cps['Sample']):
        
        st.error(f"""The name "{name_of_wash}" is not in the Excel sheet""")
    else:
        pass
    
    
    # prepare subsheet with background and HNO3 measurements
    df_cps = df_cps[((df_cps['Sample']== name_of_BG) | (df_cps['Sample']== name_of_wash))].reset_index(drop=True)
    df_cps = df_cps.round(0)
    df_cps = df_cps.replace(0, np.nan)
    
    # filter for BG outlier
    try:
        for i in df_cps.drop(columns=['Order', 'Sample']):
            mean = np.mean(df_cps[i])
            sd = np.std(df_cps[i])
            
            #z-score = (mean - measurement) / standard deviation
            
            for j in range(len(df_cps[i])):
                # calc z-score
                z_score_sample = ((df_cps[i][j] - mean )/sd)
                
                if z_score_sample >  Z_score_outlier or z_score_sample < ((-1) *Z_score_outlier)  :
                    df_cps[i][j] = np.nan
    except Exception:

        st.error(f""" An error occured during function "calc_background_cps" while filtering outliers within BG/HNO3 """)
        traceback.print_exc()
        
    # calc mean and sd
    try:
        df_cps_copy = df_cps.copy()
        df_cps_copy = df_cps_copy.replace([name_of_BG, name_of_wash],np.nan)
        df_cps_mean = pd.Series(dict(df_cps_copy.mean()))        
        df_cps_mean['Sample'] = 'Mean'
        df_cps_mean['Order'] = 'Mean'
        df_cps_sd = pd.Series(dict(df_cps_copy.std()))
        df_cps_sd['Sample'] = 'Standard deviation'
        df_cps_sd['Order'] = 'Standard deviation'
        

        st.success(f""" Mean value and standard deviation for Backgrounds were calculated after filtering. """)
            
            
        #add mean and sd to df_cps
        df_cps = pd.concat([df_cps, df_cps_mean.to_frame().T, df_cps_sd.to_frame().T] ).reset_index(drop=True)
        background_calc_df_cps = df_cps[((df_cps['Sample']=='Mean') | (df_cps['Sample']=='Standard deviation'))].reset_index(drop=True)
        return [background_calc_df_cps, df_cps]
    except Exception:
        st.error(f"""  An error occured during function "calc_background_cps" while trying to build BG/HNO3 dataframe """)
        traceback.print_exc()
        
        
    

# ---------------------------------------------------------------- filter for quality data - delete non quality data
def filter_for_qualitiy_data (df_cps, background_mean_sd_df, df_conc_RSD, df_conc, df_calib_coef, name_blank: str, name_one_calib : str, multiplicity_BG : int = 6, cut_off_RSD : float = 10, cut_off_ppb : int = 15, calib_BG_HNO3_names=['BG','HNO3','BIR-1','JB-2','BHVO-2','BCR-2', 'AGV-2']):
    
    # Trace elements and samples that are below the quality values
    Problem_step =[]
    Problematic_element = []
    Problematic_sample = []

    if df_cps.shape[1] != background_mean_sd_df.shape[1] or df_conc.shape[1] != background_mean_sd_df.shape[1]:
        return st.error(f""" ERROR: the CPS, Conc, and Background data have not the same amount of columns.
                            One of the datasets misses elements""")
        
    # prepare df with blank
    blank_df = df_conc[df_conc['Sample']== name_blank].reset_index(drop = True)
    
    # prepare reccomended conc
    df_ugg_recomend = df_conc.copy()
    
    # prepare mean and sd df
    mean_df = background_mean_sd_df[background_mean_sd_df['Sample']=='Mean'].reset_index(drop=True)
    sd_df = background_mean_sd_df[background_mean_sd_df['Sample']=='Standard deviation'].reset_index(drop=True)

    try:
        # Filter for Quantification limit
        # delete concentrations that are below quantification limit
        for i in background_mean_sd_df.drop(columns=['Sample','Order']):
            # calc mean + multiplicity * standard deviation
            filter_val = mean_df[i][0] + multiplicity_BG * sd_df[i][0]
            for j in range(len(df_ugg_recomend[i])):
                if df_cps[i][j] < filter_val: # Quantification limit ist bigger than cps of sample then make conc in recommended_df to nan
                    # make a list with comments to know what was done
                    if df_ugg_recomend['Sample'][j] != 'BG' and df_ugg_recomend['Sample'][j] != 'HNO3':
                        Problem_step.append('Below Background - conc. deleted')
                        Problematic_element.append(i)
                        Problematic_sample.append(df_ugg_recomend['Sample'][j])
                    df_ugg_recomend[i][j] = np.nan

                else: pass
                
        st.success(f' All samples below the quantification limit (= mean + {multiplicity_BG} * sd) were filtered out')
    except Exception:
        raise
        st.error('An error occured during function "filter_for_qualitiy_data" while trying delete samples below quantification limit')
        
        
        
    
    try:
    # Filter for ugg_RSD
        for i in df_conc_RSD.drop(columns=['Sample','Order']):
            for j in range(len(df_ugg_recomend[i])):
                if df_conc_RSD[i][j] > 6 and df_conc_RSD[i][j] < cut_off_RSD:
                    if df_ugg_recomend['Sample'][j] != 'BG' and df_ugg_recomend['Sample'][j] != 'HNO3':
                            Problem_step.append('RSD above 6% - careful')
                            Problematic_element.append(i)
                            Problematic_sample.append(df_ugg_recomend['Sample'][j])
                if df_conc_RSD[i][j] > cut_off_RSD: # realtive error is higher than cut_off_RSD - delete
                    # make a list with comments to know what was done
                    if df_ugg_recomend['Sample'][j] != 'BG' and df_ugg_recomend['Sample'][j] != 'HNO3':
                        Problem_step.append(f'RSD above {cut_off_RSD} - deleted')
                        Problematic_element.append(i)
                        Problematic_sample.append(df_ugg_recomend['Sample'][j])
                    # make samples with RSD higher than cut_off_RSD to nan
                    df_ugg_recomend[i][j] = np.nan

                else: pass
        st.success(f"""All samples with RSD above {cut_off_RSD} were filtered out""")
    except Exception:
        st.error(f"""An error occured during function "filter_for_qualitiy_data" while trying delete samples with high""")
        
        traceback.print_exc()
            
    try:  
        # delete samples with concentrations beleow 15ppb
        for i in df_ugg_recomend.drop(columns=['Sample','Order']):
            for j in range(len(df_ugg_recomend[i])):
                if df_ugg_recomend[i][j] < (cut_off_ppb/1000): # concentration is very low
                    # make a list with comments to know what was done
                    if df_ugg_recomend['Sample'][j] != 'BG' and df_ugg_recomend['Sample'][j] != 'HNO3':
                        Problem_step.append(f'Concentration below {cut_off_ppb} ppb - deleted')
                        Problematic_element.append(i)
                        Problematic_sample.append(df_ugg_recomend['Sample'][j])
                    # make samples with ppb lower than cut_off_ppb deleted
                    df_ugg_recomend[i][j] = np.nan
        st.success(f"""All samples with ppb belwo {cut_off_ppb} were filtered out""")
    except Exception:
        st.error(f""" An error occured during function "filter_for_qualitiy_data" while trying delete samples with low ppb """)
        traceback.print_exc()
        
            
    calib_BG_HNO3_names.append(name_blank)
    

    # delete calibratons HNO3 and BG in recommended_df, in standard dev conc in RSD conc
    for i in calib_BG_HNO3_names:
        df_ugg_recomend = df_ugg_recomend[df_ugg_recomend['Sample'] != i].reset_index(drop=True)
        df_conc_RSD = df_conc_RSD[df_conc_RSD['Sample'] != i].reset_index(drop=True)
        

    # delete problems for HNO3, BG, and calibration
    problem_dict = dict({'Filter':Problem_step,'Element':Problematic_element,'Samples':Problematic_sample})
    problem_df_1 = pd.DataFrame(problem_dict)

    for i in calib_BG_HNO3_names:
        problem_df_1 = problem_df_1[problem_df_1['Samples'] != i].reset_index(drop=True)
        

    # empty problem lists
    Problem_step =[]
    Problematic_element = []
    Problematic_sample = []
    try:
        # evaluate calibration coefficient
        df_calib_coef = df_calib_coef[df_calib_coef['Sample'] == name_one_calib].reset_index(drop=True)
        for i in df_calib_coef.drop(columns=['Sample','Order']):
            for j in range(len(df_calib_coef[i])):
                if df_calib_coef[i][j] < 0.995 and df_calib_coef[i][j] > 0.990:
                    Problem_step.append(f'Calibration {j+1} is below 0.995 be careful')
                    Problematic_element.append(i)
                if df_calib_coef[i][j] < 0.990:
                    Problem_step.append(f'Calibration {j+1} is below 0.990 dont use this calibration and the samples that were calculated with it')
                    Problematic_element.append(i)

    except Exception:
        st.error(f"""An error occured during function "filter_for_qualitiy_data" while trying evaluate calibration coefficient""")

        traceback.print_exc()

    #again make df
    problem_dict = dict({'Filter':Problem_step,'Element':Problematic_element})
    problem_df_2 = pd.DataFrame(problem_dict)
    
    problem_df = pd.concat([problem_df_1 ,problem_df_2]).reset_index(drop=True)
    problem_df = problem_df.sort_values(['Filter', 'Samples']).reset_index(drop=True)
    df_ugg_recomend = pd.concat([df_ugg_recomend, blank_df]).reset_index(drop=True)
    
    return [df_ugg_recomend, problem_df, df_cps, df_conc, df_conc_RSD]
