from requests import delete
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime,timedelta
from dateutil import tz
import pandas as pd
import xml.etree.ElementTree as et
import json 
import shutil
from airflow import models
from airflow.operators import bash
from airflow.operators import bash_operator
from airflow.operators import python_operator
from google.cloud import bigquery
import pandas_gbq


DAGS_FOLDER = os.environ["DAGS_FOLDER"]


default_args = {
    'owner': 'Mahadevan Iyer',
    'depends_on_past': False,
    'email': ['raj.iyer3940@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(year=2022, month=11, day=20)
    
}

with models.DAG(
        'composer_big_data_duke',
        catchup=False,
        default_args=default_args,
        schedule_interval='25 1 * * *') as dag:

    def scrape_duke():
        
        def parsing_xml_duke():
            xml_file = path + '/'+file_name
            try:
                xtree = et.parse(xml_file)
                xroot = xtree.getroot() 
                # Auto-detect zones:
                from_zone = tz.tzutc()
                to_zone = tz.tzlocal()

                df_cols = ["Date_Time", "Value"]
                rows = []

                for neighbor in xroot.iter('{http://naesb.org/espi}IntervalReading'):
                    date_time = datetime.utcfromtimestamp(int(neighbor[0][0].text))
                    date_time = date_time.replace(tzinfo=from_zone)
                    date_time = date_time.astimezone(to_zone)
                    date_time = date_time.strftime('%Y-%m-%d T %H:%M')
                    
                    value = float(neighbor[1].text)
                    rows.append({df_cols[0]:date_time,df_cols[1]:value})

                today_energy_usage = pd.DataFrame(rows,columns = df_cols)    
                
                os.remove("Energy Usage.xml")
                #print(today_energy_usage.head(10))
                print("Removed Energy.xml",os.listdir(path))

                today_energy_usage['Account']=fb_name
                
                return today_energy_usage

            except Exception as file_not_found:
                print(f'File not found while parsing: {file_not_found}')
                return pd.DataFrame()

        
        file_name = 'Energy Usage.xml'
        path =os.getcwd()
        client = bigquery.Client()
        query_job = client.query("""SELECT * FROM `duke-energy-big-data-project.Duke_credentials.Duke_credentials` """)
        results = query_job.result() 
        ls=[]
        try:
            os.remove("Energy Usage.xml")
        except Exception as file_not_found_1:
            print(f'File not found at start. Proceeding to get file {file_not_found_1}')

        for row in results:
            print(row.UserId)
            fb_name= row.UserId
            fb_pass=row.Password
            # Initiate the browser
            ct=0
            
            try:
                print(f'Checking chrome Binary {os.listdir(path)}')
                options = webdriver.ChromeOptions()
                prefs = {"download.default_directory":path,'safebrowsing.enabled': 'false'};
                options.add_experimental_option("prefs",prefs);
                options.binary_location= '/usr/bin/google-chrome-stable'
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                # options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1024,768')
                browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
            except Exception as a:
                print(f'Failed to create browser: {a}')
                break

            while ct<=1:
                print(os.listdir(path))
                if file_name in os.listdir(path):
                    print("File found")
                    break
                else:
                    time.sleep(30)
                        
                    try:
                    # Go to Duke Website
                        browser.get('https://p-auth.duke-energy.com/my-account/sign-in')
                        print("Loaded Duke Website")
                        time.sleep(20)

                    except Exception as duke:
                        print(f'Failed to load Duke website: {duke}')
                        ct+=1
                        browser.close()
                        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
                        continue

                    try:
                    # Fill credentials
                        WebDriverWait(browser, 60).until(EC.presence_of_element_located(("name","userId"))).send_keys(fb_name)
                        WebDriverWait(browser, 60).until(EC.presence_of_element_located(("name","userPassword"))).send_keys(fb_pass)
                        print("Filled credentials")
                        time.sleep(5)
                    except Exception as fill_cred:
                        print(f'Failed to fill login credentials: {fill_cred}')
                        ct+=1
                        browser.close()
                        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
                        continue
                    
                    try:
                    # Click Log In
                        WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="mobile-login"]/div[4]/button'))).click()
                        print("Click Login")
                        time.sleep(15)
                    except Exception as login:
                        print(f'Failed to login: {login}') 
                        ct+=1
                        browser.close() 
                        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
                        continue

                    try:                         
                    # Energy bill
                        WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="page-components"]/div[2]/div/div[2]/div[2]/div/div[1]/div[2]/div/div[4]/a'))).click()
                        print("Get energy details")
                        time.sleep(30)
                    except Exception as get_bill:
                        print(f'Failed to open the energy usage page: {get_bill}')
                        ct+=1 
                        browser.close()
                        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
                        continue

                    try: 
                    # Click download my data
                        WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="page-components"]/div[2]/div[4]/div[6]/div/div/div[3]/a'))).click()
                        print("download data")
                    except Exception as download_data:
                        print(f'Failed download: {download_data}') 
                        ct+=1
                        browser.close()
                        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
                        continue
                
                    # Logout
                    try:
                        WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH,'/html/body/header/div/div/section[1]/div[1]/div[2]/div[3]/div/div/button/span[1]'))).click() 
                        time.sleep(5)
                        WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH,'/html/body/header/div/div/section[1]/div[1]/div[2]/div[3]/div/div/ul/li[5]/a/span'))).click()
                        time.sleep(5)
                        browser.close()
                        
                    except Exception as logout:
                        print(f'Failed to logout of browser: {logout}')
                        ct+=1
                        browser.close()
                        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
                        continue
                 
                    if ct==0:
                        print("Proceeding to parsing")
                    else:
                        print(f'Attempting to re-start browser')
                    
                print("Number of retries: -",ct)
                
            print("Got the xml. Now lets parse")
            
            # Parsing
            df= parsing_xml_duke()
            if df.shape[0]<=0:
                print("Job failed for user",fb_name)
            else:
                ls.append(df)
        try:
            df = pd.concat(ls)
            df.to_gbq('duke_usage_data.all_user_usage',project_id= 'duke-energy-big-data-project',if_exists='replace')
        except Exception as failed_job:
            print(f'Job Failed',failed_job)

    scrape_duke = python_operator.PythonOperator(
        task_id='scrape_duke',
        python_callable=scrape_duke)

    scrape_duke
