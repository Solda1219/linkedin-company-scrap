import os
import time
from datetime import datetime, date, timedelta
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# from extra_utils import date_to_str


def headDriver():
    options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1200")
    try:
        driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
        agent = driver.execute_script("return navigator.userAgent")
        driver.close()
        options.add_argument("user-agent=" + agent)
        driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
        return driver
    except:
        print("You must use same chrome version with chrome driver!")
        return 0


def headlessDriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--window-size=1920, 900")
    options.add_argument("--hide-scrollbars")
    try:
        driver = webdriver.Chrome(
            options=options, executable_path="chromedriver.exe")
        agent = driver.execute_script("return navigator.userAgent")
        driver.close()
        options.add_argument("user-agent=" + agent)
        driver = webdriver.Chrome(
            options=options, executable_path="chromedriver.exe")

        return driver
    except:
        print("You must use same chrome version with chrome driver!")
        return 0


def findClickY(driver):
    element = driver.find_element_by_xpath("//a[@class='next']")
    if element:
        return element
    else:
        return False


class LinkedinComScraper():
    ALL_OUT = '../social_media_data'
    LNK_URLS = os.path.join(ALL_OUT, 'linkedin_urls.csv')
    LNK_FOLDER = 'linkedin'

    def __init__(self):
        self.df_urls = pd.read_csv(self.LNK_URLS, encoding='utf-8-sig')

        self.scrape_date = date.today().strftime("%d/%m/%Y")
        self.folder_date = self.scrape_date.replace('/', '-')
        self.lnk_out = os.path.join(
            os.path.join(self.ALL_OUT, self.folder_date),
            self.LNK_FOLDER
        )

        os.makedirs(self.lnk_out, exist_ok=True)

    def writeCsvheader(self, filename, columns):
        try:
            os.remove(filename)
        except:
            pass
        df = pd.DataFrame(columns=columns)
        # filename= str(datetime.datetime.now()).replace(':', '-')+'.csv'
        df.to_csv(filename, mode='x', index=False, encoding='utf-8-sig')

    def saveToCsv(self, filename, newPage, columns):
        df = pd.DataFrame(newPage, columns=columns)
        print("Now items writed in csv file!")
        df.to_csv(filename, mode='a', header=False,
                  index=False, encoding='utf-8-sig')

    def scrape(self):

        columns = ['url', 'activity_id', 'follower_count', 'date', 'description', 'reaction_count', 'comment_count']
        company_id = "nullOfDateyyety"
        filename = os.path.join(self.lnk_out, "{}.csv".format(company_id))
        if os.path.exists(filename):
            return

        self.writeCsvheader(filename, columns)
        signinUrl = "https://www.linkedin.com/uas/login"
        intendedUrl = "https://www.linkedin.com/company/fairlie-sensetfinance/"

        linkedin_username = "sabashubladze69@gmail.com"
        linkedin_password = "antifriz"
        driver = headDriver()
        driver.get(signinUrl)
        time.sleep(1)

        username_input = driver.find_element_by_id('username')
        username_input.send_keys(linkedin_username)

        password_input = driver.find_element_by_id('password')
        password_input.send_keys(linkedin_password)
        password_input.submit()
        time.sleep(70)
        if "posts/?feedView=all" in intendedUrl:
            modifiedUrl = intendedUrl
        else:
            if intendedUrl[-1] == '/':
                modifiedUrl = intendedUrl + "posts/?feedView=all"
            else:
                modifiedUrl = intendedUrl + "/posts/?feedView=all"

        driver.get(modifiedUrl)
        time.sleep(1)
        if len(driver.find_elements_by_xpath("//div[@class= 'feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative artdeco-card ember-view']"))> 0:
            for i in range(30):
                time.sleep(0.2)
                recentList = driver.find_elements_by_xpath(
                    "//div[@class='feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative artdeco-card ember-view']")
                if len(recentList) == 0:
                    break
                else:
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", recentList[len(recentList) - 1])
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            itemNodes = soup.find_all('div', attrs={
            'class': 'feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative artdeco-card ember-view'})
        else:
            for i in range(30):
                time.sleep(0.2)
                recentList = driver.find_elements_by_xpath(
                    "//div[@class='feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative feed-shared-update-v2--e2e artdeco-card ember-view']")
                if len(recentList) == 0:
                    break
                else:
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", recentList[len(recentList) - 1])
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            itemNodes = soup.find_all('div', attrs={
                'class': 'feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative feed-shared-update-v2--e2e artdeco-card ember-view'})
        followerTmps = soup.find_all(
            'div', attrs={'class': 'org-top-card-summary-info-list__info-item'})
        for followerTmp in followerTmps:
            if 'follower' in followerTmp.text:
                followerCount = followerTmp.text.strip() 
        print(followerCount)
        return
        newPage = []
        for itemNode in itemNodes:
            activityId = ''
            try:
                activityId = itemNode.attrs['data-urn']
            except:
                pass
            followerCount = 0
            try:
                followerCount = itemNode.find('span', attrs={
                    'class': 'feed-shared-actor__description t-12 t-normal t-black--light'}).text.strip()
            except:
                pass
            date = 0
            try:
                date = itemNode.find('span', attrs={
                    'class': 'feed-shared-actor__sub-description t-12 t-normal t-black--light'}).text.strip()
            except:
                pass
            description = ''
            try:
                description = itemNode.find('span', attrs={'class': 'break-words'}).text.strip()
            except:
                pass
            reactionCount = 0
            try:
                reactionCount = itemNode.find('span', attrs={
                    'class': 'v-align-middle social-details-social-counts__reactions-count'}).text.strip()
            except:
                pass
            commentCount = 0
            try:
                commentCount = itemNode.find('li', attrs={
                    'class': 'social-details-social-counts__comments social-details-social-counts__item'}).text.strip()
            except:
                pass
            new = {'url': intendedUrl, 'activity_id': activityId, 'follower_count': followerCount,
                   'date': date, 'description': description, 'reaction_count': reactionCount,
                   'comment_count': commentCount}
            print(new)
            if 'week' in date:
                newPage.append(new)
                continue
            else:
                if 'year' in date:
                    continue
                elif (int(date[0]) > 5 or date[:2] == '10' or date[:2] == '11' or date[:2] == '12'):
                    continue
                else:
                    newPage.append(new)

        self.saveToCsv(filename, newPage, columns)
        driver.close()
        time.sleep(1)

    def scrape_fb_all(self):

        for i, row in tqdm(self.df_urls.iterrows(), total=self.df_urls.shape[0]):
        # for row in self.df_urls.iterrows():
            self.scrape()


if __name__ == '__main__':
    scraper = LinkedinComScraper()
    scraper.scrape()

