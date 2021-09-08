import pickle
import re
import time
import urllib.request
from typing import List, Dict

from selenium import webdriver


def save_obj(obj, name):
    with open(f'{name}.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(f'{name}.pkl', 'rb') as f:
        return pickle.load(f)


def crawl_imgSet():
    driver = webdriver.Firefox()
    driver.get('https://www.imdb.com/chart/top/?sort=nv,desc&mode=simple&page=1')
    time.sleep(3)

    movieLink = driver.find_elements_by_css_selector('tbody.lister-list > tr > td:nth-child(2) > a')

    links = []
    for i, movie in enumerate(movieLink):
        if i >= 100:
            break
        links.append(movie.get_attribute('href'))

    print(links)
    print(len(links))

    imgMap = dict()
    for i, link in enumerate(links):
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.5)
        driver.execute_script(f'''window.open("{link}", "_blank")''')
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[1])
        genreTags = driver.find_elements_by_css_selector('span.ipc-chip__text')[:5]
        genres = [aTag.get_attribute('innerHTML') for aTag in genreTags]
        print(genres)
        time.sleep(2)

        driver.find_element_by_xpath('//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[3]/div[2]/div[2]/div[1]/a/div').click()
        time.sleep(3)

        imgs, actors = [], []
        for _ in range(5):
            imgs.append(driver.find_element_by_css_selector('meta[property=\'og:image\']').get_attribute('content'))
            actors.append(driver.find_element_by_css_selector('div.MediaSheetstyles__SecondaryContent-sc-1warcg6-10.hrbmLW > div:nth-child(1) > span:nth-child(2) > a:nth-child(1)').get_attribute('innerHTML'))
            driver.find_element_by_xpath('//*[@id="__next"]/main/div[2]/div[3]/div[3]').click()
            time.sleep(0.1)

        for j, img in enumerate(imgs):
            jpg = urllib.request.urlopen(img).read()
            with open(f'img/{i}-{j}.jpg', 'wb') as f:
                f.write(jpg)
                imgMap[f'{i}-{j}.jpg'] = [ genres, [actors[j]] ]
        # genres
        print(imgs)
        print(actors)

        driver.close()  # close current tab

    save_obj(imgMap, "ImgMap")


def crawl_stroyline():
    driver = webdriver.Firefox()
    driver.get('https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&view=simple')

    CORPUS: List[str] = []
    CAST: List[Dict[str, str]] = []
    for _ in range(9):
        time.sleep(3)
        movieLink = driver.find_elements_by_css_selector('div.lister.list.detail.sub-list > div > div > div.lister-item-content > div > div.col-title > span > span:nth-child(2) > a')
        links = []
        for movie in movieLink:
            links.append(movie.get_attribute('href'))
        print(links)
        print(len(links))

        for i, link in enumerate(links):
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(0.5)
            driver.execute_script(f'''window.open("{link}", "_blank")''')
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)

            # collect storyline
            storyline = driver.find_element_by_css_selector(
                'div.Storyline__StorylineWrapper-sc-1b58ttw-0.iywpty > div > div > div'
            ).text  # get_attribute('innerHTML')

            ### REGEX ###
            storyline = re.sub("\.\s—.+$", ".", storyline)
            print(storyline)

            CORPUS.append(storyline)
            time.sleep(2)

            # collect CAST dict
            driver.find_element_by_css_selector(
                '#__next > main > div > section > div > section > div > div > section > div > div > a > h3'
            ).click()
            time.sleep(1)
            actors = driver.find_elements_by_css_selector('table.cast_list > tbody > tr > td:nth-child(2)')
            actors = [actor.text for j, actor in enumerate(actors) if j < 5]
            characters = driver.find_elements_by_css_selector('table.cast_list > tbody > tr > td:nth-child(4)')
            characters = [character.text for j, character in enumerate(characters) if j < 5]

            print(list(zip(actors, characters)))

            castDict = dict()
            for a, c in zip(actors, characters):
                castDict[c] = a
            CAST.append(castDict)

            driver.close()  # close current tab
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element_by_css_selector('#main > div > div.desc > a').click()
    save_obj(CORPUS, "StoryLine")
    save_obj(CAST, "Cast")


if __name__ == '__main__':
    # crawl_imgSet()
    crawl_stroyline()