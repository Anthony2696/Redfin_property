#!/bin/sh

#sudo docker run -it \
#    --mount type=bind,source=/home/anthony/Documentos/workkukun/Redfin.com/redfin_colleted\(Property\)/Redfin_Property/extract_bd_input,target=/app \
#    --name bd_to_csv anthony/insert-redfin:latest

sudo docker run -it \
    --mount type=bind,source=$(pwd),target=/app \
    --name bd_to_csv anthony/insert-redfin:latest
