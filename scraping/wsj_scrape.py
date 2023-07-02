
import os
import logging
import time
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)



URL = "https://www.wsj.com/news/archive/2020/march"
ARG_WINDOW_SIZE = "--window-size=1920,1080"



def find_text_by_xpath(driver, pattern: str) -> str:
    """Helper for finding text stored under xpath pattern"""
    try:
        text_output = driver.find_elements('xpath', pattern)
    except (NoSuchElementException, StaleElementReferenceException):
        text_output = ""
    return text_output


def parse_daylinks(driver, writer, daylinks):
    """Iterate over scraped daylinks to get fields of interest for each article"""
    for i in range(11, len(daylinks)):
        # Get all sub daylinks by xpath
        daylinks2 = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//a[@class="WSJTheme--day-link--19pByDpZ "][@href]')
            )
        )
        logging.info("DayLinks2 is:", daylinks2)
        time.sleep(1)
        daylinks2[i].click()
        time.sleep(1.5)

        # Find headline links
        linkslist1 = None
        while not linkslist1:
            try:
                linkslist1 = driver.find_elements('xpath', 
                                                 './/h2[@class="WSJTheme--headline--unZqjb45 reset WSJTheme--heading-standard-s--2eMU4jl4 WSJTheme--standard--2eOdD903 typography--serif-display--ZXeuhS5E WSJTheme--small--2f09SjbK "]//a[@href]')
            except:
                continue
        logging.info("Length of linkslist1 is:", len(linkslist1))
        time.sleep(2)

        for i in range(0, len(linkslist1)):
            time.sleep(2)
            linkslist = None
            while not linkslist:
                try:
                    linkslist = driver.find_elements('xpath', './/h2[@class="WSJTheme--headline--unZqjb45 reset WSJTheme--heading-standard-s--2eMU4jl4 WSJTheme--standard--2eOdD903 typography--serif-display--ZXeuhS5E WSJTheme--small--2f09SjbK "]//a[@href]')
                except:
                    continue
            logging.info("Length of linkslist is:", len(linkslist))
            time.sleep(2)
            try:
                linkslist[i].click()
                logging.info(
                    "Trying to click the following web element:", linkslist[i]
                )
                time.sleep(1)
                try:
                    article_string = ""
                    article_string = driver.find_elements('xpath', 
                       ".//article"
                    )[0].text
                    # for ele in text1:
                    #     article_string += ele.text
                except (
                    NoSuchElementException,
                    StaleElementReferenceException,
                ) as e:
                    article_string = ""
                    pass

                # Get article fields of interest
                article_headline = find_text_by_xpath(driver, 
                    './/h1[@class="wsj-article-headline"]'
                )
                article_subheadline = find_text_by_xpath(driver, 
                    './/h2[@class="sub-head"]'
                )
                article_published_date = find_text_by_xpath(driver, 
                    ".//time[@class='timestamp article__timestamp flexbox__flex--1']"
                )
                article_author = find_text_by_xpath(driver, 
                    './/button[@class="author-button"]'
                )
                article_topic = find_text_by_xpath(driver, 
                    './/li[@class="article-breadCrumb"][1]/a'
                )
                article_number_comments = find_text_by_xpath(driver, 
                    './/a[@id ="article-comments-tool"]/span'
                )
                # Prepare row output
                article_dict = {
                    "article_body_text": article_string,
                    "article_headline": article_headline,
                    "article_subheadline": article_subheadline,
                    "article_published_date": article_published_date,
                    "author": article_author,
                    "topic": article_topic,
                    "article_number_comments": article_number_comments,
                }
                # Write results
                writer.writerow(article_dict.values())
                driver.back()
            except Exception as e:
                logging.info("Failed to click on {} because of exception: {}".format(linkslist[i], str(e)))
                driver.back()
                continue
        time.sleep.back()


def signin(driver):
    """Send username and password env vars to signin form fields and press submit button"""
    # Click signin button
    sign_in_link = driver.find_element_by_link_text("Sign In")
    sign_in_link.click()
    time.sleep(2)
    # Find username and pw fields
    username = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
    )
    password = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "password"))
    )

    user = os.environ.get("USER")
    pw = os.environ.get("PASS")

    # Input username and pw
    username.send_keys(user)
    password.send_keys(pw)
    # Find and click submit button once username and pw inputted
    submit_button = self.driver.find_element_by_xpath(
        ".//button[@type='submit'][@class='solid-button basic-login-submit']"
    )
    submit_button.click()

    time.sleep(1)



if __name__ == "__main__":
    os.environ['PATH'] = os.environ['PATH'] + 'C:\\WebDriver\\bin';
    chrome_options = Options()
    chrome_options.add_argument(ARG_WINDOW_SIZE)

    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    daylinks = driver.find_elements('xpath', '//a[@class="WSJTheme--day-link--19pByDpZ "][@href]')

    signin(driver)

    username = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
    )
    password = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "password"))
    )

    filename = "wsj_articles.csv"
    csv_file = open(filename, "w", encoding="utf-8", newline="")
    writer = csv.writer(csv_file)

    parse_daylinks(driver=driver, writer=writer, daylinks=daylinks)
