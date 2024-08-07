from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import selenium
import datetime
import os
import time


class Twitterbot:
 
    def __init__(self, email, password):
        self.email = email
        self.password = password
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        service = Service(executable_path=os.path.join(os.getcwd(),'chromedriver.exe'))
        self.bot = webdriver.Chrome(
            options = chrome_options,
            service=service
        )
 
    def login(self):
        tries = 0
        while True:
            try:
                bot = self.bot
                bot.get('https://twitter.com/login')
                time.sleep(6)
                email = bot.find_element(By.XPATH,
                    '//input'
                )
                email.send_keys(self.email)
                
                time.sleep(5)
                ActionChains(bot).send_keys(Keys.RETURN).perform()
                time.sleep(3)
                password = bot.find_elements(By.TAG_NAME,
                    "input"
                )[1]
                password.send_keys(self.password)
                
                ActionChains(bot).send_keys(Keys.RETURN).perform()
                time.sleep(3)
                break
            except Exception:
                if tries >= 1:
                    break
                tries += 1
            except KeyboardInterrupt:
                return
            
def setup_bot(email, password):
    bot = Twitterbot(email, password)
    bot.login()
    return bot


def scrape_accounts(driver, accountsToScrape, keyword, bioCheck=False):

    # if the bioCheck is set to true, the bot will check if the bio contains the keyword

    url = f"https://x.com/search?q={keyword}&src=typed_query&f=user"
    url = f"https://x.com/search?q={keyword}&src=typed_query&f=user"
    driver.bot.get(url)
    time.sleep(5)
    accs = []
    while accountsToScrape > 0:
        divs = driver.bot.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')
        for div in divs:
            try:
                if accountsToScrape == 0:
                    break
                

                try:
                    if bioCheck:
                        if keyword.lower() not in div.text.lower():
                            print("The given keyword is not in the bio of the account!")
                            continue
                    if div.text.split("\n")[1] in accs:
                        continue
                except:
                    continue
                try:
                    if div.text.split("\n")[2] in accs:
                        continue
                except:
                    pass
                accs.append(div.text.split("\n")[1]) if "followed by" not in div.text.lower() else accs.append(div.text.split("\n")[2])
                accountsToScrape -= 1
                div.location_once_scrolled_into_view
            except StaleElementReferenceException:
                pass
            
    return accs, driver

def get_followers(driver, accounts):
    wait  = WebDriverWait(driver.bot, 10)
    data  = {}
    for acc in accounts:
        driver.bot.switch_to.window(driver.bot.window_handles[0])
        driver.bot.execute_script(f"window.open('https://x.com/{acc}', '_blank');")
        time.sleep(3)
        driver.bot.switch_to.window(driver.bot.window_handles[1])
        followers =  wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(translate(@href, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "followers")]')))
        followers = re.sub(',', '', followers.text)
        if 'k' in followers.lower():
            followers = float(followers.lower().split('k')[0]) * 1000
        elif 'm' in followers.lower():
            followers = float(followers.lower().split('m')[0]) * 100000
        else:
            followers = float(followers.split(' ')[0])

        data[acc] = followers
        driver.bot.close()
    return data


def tester(email, password, accountsToScrape, keyword):
    bot = setup_bot(email, password)
    time.sleep(30)
    accs, driver = scrape_accounts(bot, accountsToScrape, keyword, bioCheck=True)
    data = get_followers(driver, accs)
    return data


if __name__ == "__main__":
    username = input("Username: ")
    password = input("Password: ")
    accountsToScrape = int(input("Accounts to scrape: "))
    keyword = input("Keyword: ")
    data = tester(username, password, accountsToScrape, keyword)
    print(data)