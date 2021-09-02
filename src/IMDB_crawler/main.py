import pickle
import time
import urllib.request
from selenium import webdriver


def save_obj(obj, name):
    with open(f'{name}.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(f'{name}.pkl', 'rb') as f:
        return pickle.load(f)


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
            imgMap[f'{i}-{j}.jpg'] = [ [actors[j]] ]
    # genres
    print(imgs)
    print(actors)

    driver.close()  # close current tab

save_obj(imgMap, "ImgMap")
