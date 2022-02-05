import time
import pandas as pd
import datetime
import os
import shutil
import boto3
import random
from funtions_bot import initChromeDriver
from funtions_bot import extract_images
from funtions_bot import get_df
from funtions_bot import upload_images
from funtions_bot import exec_cyberghost
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scrapy import Selector
from tqdm import tqdm
from botocore.exceptions import ClientError

####################################
dr = ChromeDriverManager().install()
df,_ = get_df('./input')
list_scrape = pd.DataFrame(columns=[
    'ADDRESS',
    'URL',
    'CITY',
    'ZIP_CODE',
    'STATE'
])

if __name__ == '__main__':
    print('START REDFIN BOT IMAGES')
    folder = str(time.strftime("%Y-%m-%d-%H:%M"))
    cmd = 'sudo cyberghostvpn --traffic --country-code codecountry --connect'
    d = {1:'MX', #Mexico
        2: 'US', #USA
        3: 'ES', #España
        4: 'AR', #Argentina
        5: 'CN' #China
    }
    attemps = 0
    list_scrape = df
    try:
        s3 = boto3.client('s3')
        while(attemps < 3 and list_scrape.shape[0] > 0):
            c = d[random.randint(1,5)]
            debug1 = pd.DataFrame(columns=[
                "index",
                "TIME_DOWNLOAD_IN_SECONDS",
                "reason",
                "images_urls",
                "date_create_source"
            ])
            debug2 = pd.DataFrame(columns=[
                "name",
                "path",
                "original_id"
            ])

            attemps += 1
            time_init_cyb = 0
            time_end_cyb = 0

            #-- PROCESS DOWNLOAD CSV --#
            for indx,row in tqdm(list_scrape.iterrows(), desc=f"Extract Images Properties",total=len(list_scrape)):
                try:
                    #if indx == 2: break
                    if time_init_cyb == 0:
                        time_init_cyb = datetime.datetime.now()
                        exec_cyberghost(cmd,c)
                        print('Time_init cyberghost',time_init_cyb,'Time_end cyberghost',time_end_cyb)

                    time_init = datetime.datetime.now()
                    url = str(row["build_link_source"])
                    
                    folderExists = os.path.isdir("./temp")
                    if folderExists:
                        shutil.rmtree(f"{os.getcwd()}/temp")
                    os.mkdir("./temp")


                    if url != '':
                        print('\n\nconsulting link -> ',url)
                            
                        try:
                            driver = initChromeDriver(dr)
                            driver.get(url)
                            time.sleep(1)
                            html = driver.page_source
                            respObj = Selector(text=html)
                            link_resp = driver.current_url
                            block1 = respObj.xpath('//form[@id="rf_unblock"]//div[@id="captcha"]').get()
                            block2 = respObj.xpath('//div[@id="txt"]//p[2]//text()').get()
                            if block1 != None:
                                debug1 = debug1.append({
                                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                        "reason":'locked',
                                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                        "index":indx,
                                        "images_urls":''
                                    },ignore_index=True)
                                
                                debug1.to_csv(f'results_redfin_propertyImages{attemps}.csv',index=False)
                                print('Property not scraped!, locked')

                            elif block2 != None:
                                if block2.lower().find('complete the captcha') != -1:
                                    debug1 = debug1.append({
                                            "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                            "reason":'locked',
                                            "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                            "index":indx,
                                            "images_urls":''
                                        },ignore_index=True)
                                    
                                    debug1.to_csv(f'results_redfin_propertyImages{attemps}.csv',index=False)
                                    print('Property not scraped!, locked')
                            else:
                                originalid = row["original_id"]
                                images = extract_images(respObj,originalid)
                                if len(images)>0:                                                
                                    debug2 = upload_images(images,folder,s3,debug2,originalid)
                                    debug1 = debug1.append({
                                            "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                            "reason":'good',
                                            "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                            "index":indx,
                                            "images_urls":images
                                        },ignore_index=True)
                                    
                                    debug1.to_csv(f'results_redfin_propertyImages{attemps}.csv',index=False)
                                    debug2.to_csv(f'results_images{attemps}.csv',index=False)
                                    print('Images scraped!')
                                else:
                                    debug1 = debug1.append({
                                            "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                            "reason":'No images',
                                            "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                            "index":indx,
                                            "images_urls":''
                                        },ignore_index=True)
                                    
                                    debug1.to_csv(f'results_redfin_propertyImages{attemps}.csv',index=False)
                                    print('No scraped!')

                            driver.quit()
                        except Exception as e:
                            print('***Error Execute***:',e)
                            debug1 = debug1.append({
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "reason":'Error during execute',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "index":indx,
                                    "images_urls":''
                                },ignore_index=True)
                            debug1.to_csv(f'results_redfin_propertyImages{attemps}.csv',index=False)
                            print('Property not scraped!')
                            driver.quit()

                    folderExists = os.path.isdir("./temp")
                    if folderExists:
                        shutil.rmtree(f"{os.getcwd()}/temp")
                    os.mkdir("./temp")

                    time_end_cyb = datetime.datetime.now()
                    if (time_end_cyb - time_init_cyb).total_seconds() >= 420: # Establecer la frecuencia con que rotara la ip (en segundos)
                        time_init_cyb = 0

                except Exception as e:
                    print('***ERROR***: ',e)            

            #attemps += 1
            #debug.to_csv(f'results_redfin{attemps}.csv',index=False)
            #states_in_list = [ e for e in list_scrape["state_name"] ]
            #cities_in_list = [ e for e in list_scrape["city_name"] ]
            #counties_in_list = [ e for e in list_scrape["county_name"] ]
            #zips_in_list = [ e for e in list_scrape["zip_code"] ]

            zips_downloaded = [ int(debug1["index"][i]) for i in range(len(debug1["images_urls"])) if (debug1["reason"][i] != 'Error during execute' and debug1["reason"][i] != 'locked')]
            """
            states = [ states_in_list[zips_in_list.index(e)] for e in zips_not_downloaded ]
            cities = [ cities_in_list[zips_in_list.index(e)] for e in zips_not_downloaded ]
            counties = [ counties_in_list[zips_in_list.index(e)] for e in zips_not_downloaded ]

            data = {
                'zip_code':zips_not_downloaded,
                'state_name':states,
                'city_name':cities,
                'county_name':counties
            }

            list_scrape = pd.DataFrame(data)
            """
            list_scrape = list_scrape.drop(zips_downloaded,axis=0)

        exec_cyberghost('','','yes')
    except ClientError as e:
        print('Error Connect with AWS',e)