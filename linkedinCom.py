from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
import sys
from selenium.webdriver.support.ui import WebDriverWait


def headDriver():
    options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1200")
    try:
        driver = webdriver.Chrome(
            options=options, executable_path="chromedriver.exe")
        agent = driver.execute_script("return navigator.userAgent")
        driver.close()
        options.add_argument("user-agent="+agent)
        driver = webdriver.Chrome(
            options=options, executable_path="chromedriver.exe")
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
        options.add_argument("user-agent="+agent)
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
        columns = ['url', 'activity_id', 'follower_count', 'date',
                   'description', 'reaction_count', 'comment_count']
        filename = "LinkedinCom.csv"
        self.writeCsvheader(filename, columns)
        signinUrl = "https://www.linkedin.com/uas/login"
        intendedUrl = "https://www.linkedin.com/company/homunity/"

        linkedin_username = "sabashubladze69@gmail.com"
        linkedin_password = "antifriz"
        driver = headlessDriver()
        driver.get(signinUrl)
        time.sleep(2)

        username_input = driver.find_element_by_id('username')
        username_input.send_keys(linkedin_username)

        password_input = driver.find_element_by_id('password')
        password_input.send_keys(linkedin_password)
        password_input.submit()

        if "posts/?feedView=all" in intendedUrl:
            modifiedUrl = intendedUrl
        else:
            if intendedUrl[-1] == '/':
                modifiedUrl = intendedUrl + "posts/?feedView=all"
            else:
                modifiedUrl = intendedUrl + "/posts/?feedView=all"

        driver.get(modifiedUrl)
        time.sleep(1)

        # sortBtn= driver.find_element_by_xpath("//button[@class='sort-dropdown__dropdown-trigger display-flex t-12 t-black--light t-normal artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view']")
        # sortBtn.click()
        # time.sleep(2)
        # # for i in range(1):
        # #     time.sleep(0.2)
        # #     recentList = driver.find_elements_by_xpath(
        # #         "//div[@class='artdeco-dropdown__content artdeco-dropdown__content--is-open artdeco-dropdown--is-dropdown-element artdeco-dropdown__content--justification-right artdeco-dropdown__content--placement-bottom ember-view']")
        # #     if len(recentList) == 0:
        # #         break
        # #     else:
        # #         driver.execute_script(
        # #             "arguments[0].scrollIntoView();", recentList[len(recentList) - 1])
        # recentBtn = driver.find_elements_by_xpath("//div[@class='artdeco-dropdown__content artdeco-dropdown__content--is-open artdeco-dropdown--is-dropdown-element artdeco-dropdown__content--justification-right artdeco-dropdown__content--placement-bottom ember-view']")[-1]
        # recentBtn.click()
        # time.sleep(10)
        #scroll part
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

        # itemNodes = soup.find_all('div', attrs={'class': 'occludable-update ember-view'})
        itemNodes = soup.find_all('div', attrs={
                                  'class': 'feed-shared-update-v2 feed-shared-update-v2--minimal-padding full-height relative feed-shared-update-v2--e2e artdeco-card ember-view'})
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
                description = itemNode.find(
                    'span', attrs={'class': 'break-words'}).text.strip()
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
                   'date': date, 'description': description, 'reaction_count': reactionCount, 'comment_count': commentCount}

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


if __name__ == '__main__':
    scraper = LinkedinComScraper()
    scraper.scrape()
