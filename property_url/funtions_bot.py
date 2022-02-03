from selenium import webdriver
from selenium_stealth import stealth
from os import listdir
from scrapy import Selector
import os
import time
import pandas as pd
import sys
import re
from subprocess import TimeoutExpired,Popen

def exec_cyberghost(cmd,country,stop=None):
    try:
        if stop == None:
            cmd = cmd.replace('codecountry',str(country))
            cmd = cmd.split(' ')
            proc = Popen(cmd)
            print('Execute command: ',cmd)
        else:
            proc = Popen(['sudo','cyberghostvpn','--stop'])
        try:            
            proc.wait(60)
        except TimeoutExpired as e:
            print('TimeoutExpired Execute cyberghost',e)
            os.kill(proc.pid,15)

    except Exception as e:
        print('Error Exception: ',e)

def get_ip():
    version = sys.version[0]

    if version == '2':
        import urllib2 as urllib
    else:
        import urllib.request as urllib

    url1 = None
    url2 = None
    servidor1 = 'http://www.soporteweb.com'
    servidor2 = 'http://www.ifconfig.me/ip'

    consulta1 = urllib.build_opener()
    consulta1.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0')] 
    consulta2=consulta1

    try:
        url1 = consulta1.open(servidor1, timeout=17)
        respuesta1 = url1.read()
        if version == '3':
            try:
                respuesta1 = respuesta1.decode('UTF-8')
            except UnicodeDecodeError:
                respuesta1 = respuesta1.decode('ISO-8859-1')

        url1.close()
        #print('Servidor1:'+respuesta1)
        return respuesta1
    
    except:
        print('Falló la consulta ip a '+servidor1)
        try:
            url2 = consulta2.open(servidor2, timeout=17)
            respuesta2 = url2.read()
            if version == '3':
                try:
                    respuesta2 = respuesta2.decode('UTF-8')
                except UnicodeDecodeError:
                    respuesta2 = respuesta2.decode('ISO-8859-1')

            url2.close()
            #print('Servidor2:'+respuesta2)
            return respuesta2
        except:
            #print('Falló la consulta ip a '+servidor2)
            return ''

def find_proxie_valid(PROXIES,pxy,link):
    if pxy == None:
        driver = initChromeDriver()
        driver.get(link)
        time.sleep(1)
        html = driver.page_source
        respObj = Selector(text=html)
        link_resp = driver.current_url
        return pxy,PROXIES,respObj,link_resp,driver

    while(True):
        testp = False
        response = ''
        link_resp = ''
        if pxy != '':
            testp,response,link_resp,driver = test_proxie(link,pxy)

        if testp == True:
            print('proxie good!')
            return pxy,PROXIES,response,link_resp,driver

        while(len(PROXIES)>0 and testp == False):
            PROXIES,pxy = rotate_proxie(PROXIES,pxy)
            if len(PROXIES)>0:
                PROXIES.pop(0)
                testp,response,link_resp,driver = test_proxie(link,pxy)

            if testp == True:
                print('good proxie!')
                return pxy,PROXIES,response,link_resp,driver       
        
        if len(PROXIES) == 0:
            print('Generando nueva lista PROXIES')
            PROXIES,pxy = create_list_proxies()

def test_proxie(link,pxy):
    print('Testing proxie: ',pxy)
    #str(input('presione ENTER para continuar'))
    try:
        html = ''
        driver = initChromeDriver(pxy)
        driver.set_page_load_timeout(60)
        driver.get(link)
        time.sleep(1)       
        html = driver.page_source
        xpath = '//div[@class="InputBox"]//input[@id="search-box-input"]'
        respObj = Selector(text=html)
        search_box = respObj.xpath(xpath).extract_first()
        if search_box != None:
            return True,respObj,driver.current_url,driver
        
        driver.quit()
    except Exception as e:
        print('*WARNING* ',e)
        driver.quit()

    return False,'','',''

def rotate_proxie(PROXIES,pxy):
    if str(pxy) == str(PROXIES[0]):
        PROXIES.pop(0)
        if len(PROXIES)>0:
            return PROXIES,PROXIES[0]
        else:
            return [],''
     
    return PROXIES,PROXIES[0]

def create_list_proxies():
    driver = initChromeDriver()
    driver.get("https://free-proxy-list.net/")

    PROXIES = []
    html = driver.page_source
    respObj = Selector(text=html)
    table_proxies = respObj.xpath("//section[@id='list']//table//tbody//tr")

    for row in table_proxies:
        ip_addr = row.xpath('td[1]//text()').extract_first()
        port = row.xpath('td[2]//text()').extract_first()

        if ip_addr != None and port != None:
            ip_addr = clean(ip_addr)
            port = clean(port)
            PROXIES.append(ip_addr+":"+port)

    driver.quit()
    if len(PROXIES)>0:
        return PROXIES,PROXIES[0]
    else:
        return [],''

def clean(cadena):
    cadena = str(cadena)
    cadena = cadena.strip()     
    cadena = cadena.replace(',','').replace('<','').replace('>','')
    cadena = cadena.replace('*','').replace('(','').replace(')','')
    cadena = cadena.replace('\n','')
    cadena = cadena.replace('\r','')
    cadena = cadena.replace('\t','')
    cadena = cadena.replace(';','')
    cadena = cadena.replace('$','')
    cadena = cadena.replace('%','percent')
    cadena = cadena.replace('"','')
    cadena = cadena.replace('\xa0','')
    cadena = cadena.replace('&amp','&')
    
    if cadena.lower() == 'nan':
        cadena = cadena.lower().replace('nan','')
    if cadena.lower() == 'none':
        cadena = cadena.lower().replace('none','')
    if cadena.lower() == 'n/a':
        cadena = ''
    if cadena.lower() == 'unknown':
        cadena = ''
    if cadena.lower() == 'unassigned':
        cadena = ''

    cadena = cadena.strip()
    return cadena

#-- Inicializar chrome driver --#
def initChromeDriver(dr,proxie=None):

    options = webdriver.ChromeOptions()
    #ua = UserAgent()
    #userAgent = ua.random
    # -- Descomentar la siguiente linea, para ocultar el navegador --#
    options.add_argument('--headless')
    #-- Descomentar las siguientes dos lineas en caso de ejecutar en MAC/LINUX  --#
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')
    options.add_argument("--start-maximized")
    options.add_argument('ignore-certificate-errors') #ignore certificate errors for google chrome
    # -- USO DE PROXIES -- #
    if proxie != None:
        options.add_argument(f'--proxy-server={proxie}')
    #options.add_argument(f'user-agent={userAgent}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(executable_path=dr, options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    return driver

def get_df(folder):
    try:
        for file in listdir(folder):
            if '.csv' in file and '.~lock' not in file:
                df = pd.read_csv('{}/{}'.format(folder,file),dtype=str,keep_default_na=False)
                print('\tAbriendo',file)
                return df,file
        return [],''
    except: return [],''

def extract_info_properties_url(response):
    #PROPERTY INFORMATION
    """
    addr = self.clean(self.df["ADDRESS"][data["index"]])
    city = self.clean(self.df["CITY"][data["index"]])
    zipc = self.clean(self.df["ZIP OR POSTAL CODE"][data["index"]])
    area = self.clean(self.df["LOT SIZE"][data["index"]])
    b_size = self.clean(self.df["SQUARE FEET"][data["index"]])
    sub_cate = self.clean(self.df["PROPERTY TYPE"][data["index"]])
    beds = self.clean(self.df["BEDS"][data["index"]])
    baths = self.clean(self.df["BATHS"][data["index"]])
    state = self.clean(self.df["STATE OR PROVINCE"][data["index"]])
    year_b = self.clean(self.df["YEAR BUILT"][data["index"]])
    lat = self.clean(self.df["LATITUDE"][data["index"]])
    lon = self.clean(self.df["LONGITUDE"][data["index"]])
    price_sqft = self.clean(self.df["$/SQUARE FEET"][data["index"]])
    parcel_status = self.clean(self.df["STATUS"][data["index"]])

    b_size = response.xpath('//div[@class="home-main-stats-variant"]//div[@class="stat-block sqft-section"][contains(div,"Sq")]//span//text()').extract_first()
    if b_size != None:
        try:
            b_size = float(self.clean(b_size))
        except: b_size = ''
    else: b_size = ''

    area = response.xpath('//div[contains(span,"Lot Size")]//span[2]//text()').extract_first()
    if area != None:
        area = self.clean(area)
        area = area.lower().replace('acres','acres').replace('sq. ft.','sqft')
    else: 
        area = response.xpath('//div[@id="basicInfo"]//div[@class="table-row"][contains(span,"Lot Size")]//div//text()').extract_first()
        if area != None:
            area = self.clean(area)
            area = area.lower().replace('acres','acres').replace('sq. ft.','sqft')
        else: area = ''

    if not 'sqft' in area and not 'acres' in area: area = ''

    year_b = response.xpath('//div[contains(span,"Year Built")]//span[2]//text()').extract_first()
    if year_b != None:
        year_b = self.clean(year_b)
    else: 
        year_b = response.xpath('//div[@id="basicInfo"]//div[@class="table-row"][contains(span,"Year Built")]//div//text()').extract_first()
        if year_b != None:
            year_b = self.clean(year_b)
        else: year_b = ''

    if not re.search(r'\d{4}',year_b): year_b = ''

    time_on_redfin = response.xpath('//div[contains(span,"Time on Redfin")]//span[2]//text()').extract_first()
    if time_on_redfin != None:
        time_on_redfin = self.clean(time_on_redfin)
    else: time_on_redfin = ''

    mls = response.xpath('//div[contains(span,"MLS#")]//span[2]//text()').extract_first()
    if mls != None:
        mls = self.clean(mls)
    else: mls = ''

    hoa_dues = response.xpath('//div[@class="keyDetailsList"]//div[contains(span,"HOA Dues")]//span[2]//text()').extract_first()
    if hoa_dues != None:
        hoa_dues = self.clean(hoa_dues)
    else: hoa_dues = ''

    addr = response.xpath('//h1[@class="homeAddress"]//div[@class="street-address"]//text()[1]').extract_first()
    if addr != None:
        addr = self.clean(addr)
        if not re.search(r'^(\d+\S*\s(?:\S\s?)+)',addr):
            addr = ''
    else: addr = ''

    group_rest_addr = response.xpath('//h1[@class="homeAddress"]//div[@class="dp-subtext"]//text()').extract()
    found_state = [x for x in group_rest_addr if self.get_state(self.clean(x)) == True]
    found_zip = [x for x in group_rest_addr if (x.isdigit()==True and len(x)==5)]
    city = ''
    zipc = ''
    state = ''
    if len(found_state) == 1:
        state = self.clean(found_state[0])
    if len(found_zip) > 0:
        zipc = self.clean(found_zip[0])

    rest_addr = ''.join(group_rest_addr)
    split_addr = rest_addr.split(',')
    if len(split_addr)==2:
        city = self.clean(split_addr[0])
    else:
        city = self.clean(rest_addr.replace(state,'').replace(zipc,''))

    sub_cate = response.xpath('//div[contains(span,"Property Type")]//span[2]//text()').extract_first()
    if sub_cate != None:
        sub_cate = self.clean(sub_cate)
    else: sub_cate = ''

    category = ''
    m_cat = re.findall(r'residential|residence|resident',sub_cate.lower())
    if len(m_cat)>0:
        category = 'residential'
    else:
        m_cat = re.findall(r'commercial|commerce',sub_cate.lower())
        if len(m_cat)>0:
            category = 'commercial'
    
    baths = response.xpath('//div[@class="home-main-stats-variant"]//div[@class="stat-block baths-section"][contains(span,"Bath")]//div//text()').extract_first()
    if baths != None:
        baths = self.clean(baths)
        if baths.find('.') != -1:
            try:
                baths = self.clean(round(float(baths)))
            except: baths = ''
        else:
            try:
                baths = self.clean(int(baths))
            except: baths = ''
    else: baths = ''

    beds = response.xpath('//div[@class="home-main-stats-variant"]//div[@class="stat-block beds-section"][contains(span,"Bed")]//div//text()').extract_first()
    if beds != None:
        beds = self.clean(beds)
        if beds.find('.') != -1:
            try:
                beds = self.clean(round(float(beds)))
            except: beds = ''
        else:
            try:
                beds = self.clean(int(beds))
            except: beds = ''
    else: beds = ''

    lat = response.xpath('//li[contains(span,"Latitude:")]//span//span//text()').extract_first()
    if lat != None:
        lat = self.clean(lat)
    else: lat = ''

    lon = response.xpath('//li[contains(span,"Longitude:")]//span//span//text()').extract_first()
    if lon != None:
        lon = self.clean(lon)
    else: lon = ''
    """
    price_sqft = response.xpath('//div[contains(span,"Price/Sq.Ft")]//span[2]//text()').extract_first()
    if price_sqft != None:
        price_sqft = clean(price_sqft)
    else: price_sqft = ''

    house_description = response.xpath('//div[@id="marketing-remarks-scroll"]//p//span//text()').extract_first()
    if house_description != None:
        house_description = clean(house_description)
    else: house_description = ''

    parcel_status = response.xpath('//div[contains(span,"Status")]//span[2]//div//span//text()').extract_first()
    if parcel_status != None:
        parcel_status = clean(parcel_status)
    else: parcel_status = ''

    property_style = response.xpath('//div[contains(span,"Style")]//span[2]//text()').extract_first()
    if property_style != None:
        property_style = clean(property_style)
    else: property_style = '' 

    community = response.xpath('//div[contains(span,"Community")]//span[2]//text()').extract_first()
    if community != None:
        community = clean(community)
    else: community = ''

    table_price_insights = response.xpath('//div[@class="keyDetailsList"][2]//div[@class="keyDetail font-weight-roman font-size-base"]')
    price_insights = ''
    c=0
    if len(table_price_insights)>0:
        for item in table_price_insights:
            title = item.xpath('span[1]//div//span//text()').extract_first()
            if title != None:
                title = clean(title)
            else:
                title = item.xpath('span[1]//text()').extract_first()
                if title != None:
                    title = clean(title)
                else: title = 'title not recognized'

            value = item.xpath('span[2]//text()').extract_first()
            if value != None:
                value = clean(value)
            else: value = 'unidentified'

            if title.lower() == 'price/sq.ft' and price_sqft != '': continue

            if c == 0:
                price_insights = title+': '+value
                c+=1
            else:
                price_insights += '|'+title+': '+value
                c+=1

    if ((not 'list price:' in price_insights.lower()) and (not 'redfin estimate:' in price_insights.lower()) and (price_sqft == '') 
        and (not 'est. mo. payment:' in price_insights.lower()) and (not 'buyer\'s brokerage compensation:' in price_insights.lower())):
        price_insights = ''

    property_details_container = response.xpath('//div[@id="propertyDetails-collapsible"]//div[@class="sectionContentContainer expanded"]//div[@class="amenities-container"]')
    property_details_headers = property_details_container.xpath('div[@class="super-group-title"]')
    property_details_content = property_details_container.xpath('div[@class="super-group-content"]')
    property_details = ''
    c1 = 0
    if len(property_details_headers) >0 and (len(property_details_headers)==len(property_details_content)):
        for i,header in enumerate(property_details_headers):
            header_title = header.xpath('text()').extract_first()
            if header_title != None:
                header_title = clean(header_title)
            else: header_title = 'unidentified header'

            sub_groups = property_details_content[i].xpath('div[@class="amenity-group"]')
            content_group = ''
            c2=0
            if len(sub_groups)>0:
                for amenity in sub_groups:
                    title_amenity = amenity.xpath('h3//div//div//span//text()').extract_first()
                    if title_amenity != None:
                        title_amenity = clean(title_amenity)
                    else:
                        title_amenity = amenity.xpath('ul//div//h3//text()').extract_first()
                        if title_amenity != None:
                            title_amenity = clean(title_amenity)
                        else: title_amenity = 'unidentified title'

                    list_content_amenity = amenity.xpath('ul//li[@class="entryItem"]')
                    list_content_amenity2 = amenity.xpath('ul//li[@class="entryItem "]')

                    list_content_amenity.extend(list_content_amenity2)
                    content_amenity = ''
                    c3 = 0

                    if len(list_content_amenity)>0:
                        for item in list_content_amenity:
                            texts = item.xpath('span//text()').extract()
                            if len(texts)>0:
                                text = ''.join(texts)

                                if c3 == 0:
                                    content_amenity = clean(text)
                                    c3+=1
                                else:
                                    content_amenity += ','+clean(text)
                                    c3 += 1

                    if content_amenity != '':
                        if c2 == 0:
                            content_group = title_amenity+'<'+content_amenity+'>'
                            c2+=1
                        else:
                            content_group += '&&'+title_amenity+'<'+content_amenity+'>'
                            c2+=1

            if content_group != '':
                if c1 == 0:
                    property_details = header_title+'('+content_group+')'
                    c1+=1
                else:
                    property_details += '|'+header_title+'('+content_group+')'
                    c1+=1

    property_price = response.xpath('//div[@class="stat-block beds-section"][contains(div[1],"$")]//div[@class="statsValue"]//text()').extract_first()
    if property_price != None:
        property_price = clean(property_price)
    else: property_price = ''

    h_baths = response.xpath('//li[contains(span,"# of Baths (1/2)")]//span//span//text()').extract_first()
    if h_baths != None:
        h_baths = clean(h_baths)
        if h_baths.find('.') != -1:
            try:
                h_baths = clean(round(float(h_baths)))
            except: h_baths = ''
        else:
            try:
                h_baths = clean(int(h_baths))
            except: h_baths = ''
    else: h_baths = ''

    rooms = response.xpath('//li[contains(span,"Room Count:")]//span//span//text()').extract_first()
    if rooms != None:
        rooms = clean(rooms)
        if rooms.find('.') != -1:
            try:
                rooms = clean(round(float(rooms)))
            except: rooms = ''
        else:
            try:
                rooms = clean(int(rooms))
            except: rooms = ''
    else: 
        rooms = response.xpath('//li[contains(span,"Rooms:")]//span//span//text()').extract_first()
        if rooms != None:
            rooms = clean(rooms)
            if rooms.find('.') != -1:
                try:
                    rooms = clean(round(float(rooms)))
                except: rooms = ''
            else:
                try:
                    rooms = clean(int(rooms))
                except: rooms = ''
        else: rooms = ''

    fireplaces = response.xpath('//li[contains(span,"# of Fireplaces:")]//span//span//text()').extract_first()
    if fireplaces != None:
        fireplaces = clean(fireplaces)
    else: 
        fireplaces = response.xpath('//li[contains(span//span,"Fireplace")]//span//span//text()').extract_first()
        if fireplaces != None:
            fireplaces = clean(fireplaces)
            mf = re.findall(r'(\d+)\s(fireplaces|fireplace)',fireplaces.lower())
            if len(mf) > 0:
                fireplaces = mf[0][0]
            else: 
                if 'has fireplace' in fireplaces.lower():
                    fireplaces = 'Y'
                else: fireplaces = ''
        else: 
            fireplaces = response.xpath('//li[contains(span,"Has Fireplace")]//span//span//text()').extract_first()
            if fireplaces != None: fireplaces = 'Y'
            else: fireplaces = ''

    heating = response.xpath('//li[contains(span,"Heating System:")]//span//span//text()').extract_first()
    if heating != None:
        heating = clean(heating)
    else: 
        heating = response.xpath('//li[contains(span//span,"Heating")]//span//span//text()').extract_first()
        if heating != None:
            heating = clean(heating)
            if 'has heating' in heating.lower():
                heating = 'Y'
            else: heating = ''
        else: 
            heating = response.xpath('//li[contains(span,"Has Heating")]//span//span//text()').extract_first()
            if heating != None:
                heating = 'Y'
            else: heating = ''

    garage = response.xpath('//li[contains(span,"Garage:")]//span//span//text()').extract_first()
    if garage != None:
        garage = clean(garage)
    else: 
        garage = response.xpath('//li[contains(span,"Attached Garage")]//span//span//text()').extract_first()
        if garage != None:
            garage = clean(garage)
        else: 
            garage = response.xpath('//li[contains(span,"Has Garage")]//span//span//text()').extract_first()
            if garage != None: garage = 'Y'
            else: garage = ''

    stories = response.xpath('//li[contains(span,"Stories:")]//span//span//text()').extract_first()
    if stories != None:
        stories = clean(stories)
        try:
            stories = clean(float(stories))
        except: stories = ''
    else: 
        stories = response.xpath('//li[contains(span,"Stories")]//span//span//text()').extract_first()
        if stories != None:
            stories = clean(stories)
            try:
                stories = clean(float(stories))
            except: stories = ''
        else: 
            stories = ''

    roof = response.xpath('//li[contains(span,"Roof:")]//span//span//text()').extract_first()
    if roof != None:
        roof = clean(roof)
    else: 
        roof = response.xpath('//li[contains(span//span,"Roof")]//span//span//text()').extract_first()
        if roof != None:
            roof = clean(roof)
            if len(roof)>30: roof = ''
        else: 
            roof = response.xpath('//li[contains(span,"Roof")]//span//span//text()').extract_first()
            if roof != None:
                roof = clean(roof)
                if len(roof)>30: roof = ''
            else: rooms = ''

    foundation = response.xpath('//li[contains(span,"Foundation:")]//span//span//text()').extract_first()
    if foundation != None:
        foundation = clean(foundation)
    else: 
        foundation = response.xpath('//li[contains(span,"Foundation")]//span//span//text()').extract_first()
        if foundation != None:
            foundation = clean(foundation)
            if len(foundation)>30: foundation = ''
        else: foundation = ''

    legal = response.xpath('//li[contains(span,"Legal Lot Description:")]//span//span//text()').extract_first()
    if legal != None:
        legal = clean(legal)
    else: 
        legal = response.xpath('//li[contains(span,"Legal Description:")]//span//span//text()').extract_first()
        if legal != None:
            legal = clean(legal)
        else: legal = ''

    ext_wall = response.xpath('//li[contains(span,"Exterior Wall:")]//span//span//text()').extract_first()
    if ext_wall != None:
        ext_wall = clean(ext_wall)
    else: 
        ext_wall = response.xpath('//li[contains(span,"Exterior:")]//span//span//text()').extract_first()
        if ext_wall != None:
            ext_wall = clean(ext_wall)
        else: ext_wall = ''

    num_garage = response.xpath('//li[contains(span,"# of Garage Spaces:")]//span//span//text()').extract_first()
    if num_garage != None:
        num_garage = clean(num_garage)
        if num_garage.find('.') != -1:
            try:
                num_garage = clean(round(float(num_garage)))
            except: num_garage = ''
        else:
            try:
                num_garage = clean(int(num_garage))
            except: num_garage = ''
    else:
        num_garage = response.xpath('//li[contains(span,"# of Garage")]//span//span//text()').extract_first()
        if num_garage != None:
            num_garage = clean(num_garage)
            if num_garage.find('.') != -1:
                try:
                    num_garage = clean(round(float(num_garage)))
                except: num_garage = ''
            else:
                try:
                    num_garage = clean(int(num_garage))
                except: num_garage = ''
        else: num_garage = ''

    num_park = response.xpath('//li[contains(span,"# of Parking Spaces")]//span//span//text()').extract_first()
    if num_park != None:
        num_park = clean(num_park)
        if num_park.find('.') != -1:
            try:
                num_park = clean(round(float(num_park)))
            except: num_park = ''
        else:
            try:
                num_park = clean(int(num_park))
            except: num_park = ''
    else: 
        num_park = response.xpath('//li[contains(span,"# of Parking")]//span//span//text()').extract_first()
        if num_park != None:
            num_park = clean(num_park)
            if num_park.find('.') != -1:
                try:
                    num_park = clean(round(float(num_park)))
                except: num_park = ''
            else:
                try:
                    num_park = clean(int(num_park))
                except: num_park = ''
        else: num_park = ''

    builder = response.xpath('//li[contains(span,"Builder Name:")]//span//span//text()').extract_first()
    if builder != None:
        builder = clean(builder)
    else: builder = ''

    tax = response.xpath('//li[contains(span,"Tax Amount")]//span//span//text()').extract_first()
    if tax != None:
        tax = clean(tax)
    else: 
        tax = response.xpath('//li[contains(span,"Tax:")]//span//span//text()').extract_first()
        if tax != None:
            tax = clean(tax)
        else: 
            tax = response.xpath('//li[contains(span,"Taxes:")]//span//span//text()').extract_first()
            if tax != None:
                tax = clean(tax)
            else: tax = ''

    tax_year = response.xpath('//li[contains(span,"Tax Year:")]//span//span//text()').extract_first()
    if tax_year != None:
        tax_year = clean(tax_year)
    else: 
        tax_year = response.xpath('//li[contains(span,"Tax Year")]//span//span//text()').extract_first()
        if tax_year != None:
            tax_year = clean(tax_year)
        else: 
            tax_year = response.xpath('//li[contains(span,"Assessment Year")]//span//span//text()').extract_first()
            if tax_year != None:
                tax_year = clean(tax_year)
            else: tax_year = ''

    fee_assoc = response.xpath('//li[contains(span,"Assocation Fee:")]//span//span//text()').extract_first()
    if fee_assoc != None:
        fee_assoc = clean(fee_assoc)
    else: fee_assoc = ''

    fee_addi = response.xpath('//li[contains(span,"Additional Fee:")]//span//span//text()').extract_first()
    if fee_addi != None:
        fee_addi = clean(fee_addi)
    else: fee_addi = ''

    zoni = response.xpath('//li[contains(span,"Zoning:")]//span//span//text()').extract_first()
    if zoni != None:
        zoni = clean(zoni)
    else: 
        zoni = response.xpath('//li[contains(span,"Zoning Code:")]//span//span//text()').extract_first()
        if zoni != None:
            zoni = clean(zoni)
        else: zoni = ''

    pool = response.xpath('//li[contains(span,"Has Pool")]//span//span//text()').extract_first()
    if pool != None:
        pool = 'Y'
    else: pool = ''

    apn = response.xpath('//li[contains(span,"Parcel Number:")]//span//span//text()').extract_first()
    if apn != None:
        apn = '#'+clean(apn)
        if not re.search(r'\d+',apn):
            apn = ''
    else: 
        apn = response.xpath('//div[@id="basicInfo"]//div[contains(span,"APN")]//div//text()').extract_first()
        if apn != None:
            apn = '#'+clean(apn)
            if not re.search(r'\d+',apn):
                apn = ''

        else: apn = ''

    #debug["building_street_address"] = addr
    #debug["city_code"] = city
    #debug["state_code"] = state
    #debug["zip_code"] = zipc
    #debug["building_latitude"] = lat
    #debug["building_longitude"] = lon
    #debug["building_category"] = category
    #debug["building_sub_category_code"] = sub_cate
    #debug["number_of_bedrooms"] = beds
    #debug["number_of_bathrooms"] = baths
    #debug["building_size_sqft"] = b_size
    #debug["lot_size_sqft"] = area
    #debug["year_built"] = year_b
    #debug["price_sqft"] = price_sqft
    #debug["Time_On_Redfin"] = time_on_redfin
    #debug["MLS"] = mls
    #debug["HOA_DUES"] = hoa_dues
    debug = dict()
    debug["building_parcel_number"] = apn
    debug["parcel_status"] = parcel_status
    debug["n_garage"] = num_garage
    debug["n_parking"] = num_park
    debug["builder_name"] = builder
    debug["Association_fee"] = fee_assoc
    debug["Additional_fee"] = fee_addi
    debug["property_tax"] = tax
    debug["property_tax_year"] = tax_year
    debug["PROPERTY_DETAILS"] = property_details
    debug["PRICE_INSIGHTS"] = price_insights
    debug["HOUSE_DESCRIPTION"] = house_description
    debug["garage_type"] = garage
    debug["heating_type"] = heating
    debug["building_external_wall"] = ext_wall
    debug["foundation"] = foundation
    debug["construction_type"] = property_style
    debug["roof"] = roof
    debug["fireplace"] = fireplaces
    debug["zoning"] = zoni
    debug["legal_description"] = legal
    debug["number_of_half_bathrooms"] = h_baths
    debug["number_of_rooms"] = rooms
    debug["number_of_stories"] = stories
    debug["COMMUNITY"] = community
    debug["PROPERTY_PRICE"] = property_price
    debug["pool"] = pool
    return debug
