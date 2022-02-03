#####################################################################################################
# Inserta registros en la tabla Redin de la BD OriginalData suministrados en un archivo .csv almacenado 
# en la carpeta <input_data>
# La Entrada es un archivo .csv almacenado en la carpeta <input_data> 
# La Salida es un archivo .csv con los errores que arroja Mysql si los hubiere. Esta salida se almacena 
# en la carpeta <output>
#####################################################################################################
# Nahir Barrios  Fecha de realizacion: 2021-08-25, correo nahir.barrios@mykukun.com
#
#####################################################################################################

from operator import is_
from pathlib import Path
import pandas as pd
from pandas import DataFrame, read_csv, read_sql
from os import listdir
from os.path import join
import string
import datetime 
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm
from sshtunnel import SSHTunnelForwarder
import sshtunnel
import paramiko
import logging
import time
import os

def isNaN(num):
    return num != num
def is_null(v):
    if (isNaN(v) or v=='' or v=='nan'):
        return None
    else:
        return v


tqdm.pandas()

date_now = datetime.datetime.now()
date_now = datetime.datetime.strftime(date_now,'%Y-%m-%d')

def open_ssh_tunnel(verbose=False):
    """Abrir un tunel usando  username y pem.
       Asignar de forma correcta la locaclizacion y nombre del archivo pem
    
    :param verbose: Set to True to show logging
    :return tunnel: Global SSH tunnel connection
    """
    
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG
    
    global tunnel
    #mypkey = paramiko.RSAKey.from_private_key_file('../../pem/13.57.62.82_DB/' + 'Kukun_data_team.pem')
    mypkey = paramiko.RSAKey.from_private_key_file('./TunelSsh(NOBORRAR)/KUKUN_DATA_TEAM_NOV_2020.pem')

    tunnel = SSHTunnelForwarder(
        ('13.57.62.82', 22),
        ssh_username = 'ubuntu',
        ssh_pkey=mypkey,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    
    tunnel.start()

def close_ssh_tunnel():
    """Closes the SSH tunnel connection.
    """
    
    tunnel.close

def db_connection(db):
    open_ssh_tunnel()

    if (db == 'property_db'):
        mySQLconnection_Contractor = mysql.connector.connect(host='127.0.0.1',
                        database='OriginalData',
                        user='user_insert',
                        password='kl4v3.1ns3rt',
                        port=tunnel.local_bind_port)
        """
        user='root',
        password='mysql')                        
        user='user_insert',
        password='kl4v3.1ns3rt')
        """
        print("conexion")
        return(mySQLconnection_Contractor)
    close_ssh_tunnel()


df_report = pd.DataFrame(columns=['file_name','redfin_original_id', 'error'])
df_output = pd.DataFrame(columns=['redfin_original_id', 'building_parcel_number', 'number_of_stories', 'number_of_half_bathrooms', 'building_sub_category_code', 'number_of_rooms', 'garage_type',
    'heating_type', 'building_external_wall', 'foundation', 'construction_type', 'roof', 'fireplace', 'pool', 'zoning', 'legal_description', 'parcel_status',
    'n_garage', 'n_parking', 'builder_name', 'property_tax_year', 'property_tax', 'Association_fee', 'Additional_fee', 'PROPERTY_DETAILS', 'PROPERTY_PRICE', 'COMMUNITY',
    'PRICE_INSIGHTS','HOUSE_DESCRIPTION','build_link_source'])

def consult_original_id(original_id,cursor,table_name,path=None):
    try:
        if table_name == 'RedfinImages':
            query = f"select redfin_original_id from OriginalData.{table_name} where(redfin_original_id = {original_id} and path_image = '{path}')"
        else:
            query = f"select redfin_original_id from OriginalData.{table_name} where(redfin_original_id = %s)" % (original_id)
        cursor.execute(query)
        data = cursor.fetchall()

        if len(data) > 0: return 1

    except Error as e:
        print ("REPORT ERROR MYSQL CONSULT ORIGINAL REDFIN", e)
        return 2
    
    return 3

def process_update_redfin(row,mySQLconnection_Property,cursor,cursor_details,file_name):
    global df_output,df_report

    try:
        #N = is_null(row['N'])
        building_parcel_number = is_null(row['building_parcel_number'])
        number_of_stories = is_null(row['number_of_stories'])
        number_of_half_bathrooms =  is_null(row['number_of_half_bathrooms']) 
        number_of_rooms = is_null(row['number_of_rooms']) 	
        garage_type = is_null(row['garage_type']) 	
        heating_type =  is_null(row['heating_type']) 
        building_external_wall =  is_null(row['building_external_wall']) 
        foundation =  is_null(row['foundation'])
        construction_type = 	is_null(row['construction_type'])
        roof = is_null(row['roof'])
        fireplace = 	is_null(row['fireplace']) 
        pool =  is_null(row['pool']) 
        zoning = is_null(row['zoning']) 	
        legal_description = is_null(row['legal_description']) 
        parcel_status =  is_null(row['parcel_status']) 
        n_garage =  is_null(row['n_garage']) 
        n_parking = is_null(row['n_parking'])
        builder_name = is_null(row['builder_name'])
        property_tax_year =  is_null(row['property_tax_year'])
        property_tax =  is_null(row['property_tax'])
        Association_fee = is_null(row['Association_fee'])
        Additional_fee = is_null(row['Additional_fee'])
        PROPERTY_DETAILS = is_null(row['PROPERTY_DETAILS']) 	
        PROPERTY_PRICE =	is_null(row['PROPERTY_PRICE'])
        COMMUNITY = is_null(row['COMMUNITY'])
        PRICE_INSIGHTS =	is_null(row['PRICE_INSIGHTS'])
        HOUSE_DESCRIPTION =	is_null(row['HOUSE_DESCRIPTION'])
        original_id = is_null(row["original_id"])
        build_link_source = is_null(row["build_link_source"])
        
        cursor = mySQLconnection_Property.cursor()
        sql_update_query = """UPDATE OriginalData.Redfin \
                        SET building_parcel_number = %s, number_of_stories = %s, number_of_half_bathrooms = %s, number_of_rooms = %s, \
                        garage_type = %s, heating_type = %s, building_external_wall = %s, foundation = %s, construction_type = %s, roof = %s, fireplace = %s, pool = %s, \
                        zoning = %s, legal_description = %s, parcel_status = %s, n_garage = %s, n_parking = %s,  builder_name = %s, property_tax_year = %s, property_tax = %s, \
                        Association_fee = %s, Additional_fee = %s, PROPERTY_PRICE = %s, COMMUNITY = %s, PRICE_INSIGHTS = %s, HOUSE_DESCRIPTION = %s, build_link_source = %s \
                        WHERE (redfin_original_id = %s)"""
                        
        cursor.execute(sql_update_query, (building_parcel_number, number_of_stories, number_of_half_bathrooms, number_of_rooms, 
                        garage_type, heating_type,  building_external_wall, foundation, construction_type, roof, fireplace, pool,
                        zoning, legal_description, parcel_status, n_garage, n_parking, builder_name, property_tax_year, property_tax, Association_fee,
                        Additional_fee, PROPERTY_PRICE,  COMMUNITY, PRICE_INSIGHTS, HOUSE_DESCRIPTION, build_link_source,original_id))

        if PROPERTY_DETAILS != None:
            cursor_details = mySQLconnection_Property.cursor()
            c = consult_original_id(original_id,cursor_details,'RedfinDetails')
            if c == 1:
                sql_update_details = """ UPDATE OriginalData.RedfinDetails \
                    SET details = %s WHERE (redfin_original_id = %s) """
                cursor_details.execute(sql_update_details,(PROPERTY_DETAILS,original_id))
            elif c == 2:
                sql_update_details = """ UPDATE OriginalData.RedfinDetails \
                    SET details = %s WHERE (redfin_original_id = %s) """
                cursor_details.execute(sql_update_details,(PROPERTY_DETAILS,original_id))
            else:
                sql_insert_details = "INSERT INTO OriginalData.RedfinDetails \
                                        (redfin_original_id,details) \
                                        VALUES( %s, %s) "
                cursor_details.execute(sql_insert_details,(original_id,PROPERTY_DETAILS))

        df_output = df_output.append({'redfin_original_id':original_id, 'building_parcel_number':building_parcel_number, 'number_of_stories':number_of_stories, 
        'number_of_half_bathrooms':number_of_half_bathrooms, 'number_of_rooms': number_of_rooms, 'garage_type':garage_type,
        'heating_type':heating_type, 'building_external_wall':building_external_wall, 'foundation':foundation, 'construction_type':construction_type, 'roof':roof, 'fireplace':fireplace, 
        'pool':pool, 'zoning':zoning, 'legal_description':legal_description, 'parcel_status':parcel_status, 'n_garage':n_garage, 'n_parking':n_parking, 'builder_name':builder_name,
        'property_tax_year':property_tax_year, 'property_tax':property_tax, 'Association_fee':Association_fee, 'Additional_fee':Additional_fee, 'PROPERTY_DETAILS':PROPERTY_DETAILS, 'PROPERTY_PRICE':PROPERTY_PRICE, 'COMMUNITY,':COMMUNITY,
        'PRICE_INSIGHTS':PRICE_INSIGHTS, 'HOUSE_DESCRIPTION':HOUSE_DESCRIPTION, 'build_link_source':build_link_source}, ignore_index=True)
        
    except Error as e :
        print ("REPORT ERROR MYSQL UPDATE REDFIN ORIGINAL_ID:", e, original_id, file_name)
        df_report = df_report.append({'file_name':file_name, 'redfin_original_id': original_id, 'error':e}, ignore_index=True)

def process_update_redfin_images(row,mySQLconnection_Property,cursor,file_name):
    global df_report,df_output
    try:
        original_id = is_null(row["original_id"])
        path = is_null(row["path"])
        name = is_null(row["name"])
        cursor = mySQLconnection_Property.cursor()
        c = consult_original_id(original_id,cursor,'RedfinImages',path)
        if c == 1:
            print ("REPORT ERROR DUPLICATE MYSQL INSERT IMAGES REDFIN ORIGINAL_ID:", original_id, file_name)
            df_report = df_report.append({'file_name':file_name, 'redfin_original_id': original_id, 'error':'DUPLICATE ENTRY INTO REDFINIMAGES TABLE'}, ignore_index=True)
        elif c == 2:
            print ("REPORT ERROR DUPLICATE MYSQL INSERT IMAGES REDFIN ORIGINAL_ID:", original_id, file_name)
            df_report = df_report.append({'file_name':file_name, 'redfin_original_id': original_id, 'error':'DUPLICATE ENTRY INTO REDFINIMAGES TABLE'}, ignore_index=True)
        else:
            sql_insert_query = "INSERT INTO OriginalData.RedfinImages \
                            (path_image, redfin_original_id) \
                            VALUES(%s, %s)"
                            
            cursor.execute (sql_insert_query, (path,original_id) )
                        
            df_output = df_output.append({'redfin_original_id':original_id, 'path':path, 'name':name}, ignore_index=True)
    
    except Error as e:
        print ("REPORT ERROR MYSQL INSERT IMAGES REDFIN ORIGINAL_ID:", e, original_id, file_name)
        df_report = df_report.append({'file_name':file_name, 'redfin_original_id': original_id, 'error':e}, ignore_index=True)

def update_redfin(df, file_name):
    print("Start insert redfin for", file_name, "size_df", len(df))
    mySQLconnection_Property = db_connection('property_db')
    cursor = mySQLconnection_Property.cursor()
    cursor_details = mySQLconnection_Property.cursor()
    print("File: ", file_name)
    if 'images' in file_name:
        df.progress_apply(lambda row: process_update_redfin_images(row,mySQLconnection_Property,cursor,file_name),axis=1)
    else:
        df.progress_apply(lambda row: process_update_redfin(row,mySQLconnection_Property,cursor,cursor_details,file_name),axis=1)
    mySQLconnection_Property.commit()
    mySQLconnection_Property.close()
    cursor.close()
    cursor_details.close()
    print("End Insert ", file_name)

def delete_all_redfin():
    """
        NO USAR, BORRA TODo EL CONTENIDO
        DE LA TABLA REDFIN EN LA BD ORIGINALDATA
    """
    print('Start Delete Redfin from OriginalData')
    mySQLconnection_Property = db_connection('property_db')
    cursor = mySQLconnection_Property.cursor()
    sql_insert_query = "DELETE FROM OriginalData.Redfin"
    cursor.execute (sql_insert_query)

    mySQLconnection_Property.commit()
    mySQLconnection_Property.close()
    cursor.close()
    print("End ")

if __name__ == '__main__':
    file_name = os.environ.get("FILE_NAME")
    folder_name = os.environ.get("FOLDER_NAME")
    dir_files = f'{folder_name}/input_data/divisions/'

    #print(file_name)
    #print(folder_name)
    #print(dir_files)
    
    if '.~lock' in file_name:
            pass 
    elif ( '.csv' in file_name):
        input_data_frame = pd.read_csv(f'./{file_name}', dtype=str, keep_default_na=False,low_memory=True)    
        print ("Antes del llamado, para procesar: ", file_name)
        update_redfin(input_data_frame, file_name)

        df_output = df_output.drop_duplicates()
        file_name = file_name.replace('.csv','').replace(dir_files,'')
        if not df_output.empty:
            df_output.to_csv(join(f'./{folder_name}/output/output_'+ file_name+'.csv'), index=0)
            df_output.to_csv(join(f'./{folder_name}/output_'+ file_name+'_'+str(time.strftime("%Y-%m-%d-%H:%M"))+'.csv'), index=0)
            
        if not df_report.empty:
            df_report.to_csv(join(f'./{folder_name}/output/df_report_'+ file_name+str(time.strftime("%Y-%m-%d-%H:%M"))+ '.csv'), index=0)
            df_report.to_csv(join(f'./{folder_name}/df_report_'+ file_name+str(time.strftime("%Y-%m-%d-%H:%M"))+ '.csv'), index=0)
    
    print("END")  

