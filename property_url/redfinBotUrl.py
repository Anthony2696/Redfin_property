from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from scrapy import Selector
from funtions_bot import get_df
from funtions_bot import initChromeDriver
from funtions_bot import extract_info_properties_url
from funtions_bot import exec_cyberghost
import time
import pandas as pd
import datetime

df,_ = get_df('./input')
list_scrape = pd.DataFrame(columns=[
    'ADDRESS',
    'URL',
    'CITY',
    'ZIP_CODE',
    'STATE',
    "original_id"
])
dr = ChromeDriverManager().install()

if __name__ == "__main__":
    print('START REDFIN BOT URLS')
    cmd = 'sudo cyberghostvpn --traffic --country-code codecountry --connect'
    country = 'AR' #Argentina
    country2 = 'CL' #Chile
    country3 = 'CO' #Colombia
    attemps = 0
    list_scrape = df

    while(attemps < 3 and list_scrape.shape[0] > 0):
        debug2 = pd.DataFrame(columns=[
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
        debug1 = pd.DataFrame(columns=[
            "index",
            "TIME_DOWNLOAD_IN_SECONDS",
            "reason",
            "url",
            "date_create_source",
            "link_response"          
        ])
        attemps += 1
        time_init_cyb = 0
        time_end_cyb = 0

        #-- PROCESS DOWNLOAD CSV --#
        for indx,row in tqdm(list_scrape.iterrows(), desc=f"Extract Information Properties",total=len(list_scrape)):
            try:
                if time_init_cyb == 0:
                    time_init_cyb = datetime.datetime.now()
                    exec_cyberghost(cmd,country2)
                    print('Time_init cyberghost',time_init_cyb,'Time_end cyberghost',time_end_cyb)

                time_init = datetime.datetime.now()
                url = str(row["URL"])

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
                                "url":url,
                                "link_response":link_resp                            
                            },ignore_index=True)
                        debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                        print('Property not scraped!, locked')

                    elif block2 != None:
                        if block2.lower().find('complete the captcha') != -1:
                            debug1 = debug1.append({
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "reason":'locked',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "index":indx,
                                    "url":url,
                                    "link_response":link_resp                            
                                },ignore_index=True)
                            debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                            print('Property not scraped!, locked')
                    else:
                        elems = extract_info_properties_url(respObj)
                        debug2 = debug2.append({
                            'building_parcel_number':elems["building_parcel_number"],
                            'date_create_source':str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                            'number_of_stories':elems["number_of_stories"],
                            'number_of_half_bathrooms':elems["number_of_half_bathrooms"],
                            'number_of_rooms':elems["number_of_rooms"],
                            'garage_type':elems["garage_type"],
                            'heating_type':elems["heating_type"],
                            'building_external_wall':elems["building_external_wall"],
                            'foundation':elems["foundation"],
                            "construction_type":elems["construction_type"],
                            "roof":elems["roof"],
                            "fireplace":elems["fireplace"],
                            "pool":elems["pool"],
                            "zoning":elems["zoning"],
                            "legal_description":elems["legal_description"],
                            "parcel_status":elems["parcel_status"],
                            "n_garage":elems["n_garage"],
                            "n_parking":elems["n_parking"],
                            "builder_name":elems["builder_name"],
                            "Association_fee":elems["Association_fee"],
                            "Additional_fee":elems["Additional_fee"],
                            "PROPERTY_DETAILS":elems["PROPERTY_DETAILS"],
                            "PRICE_INSIGHTS":elems["PRICE_INSIGHTS"],
                            "HOUSE_DESCRIPTION":elems["HOUSE_DESCRIPTION"],
                            "COMMUNITY":elems["COMMUNITY"],
                            "PROPERTY_PRICE":elems["PROPERTY_PRICE"],
                            "property_tax":elems["property_tax"],
                            "property_tax_year":elems["property_tax_year"],    
                            "build_link_source":link_resp,
                            "original_id":row["original_id"]
                        },ignore_index=True)
                        debug1 = debug1.append({
                                "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                "reason":'good',
                                "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                "index":indx,
                                "url":url,
                                "link_response":link_resp                           
                            },ignore_index=True)
                        
                        debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                        debug2.to_csv(f'results_properties{attemps}.csv',index=False)
                        print('Property scraped!')


                    driver.quit()
                except Exception as e:
                    print('***Error Execute***:',e)
                    debug1 = debug1.append({
                            "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                            "reason":'Error during execute',
                            "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                            "index":indx,
                            "url":url,
                            "link_response":link_resp                         
                        },ignore_index=True)
                    debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                    print('Property not scraped!')
                    driver.quit()
                                    
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

        zips_downloaded = [ int(debug1["index"][i]) for i in range(len(debug1["url"])) if (debug1["reason"][i] == 'good')]
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