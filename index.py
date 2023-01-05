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

BASE_URL = "https://racing.hkjc.com/racing/information/English/Racing/RaceCard.aspx?RaceDate="
Race="&RaceNo=1"
dates = [
  "2023-01-05",
]

mapping = [0, 1, 2, 3, 6, 16, 8, 14, 19, 4, 13, 23, 25]
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

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 20)

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
    
    jockey = list(filter(None, re.split("(\-d)|\(|\)", rowEntry[9])))
    rowEntry[9] = jockey[0]
    rowEntry[10] = jockey[1] if len(jockey) > 1 else ""
    if rowEntry[6].endswith("Scratched"):
      rowEntry[6].replace("Scratched", "")
      rowEntry[9] = 'Scratched'
      pass
    

    race_entry.append(rowEntry)

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
    for reservecol in reservecols:
      reserverowEntry.append(reservecol.text)
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
reserve_table_row_xpath ="/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[8]/table/tbody/tr"
table_row_xpath = "//*[@id='racecardlist']/tbody/tr/td/table/tbody/tr"


count = 0
race_name = ""
# Begin grabbing data
for meet in dates:
  driver.get(BASE_URL + meet.replace('-','/')+Race)
  input("Press Enter to continue...")
  print("Scraping Race Card: " + meet)
  race_entry = []
  race_entry.append(tableHeader)
  reserverace_entry = []
  race_standby = []
  internalRaceCount = 1
  count += 1
  if os.path.isfile('Racescard_' + str(meet) + '.txt'):
    continue
  else:
    driver.get(BASE_URL + meet.replace('-','/')+Race)
    driver.implicitly_wait(20)
    same_day_selel = driver.find_elements(By.XPATH, same_day_race_link_xpaths)
    same_day_links = [x.get_attribute("href") for x in same_day_selel] 
    # Get first race - x columns y rows + race name, going, track type
    #if not (check_exists_by_xpath(table_row_xpath)):
    if not (check_exists_by_xpath(racecard_info_1_xpath)):
      continue
    else:


      if (check_exists_by_xpath(race_name_xpath)):
        tempEl = wait.until(EC.presence_of_element_located((By.XPATH, race_name_xpath)))
        race_name = (tempEl.text)
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
            race_name = (tempEl.text)
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
      print(df.head())
      csv_data = df.to_csv("./Racescard_" + str(meet) + ".txt", index=False)
      df.to_csv("./Racescard_" + str(meet) + ".csv", header=False, index=False)
      print("Saved " + str(meet))

driver.quit()

