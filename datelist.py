#import libraries
from bs4 import BeautifulSoup
import requests
import string
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import pandas as pd
import os.path
import re
from selenium.webdriver.chrome.options import Options
from operator import itemgetter

BASE_URL = "https://racing.hkjc.com/racing/information/Chinese/racing/LocalResults.aspx"
date_list_entry = []

driver_exe = 'chromedriver'
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(driver_exe, options=options)

wait = WebDriverWait(driver, 20)

def check_exists_by_xpath(xpath):
  try:
      driver.find_element(By.XPATH, xpath)
  except NoSuchElementException:
      return False
  return True

def getDate(rowtext):
    year = rowtext.split('/')[2]
    month = rowtext.split('/')[1]
    date = rowtext.split('/')[0]
    return str(year + '-' +  month + '-' + date)

def scraping_date_list(table_rows):
    for row in table_rows: date_list_entry.append(getDate(row.text))
    return date_list_entry


race_date_list_option_xpath = "//*[@id='selectId']/option"

date_list_entry = []

if os.path.isfile('Date_List'  + '.txt'):
    pass
else:
    driver.get(BASE_URL)
    driver.implicitly_wait(20)

    tempEl = wait.until(EC.presence_of_all_elements_located((By.XPATH, race_date_list_option_xpath)))
    scraping_date_list(tempEl)

    #Save file as txt
    df = pd.DataFrame(date_list_entry)
    outname = "Date_List"
    outdir = 'c:/Output'
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    fullname = os.path.join(outdir, outname)    
    csv_data = df.to_csv("./" + outname + ".txt", header=False, index=False)

    csv_data = df.to_csv(fullname + ".txt", header=False, index=False)

driver.quit()
