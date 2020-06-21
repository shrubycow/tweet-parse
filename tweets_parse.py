from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException, StaleElementReferenceException, NoSuchElementException
# from rest_app.models import TweetIds
from django.db.utils import IntegrityError
import time
import traceback
import os


class TweetsParse:

    driver = None

    def __init__(self, account, min_likes, wait_tag_time=10, sleeping_time=0.5, tweets_per_scroll=2):
        self.__account = account
        self.__min_likes = min_likes
        self.__wait_tag_time = wait_tag_time
        self.__sleeping_time = sleeping_time
        self.__tweets_per_scroll = tweets_per_scroll
        self.__tweet_ids = {}

    @classmethod
    def login(cls, login, password):
        cls.driver.get("https://twitter.com/login")
        login_el = cls.driver.find_element_by_name("session[username_or_email]")
        login_el.send_keys(login)
        password_el = cls.driver.find_element_by_name("session[password]")
        password_el.send_keys(password, Keys.ENTER)

    @classmethod
    def set_driver_settings(cls):
        cls.driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")

    def __has_link(self, tweet_block):
        try:
            tweet_block.find_element_by_css_selector(
                'div.css-1dbjc4n.r-9x6qib.r-t23y2h.r-1phboty.r-rs99b7.r-18u37iz.r-1ny4l3l.r-1udh08x.r-o7ynqc.r-6416eg')
            return True
        except NoSuchElementException:
            pass
        try:
            tweet_block.find_element_by_css_selector('div.css-901oao.r-hkyrab.r-1qd0xha.r-a023e6.r-16dba41.r-ad9z0x.r-bcqeeo.r-bnwqim.r-qvutc0 > a')
            return True
        except NoSuchElementException:
            pass
        return False

    def __is_retweet(self, tweet_block):
        username = tweet_block.find_element_by_css_selector('div.css-901oao.css-bfa6kz.r-1re7ezh.r-18u37iz.r-1qd0xha.r-a023e6.r-16dba41.r-ad9z0x.r-bcqeeo.r-qvutc0 > span').text
        if username != '@'+self.__account:
            return True
        return False


    def __scroll_and_check(self):
        before_scroll = TweetsParse.driver.execute_script("return window.pageYOffset;")
        time.sleep(self.__sleeping_time)
        TweetsParse.driver.execute_script("window.scrollBy(0, 150);")
        if TweetsParse.driver.execute_script("return window.pageYOffset;") == before_scroll:
            for i in range(40):
                before_scroll = TweetsParse.driver.execute_script("return window.pageYOffset;")
                time.sleep(self.__sleeping_time)
                TweetsParse.driver.execute_script("window.scrollBy(0, 150);")
                if TweetsParse.driver.execute_script("return window.pageYOffset;") == before_scroll:
                    pass
                else:
                    return False
        return True

    def __filter_data(self, tweet_block, likes):
        if likes >= self.__min_likes:
            try:
                if self.__has_link(tweet_block) or self.__is_retweet(tweet_block):
                    return
                print(likes)
                tweet_url = tweet_block.find_element_by_css_selector("a.r-1re7ezh.r-1loqt21.r-1q142lx.r-1qd0xha.r-a023e6.r-16dba41.r-ad9z0x.r-bcqeeo.r-3s2u2q.r-qvutc0.css-4rbku5.css-18t94o4.css-901oao").get_attribute('href')
                tweet_id = tweet_url[tweet_url.index('status/')+7:tweet_url.index('status/')+7+19]
                self.__tweet_ids[tweet_id] = likes

                # delete sticky panel with name and surname if it exists
                try:
                    TweetsParse.driver.execute_script(
                        "return document.querySelector('#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div.css-1dbjc4n.r-aqfbo4.r-14lw9ot.r-my5ep6.r-rull8r.r-qklmqi.r-gtdqiz.r-ipm5af.r-1g40b8q').remove();")
                except JavascriptException:
                    pass
                
            except StaleElementReferenceException:
                print("Сработал StaleElementReferenceException")
                TweetsParse.driver.execute_script("window.scrollBy(0, -400);")
                time.sleep(self.__sleeping_time)
    def parse(self, save_to_file=False):
        TweetsParse.driver.get(f"https://twitter.com/{self.__account}")
        WebDriverWait(TweetsParse.driver, self.__wait_tag_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "time"))).get_attribute('datetime')
        TweetsParse.driver.execute_script(
            "return document.querySelector('#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div.css-1dbjc4n.r-aqfbo4.r-14lw9ot.r-my5ep6.r-rull8r.r-qklmqi.r-gtdqiz.r-ipm5af.r-1g40b8q').remove();")
        try:
            while True:
                if self.__scroll_and_check():
                    break
                time.sleep(self.__sleeping_time)
                try:
                    print(TweetsParse.driver.execute_script('return document.querySelector("div.css-1dbjc4n.r-1omma8c").firstChild;'))
                except JavascriptException:
                    pass
                TweetsParse.driver.execute_script("window.scrollBy(0, 150);")

                tweet_blocks = WebDriverWait(TweetsParse.driver, self.__wait_tag_time).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                                                                              "article.css-1dbjc4n.r-1loqt21.r-16y2uox.r-1wbh5a2.r-1ny4l3l.r-1udh08x.r-1j3t67a.r-o7ynqc.r-6416eg")))
                likes_elem = []
                for i in range(self.__tweets_per_scroll):
                    bottom_panel_elems = tweet_blocks[i].find_elements_by_css_selector('div.css-18t94o4.css-1dbjc4n.r-1777fci.r-11cpok1.r-1ny4l3l.r-bztko3.r-lrvibr')
                    for elem in bottom_panel_elems:
                        if elem.get_attribute('data-testid') == 'like':
                            likes_elem.append(elem.find_element_by_css_selector('span.css-901oao.css-16my406.r-1qd0xha.r-ad9z0x.r-bcqeeo.r-qvutc0'))
                likes = []

                try:
                    for i in range(self.__tweets_per_scroll):
                        if 'тыс.' in likes_elem[i].text:
                            likes.append(int(float(likes_elem[i].text.split(" ")[0].replace(',', '.')) * 1000))
                        else:
                            likes.append(int(likes_elem[i].text))
                except IndexError:
                    continue
                for i in range(self.__tweets_per_scroll):
                    self.__filter_data(tweet_blocks[i], likes[i])
        except BaseException:
            print(traceback.format_exc())

        if not save_to_file:
            for tweet_id, likes in self.__tweet_ids.items():
                print(tweet_id, likes)
                try:
                    TweetIds.objects.create(id=tweet_id, likes=likes, account=self.__account)
                except IntegrityError:
                    pass
        else:
            with open(self.__account+"_tweets.txt", 'w') as file:
                for tweet_id, likes in self.__tweet_ids.items():
                    file.write(f"{tweet_id} {likes}\n")


if __name__ == "__main__":
    TweetsParse.set_driver_settings()
    TweetsParse.login('Alexandriyskiy', '115577sah')
    my_page = TweetsParse('21jqofa', 1000)
    my_page.parse(save_to_file=True)

# TweetsParse.set_driver_settings(); TweetsParse.login('Alexandriyskiy', '115577sah'); my_page = TweetsParse('21jqofa', 1000); my_page.parse()