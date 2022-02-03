from os import listdir
import pandas as pd
from sys import argv #importar argumentos desde la terminal
import time
from tqdm import tqdm

script, file_name = argv

count = 0
df_aux = None
list_files = [file for file in listdir('./input') if not '.~' in file and '.csv' in file ]

for file in tqdm(list_files, desc=f"Join Files",total=len(list_files)):
	try:
		df_file = pd.read_csv('./input/{}'.format(file),dtype=str,keep_default_na=False)
		if count == 0:
			df_aux = df_file
		else:
			df_aux = pd.concat([df_aux,df_file])
		count += 1
	except: print('Archivo defectuoso',file)
if file_name == 'results_properties' or file_name == 'results_images':
	namefile = '{}.csv'.format(file_name)
else:
	namefile = '{}_{}.csv'.format(file_name,str(time.strftime("%Y-%m-%d-%H:%M")))

if count > 0:
	df_aux.to_csv(namefile,index=False,encoding='utf-8')
	print('Fusionado con exito! en {}.csv'.format(file_name))
else: print('\t¡¡¡No generado archivo {}!!!'.format(namefile))