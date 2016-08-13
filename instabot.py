#!/usr/bin/env python

import os
import sys
import time
import logging
import logging.handlers
import cPickle
import random

import requests
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)-15s %(pathname)s:%(lineno)d - %(message)s')
handler = logging.handlers.SysLogHandler(address='/dev/log')
log = logging.getLogger(__name__)
log.addHandler(handler)

COOKIES_FILENAME = os.path.join(os.path.dirname(__file__), '.cookies.pkl')

def login_with_credentials(browser):
    log.info('Entering username')
    username = browser.find_element_by_name('username')
    username.send_keys(os.environ['USERNAME'])
    # browser.save_screenshot('uname.png')

    log.info('Entering password')
    password = browser.find_element_by_name('password')
    password.send_keys(os.environ['PASSWORD'])
    password.submit()

    # log.info('Save screenshot with home')
    time.sleep(10)
    # browser.save_screenshot('home.png')

    log.info('Saving cookies into file %s', COOKIES_FILENAME)
    cPickle.dump(browser.get_cookies() , open(COOKIES_FILENAME, 'wb'))

def login_with_cookies(browser):
    cookies = cPickle.load(open(COOKIES_FILENAME, 'rb'))
    for cookie in cookies:
        browser.add_cookie(cookie)

def like_one_post(browser, img):
    """
    Given an opened post, finds the like button, clicks on it and presses the right arrow
    in order to navigate to the next page
    :return: url of just liked image
    """
    url = None
    try:
        like = browser.find_element_by_css_selector('.coreSpriteHeartOpen')
        like.click()
        url = browser.current_url
    except:
        log.error('Image was already liked or some other error: %s', browser.current_url)

    # browser.save_screenshot(str(time.time()) + '.png')
    img.send_keys(Keys.ARROW_RIGHT)
    return url

def select_random_hashtag():
    """
    Returns a random hashtag from the latest posts or travel if none was found
    """
    r = requests.get('https://api.instagram.com/v1/users/self/media/recent?access_token={}'.format(os.environ['ACCESS_TOKEN']))
    if r.status_code == 200:
        data = r.json()
        tags = set()
        for media in data.get('data'):
            tags.update(media.get('tags'))
        return random.choice(list(tags))

    return 'travel'

def main():
    # select random hashtag from latest posts
    hashtag = select_random_hashtag()
    log.info('Hashtag #%s was selected', hashtag)

    display = Display(visible=0, size=(1024, 768))
    display.start()

    browser = webdriver.Firefox()
    log.info('Begin. Opening instagram.com')
    browser.get('https://instagram.com')

    if os.path.isfile(COOKIES_FILENAME):
        # load cookies
        log.info('Loading cookies and redirecting to instagram explore page')
        login_with_cookies(browser)
    else:
        log.info('Login with username and password')
        login_with_credentials(browser)

    # navigate to hashtag page, and wait 5s to load
    browser.get('https://www.instagram.com/explore/tags/{}/'.format(hashtag))
    log.info('Navigated to #%s', hashtag)
    time.sleep(5)

    # find first post
    img = browser.find_element_by_css_selector('article a')
    img.click()

    log.info('Found first image')

    # find first 3-9 photos to like
    for i in xrange(1, random.randint(4, 10)):
        # wait somewere between 5-10 sec
        time.sleep(random.randint(5, 11))

        # like the current active post, and move to the other
        url = like_one_post(browser, img)
        log.info('Liked image #%s, url: %s', i, url)

    # log.info('Saving screenshot')
    # browser.save_screenshot('home.png')
    log.info('Done!')

    browser.quit()

    display.stop()


if __name__ == '__main__':
    main()

