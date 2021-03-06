# %%
from selenium import webdriver
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver.chrome.options import Options
from variables import *
import re
import time
from datetime import datetime , timedelta

# #Global Variables

url = 'https://www.profession.hu/'
jobs = {
    'Keyword': [],
    'Indicator': [],
    'JobId': [],
    'Position Name': [],
    'Position Description': [],
    'Position Link': [],
    'Position Posted Time': []

}

#Sql database creation

databasename = str(pd.to_datetime("today").date()) + ' proffesion_hu.db'
engine = create_engine('sqlite:///' + databasename, echo=False)

#Job function to append elements to the dictionary


def job():
    regex = "(\d*(?=\/optimum))|(\d*(?=\?keyword)|(\d*(?=\/pro)))"
    # Job cards information.
    jobofferlist = driver.find_elements_by_css_selector(
        'h2.job-card__title > a')
    jobofferpostinglist = driver.find_elements_by_css_selector(
        'div.job-card__date')
    joboffertext = driver.find_elements_by_class_name('list_tasks')

    jobPositionNameList = [jobofferlist[i].text for i in range(
        len(jobofferlist))]  # Position name
    jobPositionLinkList = [jobofferlist[i].get_attribute(
        'href') for i in range(len(jobofferlist))]  # Position Link
    jobPositionPostTime = [jobofferpostinglist[i].text for i in range(
        len(jobofferpostinglist))]  # Position posted time
    jobPositionPartText = [joboffertext[i].text for i in range(
        len(joboffertext))]  # Position Description

    for i in range(len(jobPositionNameList)):
        indexincrement = len(jobs['Indicator'])

        jobs['Keyword'].append(elem)
        jobs['Indicator'].append(indexincrement)

        x = re.findall(regex,jobPositionLinkList[i])
        if len(x[0][0]) > 0:
            y = x[0][0]
        elif len(x[0][1]) > 0:
            y = x[0][1]
        elif len( x[0][2]) > 0:
            y = x[0][2]
        else:
            y= x[1][0]

        jobs['JobId'].append(y)



        if len(jobPositionNameList) == len(jobPositionPartText):

            jobs['Position Name'].append(jobPositionNameList[i])
            jobs['Position Description'].append(jobPositionPartText[i])
            linkre=re.findall('https://www.profession.hu/allas/[\w*-]*\d*' , jobPositionLinkList[i])
            jobs['Position Link'].append(linkre[0])

            #jobs['Position Posted Time'].append(jobPositionPostTime[i])

            if jobPositionPostTime[i].startswith('Friss'):
                timex = datetime.today().strftime('%B.%d.')
                jobs['Position Posted Time'].append(timex)

            elif jobPositionPostTime[i].startswith('ma'):
                timex = datetime.today().strftime('%B.%d.')
                jobs['Position Posted Time'].append(timex)
            
            elif jobPositionPostTime[i].startswith('tegnap'):
                timex = (datetime.today() - timedelta(days=1)).strftime('%B.%d.')
                jobs['Position Posted Time'].append(timex)
            else:
                jobs['Position Posted Time'].append(jobPositionPostTime[i])
            
        else :

            jobs['Position Name'].append(jobPositionNameList[i])
            jobs['Position Description'].append('NA')
            linkre=re.findall('https://www.profession.hu/allas/[\w*-]*\d*' , jobPositionLinkList[i])
            jobs['Position Link'].append(linkre[0])
            jobs['Position Posted Time'].append(jobPositionPostTime[i])

            if jobPositionPostTime[i].startswith('Friss'):
                timex = datetime.today().strftime('%B.%d.')
                jobs['Position Posted Time'].append(timex)

            elif jobPositionPostTime[i].startswith('ma'):
                timex = datetime.today().strftime('%B.%d.')
                jobs['Position Posted Time'].append(timex)
            
            elif jobPositionPostTime[i].startswith('tegnap'):
                timex = (datetime.today() - timedelta(days=1)).strftime('.%B.%d.')
                jobs['Position Posted Time'].append(timex)
            else:
                jobs['Position Posted Time'].append(jobPositionPostTime[i])            

    return jobs


def paging():
    try:
        job()
        while driver.find_element_by_css_selector('a.next.btn-outline-primary').is_displayed():
            driver.get(driver.find_element_by_css_selector(
                'a.next.btn-outline-primary').get_attribute('href'))
            job()
    except:
        print('DotDot')


# #Start the chrome browser and load the profession.hu website

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)   #options=chrome_options
driver.get(url)
time.sleep(2)
cookie = driver.find_element_by_id('elfogad').click()

#In the searchfield input the desired text

for elem in keyword:
    driver.get(url)
          
    searchbar = driver.find_element_by_id('header_keyword')
    searchbutton = driver.find_element_by_id('search-bar-search-button')
    searchbar.send_keys(elem)
    driver.implicitly_wait(5)
    searchbutton.click()
    # Total number of hit
    totalhit = driver.find_element_by_class_name('job-list__count').text
    print(f"Total Job for the {elem} keyword  is {totalhit} ")
    paging()


print(f"Keyword {len(jobs['Keyword'])}")
print(f"Indicator {len(jobs['Indicator'])}")
print(f"Position Name {len(jobs['Position Name'])}")
print(f"Position Description {len(jobs['Position Description'])}")
print(f"Position Link {len(jobs['Position Link'])}")
print(f"Position Posted Time {len(jobs['Position Posted Time'])}")


df = pd.DataFrame(jobs)
df.to_excel(str(pd.to_datetime("today").date()) + ' proffession_hu.xlsx')
df = df.drop('Indicator', axis=1)
df.to_sql('jobs', con=engine, if_exists='append')
driver.quit()
