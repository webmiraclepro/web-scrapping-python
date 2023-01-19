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

# import datelist
# from datelist import date_list_entry

#Race Result
#starting webdriver
BASE_URL = "https://racing.hkjc.com/racing/information/Chinese/racing/LocalResults.aspx?RaceDate="
#dates = ["2020-06-07","2020-06-03"]
dates=[
"2023-01-11",
]
xpath_string = [
  "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[3]/p[1]/span[1]",
  "//*[@id='innerContent']/div[2]/div[4]/table/thead/tr/td[1]",
  "//*[@id='innerContent']/div[2]/div[4]/table/thead/tr/td[1]",
  "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[2]/td[3]",
  "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[2]/td[1]",
  "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[2]/td[1]",
  "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[2]/td[1]",
  "//*[@id='innerContent']/div[2]/div[4]/table/tbody/tr[3]/td[1]",
  "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[4]/td[1]",
  "//*[@id='innerContent']/div[2]/div[4]/table/tbody/tr[3]/td[3]",
  "//*[@id='innerContent']/div[2]/div[4]/table/tbody/tr[3]/td[3]",
]

race_entry = []
tableHeader=[
  "HrRaceRaUrComm",
  "Replay",
  "RaceDate",
  "RaceVenue",
  "RaceNo",
  "RaceIndex",
  "RaceGoing",
  "RaceClass",
  "RaceDistance",
  "RaceRatingRange",
  "RaceName",
  "RacePrizeMoney",
  "RaceTrack",
  "RaceCourse",
  "RaceSect1",
  "RaceSect2",
  "RaceSect3",
  "RaceSect4",
  "RaceSect5",
  "RaceSect6",
  "RaceSect51",
  "RaceSect52",
  "RaceSect61",
  "RaceSect62",
  "HrFP",
  "HrNo",
  "HrName",
  "HrBrandNo",
  "HrJockey",
  "HrStable",
  "HrWeight",
  "HrBodyWeight",
  "HrDraw",
  "HrMarginLen",
  "HrPos1",
  "HrPos2",
  "HrPos3",
  "HrPos4",
  "HrPos5",
  "HrPos6",
  "HrTime",
  "HrWinOdds",
  "HrWebID",
  "DateNo",
  "Season",
  "RaceID",
  "SeasonRace",
  ]
sectsmapping = [5, 4, 3, 2, 1, 0]
mapping = [24, 25, 26, 26, 27, 28, 29, 30, 31, 32, 33, 33, 33, 33, 33, 33, 34, 35]
driver_exe = 'chromedriver'
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(driver_exe, options=options)

wait = WebDriverWait(driver, 5)

def check_exists_by_xpath(xpath):
  try:
      driver.find_element(By.XPATH, xpath)
  except NoSuchElementException:
      return False
  return True


def scraping_race_result(table_rows):
  race_raur_comm = ""
  race_replay = ""
  race_date = meet
  race_Sect = []
  race_pos = ["" for i in range(6)]

  for row in table_rows:
    rowEntry = []
    rowEntry.append(race_raur_comm)
    rowEntry.append(race_replay)
    rowEntry.append(race_date)
    for xpath in xpath_string:
      if (check_exists_by_xpath(xpath)):
        tempEl = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        rowEntry.append(tempEl.text)
        pass
      else:
        rowEntry.append("")

    sectEl = driver.find_element(By.XPATH, race_sects_xpath) 
    sects = sectEl.find_elements(By.TAG_NAME, 'td')[::-1]
    race_Sect = ["" for i in range(10)]
    for i in range(len(sects) - 2):
      race_Sect[sectsmapping[i]] = sects[i].text
    
    race_sect51_52 = list(filter(None, race_Sect[4].split("\n")[1].split(" ")))
    race_Sect[6] = race_sect51_52[0]
    race_Sect[7] = race_sect51_52[1]
    race_sect61_62 = list(filter(None, race_Sect[5].split("\n")[1].split(" ")))
    race_Sect[8] = race_sect61_62[0]
    race_Sect[9] = race_sect61_62[1]
    race_Sect[4] = race_Sect[4].split("\n")[0]
    race_Sect[5] = race_Sect[5].split("\n")[0]


    race_venu = list(filter(None, rowEntry[3].split(" ")))
    rowEntry[3] = race_venu[2]
    temp = re.findall(r'\d+', rowEntry[4])
    race_no_index = list(map(int, temp))
    rowEntry[4] = race_no_index[0]
    rowEntry[5] = race_no_index[1]
    race_class_distance_rating = rowEntry[7].split(" - ")
    rowEntry[7] = race_class_distance_rating[0]
    rowEntry[8] = race_class_distance_rating[1]
    rowEntry[9] = re.findall(r'\(([^)]+)\)', race_class_distance_rating[2])[0] if len(race_class_distance_rating) > 2 else ""
    rowEntry[11] = rowEntry[11].split(" ")[1].replace(",", "")
    for sect in race_Sect: rowEntry.append(sect)

    cols = row.find_elements(By.TAG_NAME, 'td')
    for col in cols: rowEntry.append(col.text)
    realEntry = ["" for i in range(47)]
    for i in range(len(realEntry)):
      if i > 41 :
        continue
      if i < 24 :
        realEntry[i] = rowEntry[i]
      else :
        realEntry[i] = rowEntry[mapping[i-24]]
    race_track_course = realEntry[12].split("-")
    realEntry[12] = race_track_course[0] if len(race_track_course) > 1 else realEntry[12]
    realEntry[13] = race_track_course[1] if len(race_track_course) > 1 else realEntry[13]
    realEntry[26] = re.sub(r'\(([^)]*)\)', '', realEntry[26])
    realEntry[27] = re.findall(r'\(([^)]+)\)', realEntry[27])[0]

    race_pos = realEntry[34].split(" ")[::-1]
    for i in range(6):
      if i < len(race_pos):
        realEntry[34 + 5 -i] = race_pos[i]
      else:
        realEntry[34 + 5 -i] = ""
    realEntry[33] = '"' + realEntry[33]
    race_entry.append(realEntry)


"""
Initialize variables: 

Data collected per entry: 
  Racing Date, Racing Number,
  place, horse_no, horse, jockey, trainer, actual_wt,
  declare_horse_wt, draw, lbw, running_pos, finish_time, win_odds
"""

race_sects_xpath = "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[5]"
race_date_list_option_xpath = "//*[@id='selectId']/option"
race_num_index_xpath = "//*[@id='innerContent']/div[2]/div[4]/table/thead/tr/td[1]"
same_day_race_link_xpaths = "/html/body/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr/td/a"
# same_day_race_link_xpaths = "//*[@id='innerContent']/div[2]/div[2]/table/tbody/tr/td/a"
table_row_xpath = "//div[5]/table/tbody/tr"

# Begin grabbing data
for meet in dates:
  print("Scraping: " + meet)
  race_entry = []
  internalRaceCount = 1
  if os.path.isfile('Races_Result_' + str(meet) + '.txt'):
    continue
  else:
    driver.get(BASE_URL + meet)
    driver.implicitly_wait(20)
    # same_day_selel = driver.find_elements(By.XPATH, same_day_race_link_xpaths)
    same_day_selel = wait.until(EC.presence_of_all_elements_located((By.XPATH, same_day_race_link_xpaths)))
    same_day_links = [x.get_attribute("href") for x in same_day_selel]  

    # Get first race - x columns y rows + race name, going, track type
    #tempTableEl = wait.until(EC.presence_of_all_elements_located((By.XPATH, table_row_xpath)))
    #table_rows = tempTableEl

    if not (check_exists_by_xpath(table_row_xpath)):
      continue
    else:
      tempTableEl = wait.until(EC.presence_of_all_elements_located((By.XPATH, table_row_xpath)))
      table_rows = tempTableEl

    scraping_race_result(table_rows)  
      
    # Get other races on same meet
    for same_day_link in same_day_links:
      print("Scraping " + same_day_link)
      internalRaceCount += 1
      driver.get(same_day_link)
      driver.implicitly_wait(5)

      
      if not (check_exists_by_xpath(table_row_xpath)):
        continue
      else:
        table_rows = driver.find_elements(By.XPATH, table_row_xpath)
        
        # Scrape 2nd - n
        scraping_race_result(table_rows)

    # Save file as csv
    res = sorted(race_entry, key = itemgetter(4))
    res.insert(0, tableHeader)
    df = pd.DataFrame(res)
    outname = "Races_Result_" + str(meet)
    outdir = 'c:/Output'
    if not os.path.exists(outdir):
      os.makedirs(outdir)
  
    fullname = os.path.join(outdir, outname)    
    csv_data = df.to_csv("./" + outname + ".txt", index=False)
    df.to_csv("./" + outname + ".csv", header=False, index=False, encoding="utf-8")

    csv_data = df.to_csv(fullname + ".txt", index=False)
    df.to_csv(fullname + ".csv", header=False, index=False, encoding="utf-8")


driver.quit()
