#!/bin/bash
#########################################################################################################
#Script Bash para el automatizado de scrapy, normalizado y insercion de datos desde la pagina Redfin.com
#Anthony Briceño Fecha de realizacion: 2021-09-22, correo anthony.briceno@mykukun.com

./init.sh
./run.sh
sudo docker rm $(sudo docker ps -a -f status=exited -f name=bd_to_csv -q)
