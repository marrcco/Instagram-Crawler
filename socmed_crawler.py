import gspread
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import sys
import configparser
import datetime
import gspread_dataframe as gd
from selenium.webdriver.chrome.options import Options


class Crawler:
    # reading data from config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["instagram"]["username"]
    pw = config["instagram"]["pw"]
    followers_xpath = config["instagram"]["followers_xpath"]
    login_fields_xpath = config["instagram"]["login_fields"]
    login_button_xpath = config["instagram"]["login_button_xpath"]
    webdriver_path = config["instagram"]["webdriver_path"]


    def __init__(self,type_of_media,type_of_account,sheet_to_update,delay=120,implicit_wait=10):
        self.type_of_media = type_of_media
        self.type_of_account = type_of_account
        self.sheet_to_update = sheet_to_update
        self.username = Crawler.username
        self.pw = Crawler.pw
        self.followers_xpath = Crawler.followers_xpath
        self.login_button_xpath = Crawler.login_button_xpath
        self.webdriver_path = Crawler.webdriver_path
        self.delay = delay
        self.implicit_wait = implicit_wait


    # function to pull all profile urls from sheets
    def ger_profile_urls(self):
        gc = gspread.service_account(filename="credentials.json")  # load gsheets credenetials
        sh = gc.open_by_key("GSHEETS_KEY")  # key found in last part of gsheet URL
        worksheet = sh.worksheet("profile_urls")  # choose worksheet
        res = worksheet.get_all_records()  # get all results from selected worksheet
        df = pd.DataFrame(res)  # turn results into dataframe
        df = df[(df["type_of_media"] == self.type_of_media) & (df["type_of_account"] == self.type_of_account)]
        return df

    # function for selenium setup
    def selenium_setup(self):
        option = Options()  # remove after chrome 104
        option.headless = True
        option.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(self.webdriver_path,options=option)  # load driver
        return driver

    # function for crawling instagram followers
    def crawl(self):
        df = self.ger_profile_urls()
        driver = self.selenium_setup()
        # login
        driver.get("https://www.instagram.com/accounts/login/")

        try:
            login_fields = WebDriverWait(driver,self.delay).until(EC.presence_of_all_elements_located((By.XPATH, self.login_fields_xpath)))
            username_field = login_fields[0]
            username_field.send_keys(self.username)
            print("username keys sent successfully")
            password_field = login_fields[1]
            password_field.send_keys(self.pw)
            print("password keys sent successfully")
            login_button = WebDriverWait(driver, self.delay).until(EC.presence_of_element_located((By.XPATH, self.login_button_xpath)))
            login_button.click()
            print("login button clicked\n\nlogin finished successfuly")
        except:
            print("error while trying to login")
            sys.exit()

        driver.implicitly_wait(self.implicit_wait)

        # crawling
        df[["date","soc_med"]] = [datetime.date.today(),self.type_of_media]
        for index, row in df.iterrows():
            driver.get(row["Link"])
            driver.implicitly_wait(10)
            try:
                followers = driver.find_element_by_xpath(self.followers_xpath).get_attribute("title")
                df.loc[index, "followers"] = followers
                print(f"{row['Name']} has {followers} followers")
            except:
                df.loc[index, "followers"] = "0"
                print("manual")

        return df

    # function to update the spreadsheet with new data
    def update_spreadsheet(self,df):
        gc = gspread.service_account(filename="credentials.json")  # gsheets credenetials
        sh = gc.open_by_key("GSHEETS_KEY") # taken from last part of URL
        worksheet_to_update = sh.worksheet(self.sheet_to_update)  # choose worksheet
        res_to_update = worksheet_to_update.get_all_records()  # get all results from selected worksheet
        df_to_update = pd.DataFrame(res_to_update)  # turn results into dataframe

        new_df = pd.concat([df_to_update,df])
        gd.set_with_dataframe(worksheet_to_update, new_df)
        print("worksheet updated with new data")


crawler = Crawler(type_of_media="instagram",
                  type_of_account="UFC",
                  sheet_to_update="instagram_ufc")

df = crawler.crawl()
crawler.update_spreadsheet(df)







