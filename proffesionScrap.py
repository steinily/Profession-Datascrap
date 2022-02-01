# %%
from selenium import webdriver
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver.chrome.options import Options
from variables import *
# %% [markdown]
# #Global Variables

# %%
url = 'https://www.profession.hu/'
jobs = {
    'Indicator': [],
    'Position Name': [],
    'Position Description': [],
    'Position Link': [],
    'Position Posted Time': []
}
databasename = keyword+' proffesion_hu.db'
engine = create_engine('sqlite:///' + databasename, echo=False)

# %% [markdown]
# #Start the chrome browser and load the profession.hu website

# %%
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)


# %% [markdown]
# #In the searchfield input the desired text

# %%
searchbar = driver.find_element_by_id('header_keyword')
searchbutton = driver.find_element_by_id('search-bar-search-button')
searchbar.send_keys(keyword)
searchbutton.click()

# %% [markdown]
# #Gathering the nececarry informations

# %%
# Total number of hit
totalhit = driver.find_element_by_class_name('job-list__count').text
print(f"Total Job for the {keyword} keyword  is {totalhit} ")

# %%


def job():
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
        jobs['Indicator'].append(indexincrement)
        jobs['Position Name'].append(jobPositionNameList[i])
        jobs['Position Description'].append(jobPositionPartText[i])
        jobs['Position Link'].append(jobPositionLinkList[i])
        jobs['Position Posted Time'].append(jobPositionPostTime[i])

    return jobs


# %%
# Paging
try:
    job()
    while driver.find_element_by_css_selector('a.next.btn-outline-primary').is_displayed():
        driver.get(driver.find_element_by_css_selector(
            'a.next.btn-outline-primary').get_attribute('href'))
        job()
except:
    pass

finally:
    df = pd.DataFrame(jobs)
    df.to_excel(keyword + ' proffession_hu.xlsx')
    df = df.drop('Indicator', axis=1)
    df.to_sql('jobs', con=engine, if_exists='append')
    driver.quit()
