import pandas as pd
import numpy as np

def transpose_Neptune_To_Excel (df, element, export_name):
    
    # ------------------------------------------------------ nested functions
    
    def del_duplicates_list(a_list): # a function to delete duplicates in a list
        return list(dict.fromkeys(a_list))
    
    def append_empty_row(df): # a function that appends an empty row at the end of a dataframe
        empty_list = []
        column_names = []
        for i in df:
            empty_list.append(np.nan)
            column_names.append(i)
            
        empty_row = pd.Series(empty_list, index=column_names)
        df = pd.concat([df,empty_row.to_frame().T]).reset_index(drop=True)
        return df
    
    # ------------------------------------------------------ start function
    
    # find all files that are inside the dataframe
    file_names = del_duplicates_list(list(df['Source.Name']))
    
    # make a loop that makes subdataframes based on the file names = 'Source.Names'
    
    list_pandas = [] # list with all df

    for i in file_names:
        df_copy = df[df['Source.Name']==i].copy().reset_index(drop=True)
        list_pandas.append(df_copy)
        del df_copy
        
    # change the header of the subdataframes - isotopes should be column names
    for i in range(len(list_pandas)):
        list_pandas[i].columns = list_pandas[i].iloc[22]
        
    # drop the first 20 rows that are not needed of the individual subdataframes
    for i in range(len(list_pandas)):
        list_pandas[i] = list_pandas[i].drop(list_pandas[i].index[0:23]).reset_index(drop = True)
    
    # drop the last 13 rows with mean, error, sd etc.
    for i in range(len(list_pandas)):
        list_pandas[i] = list_pandas[i].drop(list_pandas[i].index[60:73]).reset_index(drop = True)
        
    # The first column header is the name of the file, the full collumn is the name of the file
    # This would be problematic once the files will be concated
    # Add a column with the name 'Sample' inside the column is the name of the file
    # Delete the column with the file name keep the column with 'Sample'
    for i in range(len(list_pandas)):
        name = str(list_pandas[i].columns[0])
        list_pandas[i]['Sample'] = list_pandas[i][name]
        list_pandas[i]=list_pandas[i].drop(columns = [name])
    
    # Build final dataframe
    df_starter = list_pandas[0]

    for i in range(len(list_pandas[1:])):
        df_starter = append_empty_row(df_starter)
        df_starter = pd.concat([df_starter, list_pandas[i+1]]).reset_index(drop=True)

    # ------------------------------------------------------- add the different Elements
    if element == 'W':
        final_list_names = [ "Sample", "Cycle", "Time", "177Hf", "178Hf", "180W", "181Ta", "182W", "183W", "184W", "186W", "188Os",
                            "180W/184W (1)", "182W/184W (2)", "183W/184W (3)", "186W/184W (4)", "180W/183W (5)", "182W/183W (6)",
                            "184W/183W (7)", "186W/183W (8)", "177Hf/184W (9)", "181Ta/184W (10)", "188Os/184W (11)", 
                            "177Hf/183W (12)", "181Ta/183W (13)", "188Os/183W (14)" ]
    elif element == 'Mo':
        final_list_names = ["Sample", "Cycle", "Time", "91Zr", "92Mo", "94Mo", "95Mo", "96Mo", "97Mo", "98Mo", "99Ru", "100Mo"]
    else:
        return NotImplementedError
    # ------------------------------------------------------- add the different Elements
    
    # ------------------------------------------------------- convert string to numbers
    
    df_final = df_starter[final_list_names]
    
    for i in final_list_names[3:]:
        df_final[i] = df_final[i].astype(np.float64)
    
        
    # Transpose final df
    df_final = df_final.transpose()
    
    return df_final