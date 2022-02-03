import time
import pandas as pd
import datetime
from funtions_bot import initChromeDriver
from funtions_bot import extract_info_properties_url
from funtions_bot import get_df
from funtions_bot import exec_cyberghost
from funtions_bot import search
from funtions_bot import move_to_element
from funtions_bot import get_response
from funtions_bot import exec_cyberghost
from funtions_bot import exec_cyberghost

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from scrapy import Selector
from tqdm import tqdm
####################################
dr = ChromeDriverManager().install()
df,_ = get_df('./input')
list_scrape = pd.DataFrame(columns=[
    'ADDRESS',
    'URL',
    'CITY',
    'ZIP_CODE',
    'STATE',
    "original_id"
])
def load_input(df):
    try:
        #df = pd.read_excel(filename,engine='openpyxl')
        cols = ['ADDRESS','CITY','STATE','ZIP_CODE']#df.columns
        df['combined'] = df[cols].apply(lambda row: '%'.join(row.values.astype(str)), axis=1)
        input_data = df['combined'].to_list()
        
        return input_data
    except Exception as f:
        print("Exception in loading input file: ",f)

def reload():
    driver = initChromeDriver(dr)
    driver.get('https://www.redfin.com')
    return driver

def main():
    try:
        print('START REDFIN BOT ADDRESS')
        #input_data = load_input(df) # Load input 
        #driver = initChromeDriver(dr)
        #driver.get('https://www.redfin.com')
        #search_bar = driver.find_element_by_id("search-box-input")
        # Wait for initialize, in seconds
        
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

            for indx,row in tqdm(list_scrape.iterrows(),desc='Getting Info Properties',total=len(list_scrape)):
                time_init = datetime.datetime.now()
                try:
                    driver = reload()
                    entry = row["ADDRESS"]+'%'+row["CITY"]+'%'+row["STATE"]+'%'+row["ZIP_CODE"]

                    if time_init_cyb == 0:
                        time_init_cyb = datetime.datetime.now()
                        exec_cyberghost(cmd,country2)
                        print('Time_init cyberghost',time_init_cyb,'Time_end cyberghost',time_end_cyb)

                    
                    ## Replace "%" with space to search on site
                    search_entry = entry.replace('%'," ")
                    ## If search is successfull
                    search_bar = driver.find_element_by_id("search-box-input")
                    print('\nConsulting Address:',search_entry)
                    if search(search_entry,driver,search_bar) == True:
                        time.sleep(1)
                        try:
                            wait = WebDriverWait(driver, 5)
                            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'item-title')))
                            
                            url = driver.find_element_by_class_name("item-title").get_attribute('href')

                            response = get_response(url,driver)
                            time.sleep(0.5)
                            if response != '':
                                elems = extract_info_properties_url(response)
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
                                    "build_link_source":url,
                                    "original_id": row["original_id"]
                                },ignore_index=True)
                                debug1 = debug1.append({
                                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                        "reason":'good',
                                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                        "index":indx,
                                        "url":'',
                                        "link_response":url                           
                                    },ignore_index=True)
                                
                                debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                                debug2.to_csv(f'results_properties{attemps}.csv',index=False)
                                print('Property scraped!')
                            else:
                                debug1 = debug1.append({
                                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                        "reason":'url not found',
                                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                        "index":indx,
                                        "url":'',
                                        "link_response":''                           
                                    },ignore_index=True)
                                
                                debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                            
                        except Exception as e:
                            print('Error during Execute:',e)
                            debug1 = debug1.append({
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "reason":'Error during execute',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "index":indx,
                                    "url":'',
                                    "link_response":''                           
                                },ignore_index=True)                            
                            debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                    else:
                        print('Not located Search bar!')
                        html = driver.page_source
                        respObj = Selector(text=html)
                        block1 = respObj.xpath('//form[@id="rf_unblock"]//div[@id="captcha"]').get()
                        block2 = respObj.xpath('//div[@id="txt"]//p[2]//text()').get()
                        if block1 != None:
                            debug1 = debug1.append({
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "reason":'locked',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "index":indx,
                                    "url":'',
                                    "link_response":''                            
                                },ignore_index=True)
                            debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                            print('Property not scraped!, loked')

                        elif block2 != None:
                            if block2.lower().find('complete the captcha') != -1:
                                debug1 = debug1.append({
                                        "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                        "reason":'locked',
                                        "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                        "index":indx,
                                        "url":'',
                                        "link_response":''                            
                                    },ignore_index=True)
                                debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                                print('Property not scraped!, loked')
                        else:
                            debug1 = debug1.append({
                                    "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                                    "reason":'Error during execute',
                                    "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                                    "index":indx,
                                    "url":'',
                                    "link_response":''                            
                                },ignore_index=True)
                            debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                            print('Property not scraped!')

                    time_end_cyb = datetime.datetime.now()
                    if (time_end_cyb - time_init_cyb).total_seconds() >= 420: # Establecer la frecuencia con que rotara la ip (en segundos)
                        time_init_cyb = 0
                    
                    driver.close()

                except Exception as f:
                    print("Exception: ",f )
                    debug1 = debug1.append({
                            "date_create_source":str(time.strftime("%Y-%m-%d-%H:%M:%S")),
                            "reason":'Error during execute',
                            "TIME_DOWNLOAD_IN_SECONDS":(datetime.datetime.now() - time_init).total_seconds(),
                            "index":indx,
                            "url":'',
                            "link_response":''                           
                        },ignore_index=True)
                    
                    debug1.to_csv(f'results_redfin_property{attemps}.csv',index=False)
                    driver.close()
        
            zips_downloaded = [ int(debug1["index"][i]) for i in range(len(debug1["url"])) if (debug1["reason"][i] != 'Error during execute' and debug1["reason"][i] != 'locked')]
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
        
    except Exception as f:
        # print(driver.page_source)
        print("Exception in main function: ",f)

if __name__ == "__main__":
    main()
