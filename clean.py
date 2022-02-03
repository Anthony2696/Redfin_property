# -*- coding: utf-8 -*-
import pandas as pd
import re
import time
from tqdm import tqdm

def Date_Convert(ListDate,sep,separador_csv):
	"""
	separador = '-' , '/' or '.' for date as dd-mm-aaaa or dd/mm/aaaa
	Convert to aaaa/mm/dd
	"""
	#Regex Available Dates
	Dated_m_a = r"^(0[1-9]|[1-2][0-9]|3[01]|[1-9])[/.-](0?[1-9]|1[0-2])[m][/.-]([0-9]{4})$"
	Datem_d_a = r"^(0:?[1-9]|1[0-2]|[1-9])[m][/.-](0[1-9]|[1-2][0-9]|3[01]|[1-9])[/.-](\d{4})$"
	Datea_m_d = r"(\d{4})[/.-](0?[1-9]|1[0-2])[m][/.-](0[1-9]|[1-2][0-9]|3[01]|[1-9])"
	List = []
	for date in ListDate:
		
		if date.find(separador_csv) == -1:
			List.append(date)
			continue
		aux = re.findall(Dated_m_a,date)
		
		if len(aux) != 0:
			dateConvert = aux[0][2]+sep+aux[0][1]+sep+aux[0][0]
			List.append(dateConvert)
		else:
			aux = re.findall(Datem_d_a,date)
			
			if len(aux) != 0:
				dateConvert = aux[0][2]+sep+aux[0][0]+sep+aux[0][1]
				List.append(dateConvert)
			else:
				aux = re.findall(Datea_m_d,date)
				
				if len(aux) != 0:
					dateConvert = aux[0][0]+sep+aux[0][1]+sep+aux[0][2]
					List.append(dateConvert)
				else:
					List.append('')
	return List

def cleanutf8(item):
	cadena = str(item)
	cadena = cadena.strip()
	if cadena.lower() == 'none':
		cadena = cadena.replace('none','')

	cadena = cadena.replace("\xa0",'')
	cadena = cadena.replace('\r','')
	cadena = cadena.replace("\t",'')
	cadena = cadena.replace("\n",'')
	cadena = cadena.replace('\'','')
	cadena = cadena.replace(',','')
	cadena = cadena.replace('$','')
	cadena = ' '.join(cadena.split())
	#MORE
	return cadena

def cleanesp(item):
	cadena = str(item)
	cadena = cadena.strip()
	if cadena.lower() == 'none':
		cadena = cadena.replace('none','')

	cadena = cadena.replace("\xa0",'')
	cadena = cadena.replace('\r','')
	cadena = cadena.replace("\t",'')
	cadena = cadena.replace("\n",'')
	cadena = cadena.replace('\'','')
	cadena = cadena.replace(',','')
	cadena = cadena.replace('$','')
	cadena = cadena.replace('—','')
	cadena = ' '.join(cadena.split())
	#MORE
	return cadena

def replace_dates(e):
	if str(e).lower().find('december') != -1:
		return str(e).lower().replace('december','12m')
	elif str(e).lower().find('november') != -1:
		return str(e).lower().replace('november','11m')
	elif str(e).lower().find('october') != -1:
		return str(e).lower().replace('october','10m')
	elif str(e).lower().find('september') != -1:
		return str(e).lower().replace('september','09m')
	elif str(e).lower().find('august') != -1:
		return str(e).lower().replace('august','08m')
	elif str(e).lower().find('july') != -1:
		return str(e).lower().replace('july','07m')
	elif str(e).lower().find('june') != -1:
		return str(e).lower().replace('june','06m')
	elif str(e).lower().find('may') != -1:
		return str(e).lower().replace('may','05m')
	elif str(e).lower().find('april') != -1:
		return str(e).lower().replace('april','04m')
	elif str(e).lower().find('march') != -1:
		return str(e).lower().replace('march','03m')
	elif str(e).lower().find('february') != -1:
		return str(e).lower().replace('february','02m')
	elif str(e).lower().find('january') != -1:
		return str(e).lower().replace('january','01m')
	else: return e

def depuracion(df):
	try:
		#CAMPOS OBLIGATORIOS
		####################
		list_index_addr = []
		address = 0
		for i, row  in tqdm(df.iterrows(), desc="Depuration Loop", total=len(df)):
			try: lot_size_value = float(row["LOT SIZE"])
			except: lot_size_value= 0.0
			try: b_size_value = float(row["SQUARE FEET"])
			except: b_size_value = 0.0

			if lot_size_value < b_size_value:
				df["LOT SIZE"][i] = ''
				df["SQUARE FEET"][i] = ''
			if re.search(r'^(\d+\S*\s(?:\S\s?)+)',row["ADDRESS"]):
				address+=1
			else:				
				list_index_addr.append(i)

		promedio_addr = (address/df.shape[0])*100
		if promedio_addr < 70 and len(list_index_addr)>0:
			for j in list_index_addr:
				df["ADDRESS"][j] = ''
			print('DEPURADO TABLE PROPERTY IN BUILDING ADDRESS')

		return df
	except:
		print('.')

	return df

def join_csv(df1,df2):
	if df2.shape[0] == 0:
		return df1
	
	return pd.concat([df1,df2])

def split_df(df):
	if df.shape[0] == 0: return df

	l_zips = []
	l_states = []
	l_cities = []
	l_addrs = []
	l_prices = []
	l_beds = []
	l_baths = []
	l_locs = []
	l_sqft = []
	l_dm = []
	l_ds = []
	l_urls = []

	for i,row in tqdm(df.iterrows(), desc="Split DF", total=len(df)):
		try:
			zip_code = row["ZIP OR POSTAL CODE"]
			state = row["STATE OR PROVINCE"]
			city = row["CITY"]
			mayor = 0

			addrs = row["ADDRESS"].split('|')
			prices = row["PRICE"].split('|')
			beds = row["BEDS"].split('|')
			baths = row["BATHS"].split('|')
			locations = row["LOCATION"].split('|')
			square_feets = row["SQUARE FEET"].split('|')
			day_on_markets = row["DAYS ON MARKET"].split('|')
			dollar_square = row["DOLLAR SQUARE FEET"].split('|')
			urls = row["URL"].split('|')

			mayor = max(len(addrs),len(prices))
			mayor = max(mayor,len(beds))
			mayor = max(mayor,len(baths))
			mayor = max(mayor,len(locations))
			mayor = max(mayor,len(square_feets))
			mayor = max(mayor,len(day_on_markets))
			mayor = max(mayor,len(dollar_square))
			mayor = max(mayor,len(urls))

			if len(addrs) != mayor:
				diff = mayor - len(addrs)
				addrs.extend(['' for e in range(diff)])

			if len(prices) != mayor:
				diff = mayor - len(prices)
				prices.extend(['' for e in range(diff)])

			if len(beds) != mayor:
				diff = mayor - len(beds)
				beds.extend(['' for e in range(diff)])

			if len(baths) != mayor:
				diff = mayor - len(baths)
				baths.extend(['' for e in range(diff)])

			if len(locations) != mayor:
				diff = mayor - len(locations)
				locations.extend(['' for e in range(diff)])

			if len(square_feets) != mayor:
				diff = mayor - len(square_feets)
				square_feets.extend(['' for e in range(diff)])

			if len(day_on_markets) != mayor:
				diff = mayor - len(day_on_markets)
				day_on_markets.extend(['' for e in range(diff)])

			if len(dollar_square) != mayor:
				diff = mayor - len(dollar_square)
				dollar_square.extend(['' for e in range(diff)])

			if len(urls) != mayor:
				diff = mayor - len(urls)
				urls.extend(['' for e in range(diff)])
			
			l_zips.extend([zip_code for i in range(mayor)])
			l_states.extend([state for i in range(mayor)])
			l_cities.extend([city for i in range(mayor)])
			l_addrs.extend(addrs)
			l_prices.extend(prices)
			l_beds.extend(beds)
			l_baths.extend(baths)
			l_locs.extend(locations)
			l_sqft.extend(square_feets)
			l_dm.extend(day_on_markets)
			l_ds.extend(dollar_square)
			l_urls.extend(urls)
		except:
			print('Error Split row:',i+2)
	
	data = {
		"SALE TYPE":[ '' for i in range(len(l_zips))],
		"SOLD DATE":[ '' for i in range(len(l_zips))],
		"PROPERTY TYPE":[ '' for i in range(len(l_zips))],
		"ADDRESS":[cleanesp(e) for e in l_addrs],
		"CITY":[cleanesp(e) for e in l_cities],
		"STATE OR PROVINCE":[cleanesp(e) for e in l_states],
		"ZIP OR POSTAL CODE":[cleanesp(e) for e in l_zips],
		"PRICE":[cleanesp(e) for e in l_prices],
		"BEDS":[cleanesp(e) for e in l_beds],
		"BATHS":[cleanesp(e) for e in l_baths],
		"LOCATION":[cleanesp(e) for e in l_locs],
		"SQUARE FEET":[cleanesp(e) for e in l_sqft],
		"LOT SIZE":[ '' for i in range(len(l_zips))],
		"YEAR BUILT":[ '' for i in range(len(l_zips))],
		"DAYS ON MARKET":[cleanesp(e) for e in l_dm],
		"DOLLAR SQUARE FEET":[cleanesp(e) for e in l_ds],
		"HOA/MONTH":[ '' for i in range(len(l_zips))],
		"STATUS":[ '' for i in range(len(l_zips))],
		"NEXT OPEN HOUSE START TIME":[ '' for i in range(len(l_zips))],
		"NEXT OPEN HOUSE END TIME":[ '' for i in range(len(l_zips))],
		"URL":[cleanesp(e) for e in l_urls],
		"SOURCE":[ '' for i in range(len(l_zips))],
		"MLS NUMBER":[ '' for i in range(len(l_zips))],
		"FAVORITE":[ '' for i in range(len(l_zips))],
		"INTERESTED":[ '' for i in range(len(l_zips))],
		"LATITUDE":[ '' for i in range(len(l_zips))],
		"LONGITUDE":[ '' for i in range(len(l_zips))]
	}

	df = pd.DataFrame(data)
	return df

def RedfinTable(df):
	"""
	Funcion para generar
	Redfin_Csv.csv
	"""	
	data = {
			"building_parcel_number": [cleanutf8(e) for e in df["building_parcel_number"]],
			"date_create_source": [cleanutf8(e) for e in df["date_create_source"]],
			"number_of_stories": [cleanutf8(e) for e in df["number_of_stories"]],
			"number_of_half_bathrooms": [cleanutf8(e) for e in df["number_of_half_bathrooms"]],
			"number_of_rooms": [cleanutf8(e) for e in df["number_of_rooms"]],
			"garage_type": [cleanutf8(e) for e in df["garage_type"]],
			"heating_type": [cleanutf8(e) for e in df["heating_type"]],
			"building_external_wall": [cleanutf8(e) for e in df["building_external_wall"]],
			"foundation": [cleanutf8(e) for e in df["foundation"]],
			"construction_type": [cleanutf8(e) for e in df["construction_type"]],
			"roof": [cleanutf8(e) for e in df["roof"]],
			"fireplace": [cleanutf8(e) for e in df["fireplace"]],
			"pool": [cleanutf8(e) for e in df["pool"]],
			"zoning": [cleanutf8(e) for e in df["zoning"]],
			"legal_description": [cleanutf8(e) for e in df["legal_description"]],
			"parcel_status": [cleanutf8(e) for e in df["parcel_status"]],
			"n_garage": [cleanutf8(e) for e in df["n_garage"]],
			"n_parking": [cleanutf8(e) for e in df["n_parking"]],
			"builder_name": [cleanutf8(e) for e in df["builder_name"]],
			"Association_fee": [cleanutf8(e) for e in df["Association_fee"]],
			"Additional_fee": [cleanutf8(e) for e in df["Additional_fee"]],
			"PROPERTY_DETAILS": [cleanutf8(e) for e in df["PROPERTY_DETAILS"]],
			"PRICE_INSIGHTS": [cleanutf8(e) for e in df["PRICE_INSIGHTS"]],
			"HOUSE_DESCRIPTION": [cleanutf8(e) for e in df["HOUSE_DESCRIPTION"]],
			"COMMUNITY": [cleanutf8(e) for e in df["COMMUNITY"]],
			"PROPERTY_PRICE": [cleanutf8(e) for e in df["PROPERTY_PRICE"]],
			"property_tax": [cleanutf8(e) for e in df["property_tax"]],
			"property_tax_year": [cleanutf8(e) for e in df["property_tax_year"]],
			"build_link_source": [cleanutf8(e) for e in df["build_link_source"]],
			"original_id": [cleanutf8(e) for e in df["original_id"]]
	}
	#data = stable(data,len(data["building_parcel_number"]))
	pt_df = pd.DataFrame(data)
	#pt_df = depuracion(pt_df)
	
	pt_df.to_csv('results_properties_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
	#pt_df.to_csv('./insert_original_redfin/{}/input_data/Redfin_Csv_{}-{}_{}.csv'.format(folder,state,loc,str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
	pt_df.to_csv('./send_fileRemote/input_file/results_properties_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)		

	print('Generated Results_Properties.csv')

def main():
		
	debug = pd.DataFrame(columns=[
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
	debug2 = pd.DataFrame(columns=[
		"name",
		"path",
		"original_id"
	])
	try:
		df = pd.read_csv("./merge/results_properties.csv",dtype=str,keep_default_na=False)
		RedfinTable(df)
	except:
		print('Nothing to Do. results_properties.csv not found!!')
		debug.to_csv('results_properties_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
		debug.to_csv('./send_fileRemote/input_file/results_properties_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)

	try:
		df_img = pd.read_csv("./merge/results_images.csv",dtype=str,keep_default_na=False)
		df_img.to_csv('results_images_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
		df_img.to_csv('./send_fileRemote/input_file/results_images_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
		
	except:
		debug2.to_csv('results_images_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
		debug2.to_csv('./send_fileRemote/input_file/results_images_{}.csv'.format(str(time.strftime("%Y-%m-%d-%H:%M"))),index=False)
	
main()
