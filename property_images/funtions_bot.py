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
import requests

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

def extract_images(response,oid):
        images_list = []

        photos = response.xpath('//div[@class="InlinePhotoPreview Section pos-rel ThreePhotos"]//div//a//span//img//@src').extract()
        if len(photos)>0:
            for i,photo in enumerate(photos):
                name = str(oid)+'_'+str(i)

                images_list.append({"url":photo,"name":name})
        else:
            photos = response.xpath('//span[@id="MBImageundefined"]//img//@src').extract()
            if len(photos)>0:
                for i,photo in enumerate(photos):
                    name = str(oid)+'_'+str(i)

                    images_list.append({"url":photo,"name":name})

        if len(images_list)>0:
            print('Extract images successfully!')
            return images_list
        
        print('Images not found')
        return images_list

def upload_images(list_images,folder,s3,debug,oid):
    """
        Debe tener preconfigurado las credenciales de AWS
        en su carpeta raiz: /.aws
    """
    bucket = 'kukun-property-images'
    folder = str(folder).replace(':','%3A')
    try:
        for image in list_images:
            try:
                r = requests.get(image["url"])
                open(f'./temp/{image["name"]}','wb').write(r.content)

                with open(f'./temp/{image["name"]}','rb') as f:
                    s3.upload_fileobj(f,bucket,f'Redfin_property/{folder}/{image["name"]}.png')
                    debug = debug.append({
                        "original_id":oid,
                        "path":f'https://{bucket}.s3.us.west-1.amazonaws.com/Redfin_property/{folder}/{image["name"]}.png',
                        "name":image["name"]
                    },ignore_index=True)                    
                    print('upload sucessfully!')

            except Exception as e:
                print('Except upload image:',e,'en la image',image["url"],image["names"])
        return debug
    except Exception as e:
        print('Except Boto3 client',e)
        return debug