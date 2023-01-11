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
from enum import Enum

# BASE_URL_NO_DATE = "https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx"
BASE_URL_NO_DATE = "https://racing.hkjc.com/racing/information/Chinese/racing/RaceCard.aspx"
mapping = [0, 1, 2, 3, 6, 16, 8, 14, 19, 4, 13, 23, 25]
mappingstarter = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
monthString = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


race_entry = []

 
tableHeader=[
  "HrRacedate",
  "HrRaceNo",
  "HrStarterStatus",
  "HrNo",
  "HrLast6Run",
  "HrClothesColor",
  "HrName",
  "HrBrandNo",
  "HrWeight",
  "HrJockey",
  "HrJockeyHandicap",
  "HrOverWeight",
  "HrDraw",
  "HrStable",
  "HrRating",
  "HrRatingChg",
  "HrBodyWeight",
  "HrBodyWeightChg",
  "HrBestTime",
  "HrAge",
  "HRWFA",
  "HrSex",
  "HrSeasonStakes",
  "HrPriority",
  "HrDaysSinceLastRun",
  "HrGear",
  "HrOwner",
  "HrSire",
  "HrDam",
  "HrImportCat",
  "HrWebID",
  "DateNo",
  "Season",
  "RaceID",
  "SeasonRace",
  "HrRaceCardComm"
  ]

driver_exe = 'chromedriver'
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(driver_exe, options=options)

wait = WebDriverWait(driver, 20)

def isEnglish():
  languageEl = driver.find_element(By.XPATH, language_select_xpath)
  language = languageEl.text
  return True if not (re.search("English", language)) or re.search("English", BASE_URL_NO_DATE) else False

def getMonth(str):
  return monthString.index(str) + 1

def getDate():
  meetEl = driver.find_element(By.XPATH, racecard_info_1_xpath)
  year = ''
  realmonth = ''
  date = ''
  if isEnglish():
    year = meetEl.text.split(',')[2]
    month_date = meetEl.text.split(',')[1]
    month = str(getMonth(list(filter(None, re.split("\s", month_date)))[0]) )
    realmonth = month if len(month) > 1 else "0" + month
    date = list(filter(None, re.split("\s", month_date)))[1]
    pass
    return year + '-' +  realmonth + '-' + date
  else:
    temp = re.findall(r'\d+', meetEl.text.split(',')[0])
    res = list(map(int, temp))
    year = str(res[1])
    month = str(res[2])
    realmonth = month if len(month) > 1 else "0" + month
    date = str(res[3])
    pass
    return year + '-' +  realmonth + '-' + date


def check_exists_by_xpath(xpath):
  try:
      driver.find_element(By.XPATH, xpath)
  except NoSuchElementException:
      return False
  return True

def scraping_starter_data(table_rows, meet, race_name, race_standby):
  for row in table_rows:
    rowEntry = []
    rowEntry.append(meet)
    rowEntry.append(race_name)
    rowEntry.append(race_standby) 
    cols = row.find_elements(By.TAG_NAME, 'td')
    
    for col in cols: rowEntry.append(col.text)
    realEntry = ["" for i in range(36)]
    for i in range(len(rowEntry)):
      realEntry[i] = rowEntry[mappingstarter[i]]

    jockey = list(filter(None, re.split("(\-d)|\(|\)", rowEntry[9])))
    realEntry[22] = realEntry[22].replace(",","")
    last6run = '"' + rowEntry[4]
    realEntry[4] = last6run
    realEntry[9] = jockey[0]
    realEntry[10] = jockey[1] if len(jockey) > 1 else ""
    if realEntry[6].endswith("(Scratched)"):
      tempEntry = realEntry[6]
      realEntry[6] = tempEntry.replace("(Scratched)", "")
      realEntry[9] = 'Scratched'
      pass
    

    race_entry.append(realEntry)

def scraping_stand_starter_data(reserve_table_rows, meet, race_name, race_standby):
  first = True
  for reserverow in reserve_table_rows:
    if first: 
      first = False
      continue
    reserverowEntry = []
    reserverowEntry.append(meet)
    reserverowEntry.append(race_name)
    reserverowEntry.append(race_standby) 
    reservecols = reserverow.find_elements(By.TAG_NAME, 'td')
    for reservecol in reservecols: reserverowEntry.append(reservecol.text)
    last6run = '"' + reserverowEntry[9]
    reserverowEntry[9] = last6run
    realEntry = ["" for i in range(36)]
    for i in range(len(reserverowEntry)):
      realEntry[mapping[i]] = reserverowEntry[i]

    race_entry.append(realEntry)

"""
Initialize variables: 

Data collected per entry: 
HrRacedate,HrRaceNo,HrStarterStatus,HrNo,HrLast6Run,HrClothesColor,HrName,HrBrandNo,HrWeight,HrJockey,HrJockeyHandicap,HrOverWeight,HrDraw,HrStable,HrRating,HrRatingChg,HrBodyWeight,HrBodyWeightChg,HrBestTime,HrAge,HRWFA,HrSex,HrSeasonStakes,HrPriority,HrGear,HrOwner,HrSire,HrDam,HrImportCat,HrWebID,DateNo,Season,RaceID,SeasonRace,HrRaceCardComm


"""

race_name_xpath = "/html/body/div/div[4]/table/thead/tr/td[1]"
same_day_race_link_xpaths = "//*[@id='innerContent']/div[2]/div[3]/table/tbody/tr/td/a"
racecard_info_1_xpath = "//*[@id='innerContent']/div[2]/div[4]/div[2]"
# reserve_table_row_xpath ="/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[8]/table/tbody/tr"
reserve_table_row_xpath ="//*[@id='standbylist']/tbody/tr"
table_row_xpath = "//*[@id='racecardlist']/tbody/tr/td/table/tbody/tr"
click_to_open_xpath = "//*[@id='hplnkColSelect']"
click_refresh_xpath = "//*[@id='ColSelectBody']/form/table/thead/tr/td/table/tbody/tr/td[2]/a"

mystarter_list_input_xpath = "//*[@id='ColSelectBody']/form/table/tbody/tr/td/input"
mystarter_list_xpath = "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[6]/form/table/tbody/tr"
language_select_xpath = "//*[@id='topNav']/div[1]/a[2]"


count = 0
race_name = 0
# Begin grabbing data

driver.get(BASE_URL_NO_DATE)
driver.implicitly_wait(20)
meet = getDate()
click_element = driver.find_element(By.XPATH, click_to_open_xpath)
click_element.click()

if (check_exists_by_xpath(mystarter_list_xpath)):
  starterlist_table_rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, mystarter_list_xpath)))
  pass
starterlist_table_rows = driver.find_elements(By.XPATH, mystarter_list_xpath)

for row in starterlist_table_rows:
  cols = row.find_elements(By.XPATH, mystarter_list_input_xpath)
  for col in cols:
    driver.execute_script("arguments[0].setAttribute('checked','checked')", col)  

refresh_element = driver.find_element(By.XPATH, click_refresh_xpath)
refresh_element.click()

race_entry = []
race_entry.append(tableHeader)
reserverace_entry = []
race_standby = []
internalRaceCount = 1
count += 1
if os.path.isfile('Racescard_' + str(meet) + '.txt'):
  pass
else:
  driver.get(BASE_URL_NO_DATE)
  driver.implicitly_wait(20)
  same_day_selel = driver.find_elements(By.XPATH, same_day_race_link_xpaths)
  same_day_links = [x.get_attribute("href") for x in same_day_selel] 
  # Get first race - x columns y rows + race name, going, track type
  #if not (check_exists_by_xpath(table_row_xpath)):
  if not (check_exists_by_xpath(racecard_info_1_xpath)):
    pass
  else:

    if (check_exists_by_xpath(race_name_xpath)):
      tempEl = wait.until(EC.presence_of_element_located((By.XPATH, race_name_xpath)))
      race_name = int(tempEl.text)
    if not (check_exists_by_xpath(table_row_xpath)):
      rowEntry = []
      rowEntry.append(meet)
      rowEntry.append(race_name)
      race_entry.append(rowEntry)

    else:

      tempTableEl = wait.until(EC.presence_of_all_elements_located((By.XPATH, table_row_xpath)))
      table_rows = tempTableEl

    if (check_exists_by_xpath(reserve_table_row_xpath)):
      tempTableEl2 = wait.until(EC.presence_of_all_elements_located((By.XPATH, reserve_table_row_xpath)))
      reserve_table_rows = tempTableEl2


      race_name = 1
    #race_name = driver.current_url
    #race_name  = same_day_links
      race_standby = "Starter"
      scraping_starter_data(table_rows, meet, race_name, race_standby)
      
      race_standby = "Stand-by Starter"
      scraping_stand_starter_data(reserve_table_rows, meet, race_name, race_standby)

        
    # Get other races on same meet
    for same_day_link in same_day_links:
      print("Scraping Racecard " + same_day_link)
      
      driver.get(same_day_link)
      driver.implicitly_wait(10)

      # Scrape 2nd - n
      #if not (check_exists_by_xpath(table_row_xpath)):
      if not (check_exists_by_xpath(racecard_info_1_xpath)):  
        continue
      else:

        if (check_exists_by_xpath(race_name_xpath)):
          tempEl = wait.until(EC.presence_of_element_located((By.XPATH, race_name_xpath)))
          race_name = int(tempEl.text)
        if not (check_exists_by_xpath(table_row_xpath)):
          rowEntry = []
          rowEntry.append(meet)
          rowEntry.append(race_name)
          race_entry.append(rowEntry)
        else:   
          tempTableEl = wait.until(EC.presence_of_all_elements_located((By.XPATH, table_row_xpath)))
          table_rows = tempTableEl

        if (check_exists_by_xpath(reserve_table_row_xpath)):

          tempTableEl2 = wait.until(EC.presence_of_all_elements_located((By.XPATH, reserve_table_row_xpath)))
          reserve_table_rows = tempTableEl2
        
        table_rows = driver.find_elements(By.XPATH, table_row_xpath)
        race_name += 1
  
        race_standby = "Starter"
        scraping_starter_data(table_rows, meet, race_name, race_standby)
          
        reserve_table_rows = driver.find_elements(By.XPATH, reserve_table_row_xpath)
        race_standby = "Stand-by Starter"
        scraping_stand_starter_data(reserve_table_rows, meet, race_name, race_standby)
        
    # Save file as csv
    df = pd.DataFrame(race_entry)
    outname = "Racescard_" + meet
    outdir = 'c:/Output'
    if not os.path.exists(outdir):
      os.makedirs(outdir)
  
    fullname = os.path.join(outdir, outname)    
    csv_data = df.to_csv("./" + outname + ".txt", index=False)
    df.to_csv("./" + outname + ".csv", header=False, index=False, encoding="utf-8")

    csv_data = df.to_csv(fullname + ".txt", index=False)
    df.to_csv(fullname + ".csv", header=False, index=False, encoding="utf-8")

driver.quit()

