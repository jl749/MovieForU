import time
from selenium import webdriver

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

for link in links:
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(0.5)
    driver.execute_script(f'''window.open("{link}", "_blank")''')
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[1])
    genreTags = driver.find_elements_by_css_selector('span.ipc-chip__text')[:5]
    genres = [aTag.get_attribute('innerHTML') for aTag in genreTags]
    print(genres)

    driver.find_element_by_xpath('//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[3]/div[2]/div[2]/div[1]/a/div').click()
    time.sleep(3)

    imgs, actors = [], []
    for i in range(5):
        imgs.append(driver.find_element_by_css_selector('meta[property=\'og:image\']').get_attribute('content'))
        actors.append(driver.find_element_by_css_selector('div.MediaSheetstyles__SecondaryContent-sc-1warcg6-10.hrbmLW > div:nth-child(1) > span:nth-child(2) > a:nth-child(1)').get_attribute('innerHTML'))
        driver.find_element_by_xpath('//*[@id="__next"]/main/div[2]/div[3]/div[3]').click()
        time.sleep(0.1)

    print(imgs)
    print(actors)

    driver.close()  # close current tab

