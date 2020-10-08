from bs4 import BeautifulSoup
import constants
from selenium import webdriver
import time
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
import requests

driver = webdriver.Chrome()


def authorization():
    sign_in = driver.find_elements_by_css_selector('a.header__link')
    sign_in[1].click()
    time.sleep(30)
    driver.find_element_by_css_selector('button.toolbar__btn').click()


def get_bet(container):
    match_soup = BeautifulSoup(container, "html.parser")
    # authorization()
    matches = match_soup.select(".table__row")
    print(matches)


def break_of_match(container, w):
    match_soup = BeautifulSoup(container, "html.parser")
    matches = match_soup.select(".event__match.event__match--live.event__match--oneLine")
    for match in matches:
        time.sleep(1)
        time_of_live = match.select_one("div.event__stage--block").text
        score = match.select_one("div.event__scores.fontBold").text
        team_1 = match.select_one("div.event__participant.event__participant--home").text
        id_match = match["id"]
        total_score = int(sum(list(map(lambda x: int(x.strip()), score.split("-")))))
        if time_of_live.isdigit() and total_score <= 2:
            print(score, time_of_live)
            w.write(team_1 + ' ' + str(total_score) + '\n')
            time.sleep(2)
            check = driver.find_element_by_id(id_match).find_element_by_css_selector('div.event__check.checked')
            driver.execute_script('arguments[0].scrollIntoView(true);', check)
            try:
                check.click()
            except ElementClickInterceptedException:
                driver.find_element_by_css_selector('svg.boxOverContent__svg').click()


def my_matches(container_of_matches):
    driver.get(constants.url_1)
    my_match_soup = BeautifulSoup(container_of_matches, "html.parser")
    matches = my_match_soup.select(".event__match.event__match--scheduled.event__match--oneLine")
    for match in matches:
        team_1 = match.select_one("div.event__participant.event__participant--home").text
        id_match = match["id"]
        with open("matches.txt", "r") as file:
            for line in file:
                if team_1 == line.strip():
                    time.sleep(2)
                    check = driver.find_element_by_id(id_match).find_element_by_css_selector('div.event__check')
                    driver.execute_script('arguments[0].scrollIntoView(true);', check)
                    try:
                        check.click()
                    except ElementClickInterceptedException:
                        driver.find_element_by_css_selector('svg.boxOverContent__svg').click()
    driver.execute_script("window.scrollTo(0, 0);")


def track_coefficients(container_of_coefficients, team_1, f):
    coefficient_soup = BeautifulSoup(container_of_coefficients, "html.parser")
    totals = coefficient_soup.find("table", {"id": "odds_ou_2.5"})
    time.sleep(1)
    coefficient = totals.select_one(".odds-wrap").text
    coefficient = float(coefficient)
    if coefficient > 2:
        f.write(team_1 + '\n')


def track_matches(container_of_matches, f):
    match_soup = BeautifulSoup(container_of_matches, "html.parser")
    matches = match_soup.select(".event__match.event__match--scheduled.event__match--oneLine")
    for match in matches:
        team_1 = match.select_one("div.event__participant.event__participant--home").text
        score = match.select_one("div.event__scores").text
        if score == '-':
            time_match = match.select_one("div.event__time").text.strip().replace(':', '')
        if time_match.isdigit():
            id_match = match["id"].split("_")[-1]
            url = "https://www.flashscore.ru/match/{}/#match-summary".format(id_match)
            driver.get(url )
            time.sleep(1)
            buttons = driver.find_element_by_css_selector('ul.ifmenu').find_elements_by_tag_name('li')
            if len(buttons) >= 4:
                time.sleep(1)
                element_1 = driver.find_element_by_id("li-match-odds-comparison")
                element_1.click()
                time.sleep(1)
                # try:
                element_2 = driver.find_element_by_id("bookmark-under-over")
                element_2.click()
                # except NoSuchElementException:
                    # ActionToRunInCaseNoSuchElementTrue
                container_of_coefficients = driver.find_element_by_css_selector("div[id=detcon]").get_attribute("innerHTML")
                track_coefficients(container_of_coefficients, team_1, f)


def main():
    f = open('matches.txt', 'w')
    driver.get(constants.url_1)
    time.sleep(2)
    container_of_matches = driver.find_element_by_css_selector("div[id=mc]").get_attribute("innerHTML")
    track_matches(container_of_matches, f)
    f.close()
    my_matches(container_of_matches)
    # time.sleep(2)
    # tabs = driver.find_elements_by_css_selector('div.tabs__tab')
    # tabs[2].click()
    # temp_hash = 0
    # w = open('check_matches.txt', 'w')
    # while True:
    #     time.sleep(2)
    #     container = driver.find_element_by_css_selector("div[id=mc]").get_attribute("innerHTML")
    #     if temp_hash != hash(container):
    #         break_of_match(container, w)
    #         temp_hash = hash(container)
    # authorization()
    driver.get(constants.url_1)
    temp_hash = 0
    while True:
        time.sleep(2)
        container = driver.find_element_by_css_selector("div[class=line-filter-layout--3nXMD]").get_attribute("innerHTML")
        if temp_hash != hash(container):
            get_bet(container)
            temp_hash = hash(container)


if __name__ == "__main__":
    main()
