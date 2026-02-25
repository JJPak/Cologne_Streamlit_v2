import pandas as pd

def crunch_neoma_data(df, isotope_system ):


    # define all the elements that can be processed

    Element = ['Hf','Nd', 'Cd']

    Raw_data_list = [
        ['173Yb Static 1', '174Hf Static 1', '175Lu Static 1', '176Hf Static 1', '177Hf Static 1', '178Hf Static 1', '179Hf Static 1', '180Hf Static 1', '181Ta Static 1', '183W Static 1', '177Hf.O Static 1',
                '178Hf/177Hf', '179Hf/177Hf', '173Yb/177Hf', '175Lu/177Hf', '181Ta/177Hf', '183W/177Hf', '173Yb/176Hf monitor', '175Lu/176Hf monitor',
                '174Hf/177Hf MB+I', '176Hf/177Hf MB+I', '180Hf/177Hf MB+I', '177Hf.O/177Hf'],
        
        ['150Nd Static 1', '149Sm Static 1', '148Nd Static 1', '147Sm Static 1', '146Nd Static 1', '145Nd Static 1', '144Nd Static 1', '143Nd Static 1', '142Nd Static 1', '140Ce Static 1', '142Nd.O Static 1', 
        '142Nd/144Nd', '143Nd/144Nd', '145Nd/144Nd', '146Nd/144Nd', '148Nd/144Nd', '150Nd/144Nd', '140Ce/144Nd', '140Ce/142Nd', '147Sm/144Nd', '142Nd/140Ce', '144Nd/147Sm', '148Nd/147Sm', '150Nd/147Sm'],

        ['105Pd Static 1', '106Cd Static 1', '108Cd Static 1', '110Cd Static 1', '111Cd Static 1', '112Cd Static 1', '113Cd Static 1', '114Cd Static 1', '115In Static 1', '116Cd Static 1', '118Sn Static 1',
        '105Pd/114Cd', '106Cd/114Cd', '108Cd/114Cd', '110Cd/114Cd', '111Cd/114Cd', '112Cd/114Cd', '113Cd/114Cd', '115In/114Cd', '116Cd/114Cd', '118Sn/114Cd'],

                    ]

    Interference_data_list = [
        ['174Hf Static 1', '176Hf Static 1', '180Hf Static 1'],

        ['142Nd Static 1', '144Nd Static 1', '148Nd Static 1', '150Nd Static 1'],

        ['106Cd Static 1','110Cd Static 1', '113Cd Static 1', '108Cd Static 1', '112Cd Static 1', '114Cd Static 1', '115In Static 1', '116Cd Static 1'],
    ]
    
    Mass_bias_data_list = [
        ['178Hf/177Hf', '179Hf/177Hf', '173Yb/177Hf', '175Lu/177Hf', '181Ta/177Hf', '183W/177Hf', '173Yb/176Hf monitor', '175Lu/176Hf monitor',
                '174Hf/177Hf MB+I', '176Hf/177Hf MB+I', '180Hf/177Hf MB+I', '177Hf.O/177Hf'],

        ['143Nd/144Nd MB+I', '148Nd/144Nd MB+I', '150Nd/144Nd MB+I'],

        ['105Pd/114Cd', '106Cd/114Cd', '108Cd/114Cd', '110Cd/114Cd', '111Cd/114Cd', '112Cd/114Cd', '113Cd/114Cd', '115In/114Cd', '116Cd/114Cd', '118Sn/114Cd'],
    
    ]

##################################################################################

    if isotope_system not in Element:
        print('Error: Element not found in the list')
        return None

    # find index of the chosen element
    index = Element.index(isotope_system)

    # choose the measured elements for the chosen element
    list_measured = Raw_data_list[index]

###################################################################################

    # # prepare the dataframe for easier manipulation
    
    df.iloc[0,0] = 'Type'
    df.iloc[0,1] = 'Useless1'
    df.iloc[0,2] = 'Elements'
    df.iloc[0,3] = 'Useless2'
    
    
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    
    df = df.drop(columns=['Useless1','Useless2']) # drop rows with NaN in Elements column

#################################################################################

    # prepare 3 separate data frames for raw, interference, and mass bias data
    
    raw_df_one = df[(df['Type'] == 'Sample Raw Data Averager')]
    raw_df_two = df[(df['Type'] == 'Ratios:Ratio Averager')]
    raw_df = pd.concat([raw_df_one, raw_df_two]).reset_index(drop=True)
    
    interference_corr_df = df[(df['Type'] == 'Interference Correction:Interference Correction Averager')].reset_index(drop=True)
    
    mb_and_i_corr_df = df[(df['Type'] == 'Internal Mass Bias Correction:Internal Mass Bias Correction Averager')].reset_index(drop=True)



###################################################################################

    # filter raw df
    
    
        # make a list with the rows that are needed

    order_list_raw = [] # list for average values and se values
    for i in Raw_data_list[index]:
        average_val_string = i+' Mean'
        order_list_raw.append(average_val_string)

    for i in Raw_data_list[index]:
        average_val_string = i+' SE'
        order_list_raw.append(average_val_string)

        # only take out the rows that are needed which are the averages and the 1se row

        # Create a dummy df with the required list and the col name to sort on
    dummy1 = pd.Series(order_list_raw, name = 'Elements').to_frame()
        # Use left merge on the dummy to return a sorted df
    sorted_df1 = pd.merge(dummy1, raw_df, on = 'Elements', how = 'left')
    raw_df = sorted_df1

###################################################################################

    # filter interference df


        # make a list with the rows that are needed

    order_list_interference = [] # list for average values and se values
    for i in Interference_data_list[index]:
        average_val_string = i+' Mean'
        order_list_interference.append(average_val_string)

    for i in Interference_data_list[index]:
        average_val_string = i+' SE'
        order_list_interference.append(average_val_string)

        # only take out the rows that are needed which are the averages and the 1se row

        # Create a dummy df with the required list and the col name to sort on
    dummy2 = pd.Series(order_list_interference, name = 'Elements').to_frame()
        # Use left merge on the dummy to return a sorted df
    sorted_df2 = pd.merge(dummy2, interference_corr_df, on = 'Elements', how = 'left')
    interference_corr_df = sorted_df2


###################################################################################

    # filter mass bias df


        # make a list with the rows that are needed

    order_list_massbias = [] # list for average values and se values
    for i in Mass_bias_data_list[index]:
        average_val_string = i+' Mean'
        order_list_massbias.append(average_val_string)

    for i in Mass_bias_data_list[index]:
        average_val_string = i+' SE'
        order_list_massbias.append(average_val_string)

        # only take out the rows that are needed which are the averages and the 1se row

        # Create a dummy df with the required list and the col name to sort on
    dummy3 = pd.Series(order_list_massbias, name = 'Elements').to_frame()
        # Use left merge on the dummy to return a sorted df
    sorted_df3 = pd.merge(dummy3, mb_and_i_corr_df, on = 'Elements', how = 'left')
    mb_and_i_corr_df = sorted_df3



###################################################################################

    # drop type column from all dataframes
    
    
    raw_df = raw_df.drop(columns=['Type'])
    interference_corr_df = interference_corr_df.drop(columns=['Type'])
    mb_and_i_corr_df = mb_and_i_corr_df.drop(columns=['Type'])


####################################################################################

    # transpose raw dataframe make new header and calculate the 1se % for each element

    # transpose dataframe and make new header

    raw_df = raw_df.transpose()
    new_header = raw_df.iloc[0] #grab the first row for the header
    raw_df = raw_df[1:] #take the data less the header row
    raw_df.columns = new_header #set the header row as the raw_df header

    # transfer all numbers that are string to float in dataframe
    raw_df = raw_df.apply(pd.to_numeric, errors='coerce')
    

    # Calculate the 1se % for each element

    for i in Raw_data_list[index]:
        raw_df[i+' 1SE %'] = (raw_df[i+' SE'] / raw_df[i+' Mean']) * 100
        
    # drop all columns except Mean and 1SE %

    for i in Raw_data_list[index]:
        raw_df = raw_df.drop(columns=[i+' SE'])


    
####################################################################################

    # transpose interference data frame make new header and calculate the 1se % for each element

    # transpose dataframe and make new header

    interference_corr_df = interference_corr_df.transpose()
    new_header = interference_corr_df.iloc[0] #grab the first row for the header
    interference_corr_df = interference_corr_df[1:] #take the data less the header row
    interference_corr_df.columns = new_header #set the header row as the interference_corr_df header

    # transfer all numbers that are string to float in dataframe
    interference_corr_df = interference_corr_df.apply(pd.to_numeric, errors='coerce')
    

    # Calculate the 1se % for each element

    for i in Interference_data_list[index]:
        interference_corr_df[i+' 1SE %'] = (interference_corr_df[i+' SE'] / interference_corr_df[i+' Mean']) * 100
        
    # drop all columns except Mean and 1SE %

    for i in Interference_data_list[index]:
        interference_corr_df = interference_corr_df.drop(columns=[i+' SE'])


    

####################################################################################

    # transpose mass bias data frame make new header and calculate the 1se % for each element

    # transpose dataframe and make new header

    mb_and_i_corr_df = mb_and_i_corr_df.transpose()
    new_header = mb_and_i_corr_df.iloc[0] #grab the first row for the header
    mb_and_i_corr_df = mb_and_i_corr_df[1:] #take the data less the header row
    mb_and_i_corr_df.columns = new_header #set the header row as the mb_and_i_corr_df header

    # transfer all numbers that are string to float in dataframe
    mb_and_i_corr_df = mb_and_i_corr_df.apply(pd.to_numeric, errors='coerce')
    

    # Calculate the 1se % for each element

    for i in Mass_bias_data_list[index]:
        mb_and_i_corr_df[i+' 1SE %'] = (mb_and_i_corr_df[i+' SE'] / mb_and_i_corr_df[i+' Mean']) * 100
        
    # drop all columns except Mean and 1SE %

    for i in Mass_bias_data_list[index]:
        mb_and_i_corr_df = mb_and_i_corr_df.drop(columns=[i+' SE'])


    


#####################################################################################

    # make new dfs and perpare final df

    raw_list_average = []
    raw_list_se = []
    interference_list_average = []
    interference_list_se = []
    mass_bias_list_average = []
    mass_bias_list_se = []
    
    for i in Raw_data_list[index]:
        raw_list_average.append(i+' Mean')
        raw_list_se.append(i+' 1SE %')
        
    for i in Interference_data_list[index]:
        interference_list_average.append(i+' Mean')
        interference_list_se.append(i+' 1SE %')
        
    for i in Mass_bias_data_list[index]:
        mass_bias_list_average.append(i+' Mean')
        mass_bias_list_se.append(i+' 1SE %')
        
    # create new dfs
    raw_df_average = raw_df[raw_list_average]
    raw_df_se = raw_df[raw_list_se]
    
    interference_df_average = interference_corr_df[interference_list_average]
    interference_df_se = interference_corr_df[interference_list_se]
    
    mass_bias_df_average = mb_and_i_corr_df[mass_bias_list_average]
    mass_bias_df_se = mb_and_i_corr_df[mass_bias_list_se]
    
    # transpose back to original shape
    raw_df_average = raw_df_average.transpose()
    raw_df_se = raw_df_se.transpose()
    
    interference_df_average = interference_df_average.transpose()
    interference_df_se = interference_df_se.transpose()
    
    mass_bias_df_average = mass_bias_df_average.transpose()
    mass_bias_df_se = mass_bias_df_se.transpose()
    
    # add a new column for type
    raw_df_average['Type'] = 'Raw data'
    raw_df_se['Type'] = 'Raw data'
    
    interference_df_average['Type'] = 'Interference corrected data'
    interference_df_se['Type'] = 'Interference corrected data'
    
    mass_bias_df_average['Type'] = 'Mass Bias and interference corrected data'
    mass_bias_df_se['Type'] = 'Mass Bias and interference corrected data'
    
    # combine all dataframes
    final_df = pd.concat([raw_df_average, interference_df_average, mass_bias_df_average, raw_df_se,  interference_df_se,  mass_bias_df_se])
    
    type_column = final_df.pop('Type')
    final_df.insert(0, 'Type', type_column)

    
    
    return final_df
