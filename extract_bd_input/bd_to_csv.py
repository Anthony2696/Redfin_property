import pandas as pd
from pandas import DataFrame, read_csv
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
from sys import argv #importar argumentos desde la terminal

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
    mypkey = paramiko.RSAKey.from_private_key_file('./credenciales_pem/KUKUN_DATA_TEAM_NOV_2020.pem')

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
                        database='Original',
                        user='anthony_briceno',
                        password='@nthony.Brice12',
                        port=tunnel.local_bind_port)
        """
        user='root',
        password='mysql')                        
        user='user_insert',
        password='kl4v3.1ns3rt')
        """
        print("conexion")
        close_ssh_tunnel()
        return(mySQLconnection_Contractor)

def convert_csv(csv_name,data=tuple()):
    addrs = []
    urls = []
    cities = []
    zips = []
    states = []
    oids = []

    for tupla in tqdm(data,desc='Extract Data for {}'.format(csv_name),total=len(data)):
        urls.append(tupla[0])
        addrs.append(tupla[1])
        cities.append(tupla[2])
        states.append(tupla[3])
        zips.append(tupla[4])
        oids.append(tupla[5])

    dataf = {
        "ADDRESS":addrs,
        "URL": urls,
        "CITY":cities,
        "ZIP_CODE":zips,
        "STATE": states,
        "original_id":oids
    }

    print('-- \tGenerado {}.csv'.format(csv_name))

    df = DataFrame(dataf)
    return df
    #df.to_csv('{}.csv'.format(csv_name),index=False)
        
def consultar(n,column,bdname='property_db',table='Redfin'):
    print('Start redfin consult')
    mySQLconnection_Property = db_connection(bdname)
    cursor = mySQLconnection_Property.cursor()
    data = ''
    try:
        sql_select_query = f"SELECT url,street_address,city,state_code,zip_code,redfin_original_id from Original.{table} WHERE ({column} is NULL) LIMIT {n};"
        cursor.execute(sql_select_query)
        data = cursor.fetchall()
    except Error as e:
        print('Error',e)

    mySQLconnection_Property.commit()
    mySQLconnection_Property.close()
    cursor.close()
    print("End Consult")
    return data

if __name__ == '__main__':
    df_aux = None
    count = 0
    script, file_name, column_name, n_elem= argv
    """
    while True:
        try:
            code = str(input('Ingrese el codigo del condado: '))

            data = consultar(code)

            df_code = convert_csv(code,data)

            if len(df_code) > 0:
                df_aux = pd.concat([df_aux,df_code])

                count += 1

            opt = str(input('¿Desea consultar otro codigo?\n\t- en caso afirmativo responda (Y o y): '))

            if opt.lower() != 'y':
                break
        except:
            exit = str(input('Ocurrio un error...\n\t- ¿Desea intentar de nuevo?\n\t- en caso afirmativo responda (Y o y): '))
            if exit.lower() != 'y':
                break
    if count > 0:
        namefile = '{}.csv'.format(file_name)
        df_aux.to_csv(namefile,index=False,encoding='utf-8')
        print('generado con exito! {}'.format(namefile))
    else: print('No generado!!!')
    """
    data = consultar(n_elem,column_name)
    df_code = convert_csv(file_name,data)
    df_code.to_csv(f'{file_name}.csv',index=False)