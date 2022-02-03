from sys import argv #importar argumentos desde la terminal
from os import listdir
from os.path import join
import pandas as pd

df_empty = pd.DataFrame(columns=[
    'building_parcel_number',
    'date_create_source',
    'number_of_stories',
    'number_of_half_bathrooms',
    'number_of_rooms',
    'garage_type',
    'heating_type',
    'building_external_wall',
    'foundation',
    "construction_type",
    "roof",
    "fireplace",
    "pool",
    "zoning",
    "legal_description",
    "parcel_status",
    "n_garage",
    "n_parking",
    "builder_name",
    "Association_fee",
    "Additional_fee",
    "PROPERTY_DETAILS",
    "PRICE_INSIGHTS",
    "HOUSE_DESCRIPTION",
    "COMMUNITY",
    "PROPERTY_PRICE",
    "property_tax",
    "property_tax_year",    
    "build_link_source",
    "original_id"
])

def split(df,file_name,folder_name,divisor=50000):
    if df.shape[0] <= 0:
        print('dataframe empty, nothing to do!.')
    else:
        file_name = file_name.replace('.csv','')
        lower_limit = 0
        upper_limit = divisor
        n_div = df.shape[0]//divisor
        for i in range(0,n_div+1):
            print('Ciclo:',i,lower_limit,'-',upper_limit)
            if 'results_properties' in file_name:
                file_name_o = 'part'+str(i+1)
            elif 'results_images' in file_name:
                file_name_o = 'part'+str(i+1)+'_images'
            if df.shape[0] <= upper_limit:
                df_aux = df[lower_limit:]
            else: df_aux = df[lower_limit:upper_limit]
            df_aux.to_csv(f'./{folder_name}/input_data/divisions/{file_name_o}.csv', index=False)

            lower_limit += divisor
            upper_limit += divisor

if __name__ == '__main__':
    script,folder = argv
    files = f'./{folder}/input_data/'
    df = df_empty
    for file_name in sorted(listdir(files)):
        if '.~lock' in file_name:
                continue 
        if ( '.csv' in file_name):           
            print("File: ", file_name)
            df = pd.read_csv(join(files,file_name),dtype=str,keep_default_na=False)
            split(df,file_name,folder)
            
    
