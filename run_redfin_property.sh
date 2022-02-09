#!/bin/bash
#########################################################################################################
#Script Bash para el automatizado de scrapy, normalizado y insercion de datos desde la pagina Redfin.com
#Anthony Briceño Fecha de realizacion: 2021-08-04, correo anthony.briceno@mykukun.com
#########################################################################################################

cd $(pwd)
source /home/kukun-v/Escritorio/Redfin_property/redfin/bin/activate #COLOCAR RUTA ESPECIFICA DONDE SE ENCUENTRE EL PROYECTO
#source /home/kukuno1/Desktop/Redfin_CSV/redfin/bin/activate
#source /home/anthony/kukun/bin/activate
######################ENTER FILTERS REDFIN########################
dayinit=$(date +%A)
horainit=$(date +%H)
mininit=$(date +%M)
nohup echo $"Day Init $dayinit a las $horainit:$mininit" > timeinit_redfinpro.txt

###########################VALIDATE INSERT REDFIN##############################
while :
do
	echo -e "\n\t\t*** INPUT VALIDATE INSERT REDFIN_PROPERTY ***\n"
	read -p "DO YOU WANT TO INSERT INTO THE DATABASE, PRESS Y OR N: " validateinsert

	validateinsert="${validateinsert,,}"
	if [ "$validateinsert" = '' ]; then
		validateinsert='n'
	elif [[ "$validateinsert" != 'y' && "$validateinsert" != 'n' ]]; then
		echo -e "Wrong format !,\nHELP: RESPOND WITH THE LETTERS Y OR N, TO INSERT INTO THE ORIGINALDATA DATABASE."
		continue
	fi

	echo -e "\n\t\t*** INPUT FUNCTIONALITY ***\n"
	echo -e "PRESS 1: RUN REDFIN_BOT CONSULTING BY URL"
	echo -e "PRESS 2: RUN REDFIN_BOT CONSULTING BY ADDRESS\n"
	read -p "SELECT FUNCTIONALITY: " functionality
	
	if [[ "$functionality" != '1' && "$functionality" != '2' ]]; then
		echo -e "Wrong format !,\nHELP: RESPOND WITH THE NUMBERS 1 OR 2."
		continue
	fi

	break
done
###############EXTRACT INTO DATABASE####################
cd extract_bd_input
file_bd=list1.csv
if [ -f "$file_bd" ]; then
	rm list1.csv
fi
python bd_to_csv.py list1 building_parcel_number 5000
cd ..
########################################################

################EXECUTE BOT REDFIN_PROPERTY#############
if [[ $functionality -eq 1 ]]; then
	cd property_url

	directorio_input=input
	if [ -d $directorio_input ];then
		if [ "$(ls $directorio_input)" ]; then
			echo "¡¡THE FOLDER: $directorio_input, IS NOT EMPTY!!, It will be erased and created again!"
			rm -r input
			mkdir input
		else
			echo "¡¡THE FOLDER: $directorio_input, IS EMPTY!!"
		fi
	else
		echo "¡¡THE FOLDER: $directorio_input, NOT EXIST!!"
		mkdir input
	fi
	file_bd=../extract_bd_input/list1.csv
	if [ -f "$file_bd" ]; then
		cp ../extract_bd_input/list1.csv ./input/
		python redfinBotUrl.py
		################MERGE DATA OUTPUT BOT#################
		fichero_results_redfin=results_redfin_property1.csv
		if [ -f $fichero_results_redfin ]; then
			for file in results_redfin_property*.csv; do
				mv "$file" ../merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
			done
			cd ../merge/
			python merge.py results_redfin_property #results_redfin es el nombre del archivo que generara el merge.py
			for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
			cd ../property_url #Salir de la carpeta merge
		else
			echo "¡¡El fichero: $fichero_results_redfin, no existe!!"
		fi

		fichero_rproperties=../merge/results_properties.csv
		if [ -f $fichero_rproperties ];then
			rm ../merge/results_properties.csv
		fi

		fichero_results_properties=results_properties1.csv
		if [ -f $fichero_results_properties ]; then
			for file in results_properties*.csv; do
				mv "$file" ../merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
			done
			cd ../merge/
			python merge.py results_properties #results_redfin es el nombre del archivo que generara el merge.py
			for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
			cd ../property_url #Salir de la carpeta merge
		else
			echo "¡¡El fichero: $fichero_results_properties, no existe!!"
		fi
		#########################################################

	else
		echo "List1 is not found in the directory. Bot not executed"
	fi	
	cd ..

elif [[ $functionality -eq 2 ]]; then
	cd property_address

	directorio_input=input
	if [ -d $directorio_input ];then
		if [ "$(ls $directorio_input)" ]; then
			echo "¡¡THE FOLDER: $directorio_input, IS NOT EMPTY!!, It will be erased and created again!"
			rm -r input
			mkdir input
		else
			echo "¡¡THE FOLDER: $directorio_input, IS EMPTY!!"
		fi
	else
		echo "¡¡THE FOLDER: $directorio_input, NOT EXIST!!"
		mkdir input
	fi
	file_bd=../extract_bd_input/list1.csv
	if [ -f "$file_bd" ]; then
		cp ../extract_bd_input/list1.csv ./input/
		python redfinbot_address.py
		################MERGE DATA OUTPUT BOT#################
		fichero_results_redfin=results_redfin_property1.csv
		if [ -f $fichero_results_redfin ]; then
			for file in results_redfin_property*.csv; do
				mv "$file" ../merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
			done
			cd ../merge/
			python merge.py results_redfin_property #results_redfin es el nombre del archivo que generara el merge.py
			for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
			cd ../property_address #Salir de la carpeta merge
		else
			echo "¡¡El fichero: $fichero_results_redfin, no existe!!"
		fi

		fichero_rproperties=../merge/results_properties.csv
		if [ -f $fichero_rproperties ];then
			rm ../merge/results_properties.csv
		fi

		fichero_results_properties=results_properties1.csv
		if [ -f $fichero_results_properties ]; then
			for file in results_properties*.csv; do
				mv "$file" ../merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
			done
			cd ../merge/
			python merge.py results_properties #results_redfin es el nombre del archivo que generara el merge.py
			for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
			cd ../property_address #Salir de la carpeta merge
		else
			echo "¡¡El fichero: $fichero_results_properties, no existe!!"
		fi
		##########################################################
	
	else
		echo "List1 is not found in the directory. Bot not executed"
	fi
	cd ..
else
	fichero_rproperties=merge/results_properties.csv
	if [ -f $fichero_rproperties ];then
		rm merge/results_properties.csv
	fi

	echo "BAD FUNCTIONALITY, REVIEW INPUT"
fi
#########################################################

##############EXECUTE BOT IMAGES#############
cd property_images
fichero_rpro=../merge/results_properties.csv
if [ -f $fichero_rpro ];then
	directorio_input=input
	if [ -d $directorio_input ];then
		if [ "$(ls $directorio_input)" ]; then
			echo "¡¡THE FOLDER: $directorio_input, IS NOT EMPTY!!, It will be erased and created again!"
			rm -r input
			mkdir input
		else
			echo "¡¡THE FOLDER: $directorio_input, IS EMPTY!!"
		fi
	else
		echo "¡¡THE FOLDER: $directorio_input, NOT EXIST!!"
		mkdir input
	fi
	cp ../merge/results_properties.csv ./input/
	python redfinbot_images.py
	################MERGE DATA OUTPUT BOT#################
	fichero_results_redfin_img=results_redfin_propertyImages1.csv
	if [ -f $fichero_results_redfin_img ]; then
		for file in results_redfin_propertyImages*.csv; do
			mv "$file" ../merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
		done
		cd ../merge/
		python merge.py results_redfin_propertyImages #results_redfin es el nombre del archivo que generara el merge.py
		for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
		cd ../property_images #Salir de la carpeta merge
	else
		echo "¡¡El fichero: $fichero_results_redfin_img, no existe!!"
	fi

	fichero_rimages=../merge/results_images.csv
	if [ -f $fichero_rimages ];then
		rm ../merge/results_images.csv
	fi

	fichero_results_redfin_img2=results_images1.csv
	if [ -f $fichero_results_redfin_img2 ]; then
		for file in results_images*.csv; do
			mv "$file" ../merge/input/; #mueve archivos .csv descargados en el proceso de descarga para ser fusionados
		done
		cd ../merge/
		python merge.py results_images #results_redfin es el nombre del archivo que generara el merge.py
		for file in input/*.csv; do rm "$file"; done #borrar archivos copiados anteriormente
		cd ../property_images #Salir de la carpeta merge
	else
		echo "¡¡El fichero: $fichero_results_redfin_img2, no existe!!"
	fi

	##########################################################
else
	fichero_rimages=../merge/results_images.csv
		if [ -f $fichero_rimages ];then
			rm ../merge/results_images.csv
		fi
fi

cd ..
##########################################################
##########################INSERT DATA BASE ORIGINALDATA#############################
cd send_fileRemote
if [ -d $"input_file" ]; then 
	echo $"Limpiando carpeta input_file para nueva ejecucion"; 
	rm -r input_file;
	mkdir input_file;
else
	echo $"Creando carpeta input_file para la ejecucion";
	mkdir input_file;
fi
cd ../

dayinit=$(date +%A)
horainit=$(date +%H)
mininit=$(date +%M)
year=$(date +%Y)
month=$(date +%m)
namefolder="$year-$month-$dayinit[$horainit:$mininit]"

#./prepare_input.sh $namefolder

python clean.py
if [ "$validateinsert" = 'y' ]; then
	#echo "$namefolder"
	#sudo ssh ubuntu@52.52.75.149 -i ./insert_original_redfin/TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < prepare_input.sh $namefolder
	sudo ssh ubuntu@13.57.62.82 -i ./insert_redfin_property/TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < prepare_input.sh $namefolder	
	
	cd send_fileRemote
	python send_file_remote.py $namefolder #Envia downloaded.csv a servidor remoto 50.18.238.132
	cd ../

	cd insert_redfin_property
	######################################################
	#cp results_redfin.csv ./merge/output_scrapy.csv

	#python worker.py get_zips

	######################################################

	#sudo ssh ubuntu@52.52.75.149 -i ./TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < exe.sh $namefolder
	sudo ssh ubuntu@13.57.62.82 -i ./TunelSsh\(NOBORRAR\)/KUKUN_DATA_TEAM_NOV_2020.pem 'bash -s' < exe.sh $namefolder	
	#./exe.sh $namefolder
	cd ..
fi
#################################################################################################################
dayinit=$(date +%A)
horainit=$(date +%H)
mininit=$(date +%M)
nohup echo $"Day Init $dayinit a las $horainit:$mininit" > timeEnd_redfinpro.txt
