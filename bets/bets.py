from bs4 import BeautifulSoup
import constant
from selenium import webdriver
import time


def main():
    driver = webdriver.Chrome()
    driver.get(constant.url)

    time.sleep(2)
    elements = driver.find_elements_by_css_selector("div.tabs__tab")
    elements[1].click()

    def track_matches(container):
        soup = BeautifulSoup(container, "html.parser")
        matches = soup.select(".event__match.event__match--live.event__match--oneLine")
        for match in matches:
            time_match = match.select_one("div.event__stage--block")
            total = match.select_one("div.event__scores.fontBold")
            id_match = match["id"].split("_")[-1]
            if time_match and total:
                time_match = time_match.text.strip()
                total = total.text.strip()
                if time_match.isdigit():
                    time_match = int(time_match)
                    total_sum = sum(list(map(lambda x : int(x.strip()), total.split("-"))))
                    url = "https://www.flashscore.ru/match/{}/#match-summary".format(id_match)
                    if time_match > 50 and total_sum < 3:
                        print(time_match, total_sum, total, url)

    temp_hash = 0
    while True:
        conteiner = driver.find_element_by_css_selector("div[id=mc]").get_attribute("innerHTML")
        if temp_hash != hash(conteiner):
            track_matches(conteiner)
            temp_hash = hash(conteiner)
    time.sleep(2)
if __name__ == "__main__":
    main()
