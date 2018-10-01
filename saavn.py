from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from browsermobproxy import Server
import psutil
import time
import os
import urllib.parse
import json
import requests

if __name__=='__main__':
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "browsermob-proxy":
            proc.kill()

    server = Server(path=os.getcwd()+"/browsermob-proxy-2.1.4/bin/browsermob-proxy")
    server.start()
    time.sleep(1) #proxy server takes a while to start
    proxy=server.create_proxy()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
    driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=chrome_options)

    driver.get('https://www.saavn.com')
    driver.find_element_by_id('login-btn').click()
    username=driver.find_element_by_id('login_username')
    username.send_keys(input('Enter your email ID: '))
    password=driver.find_element_by_id('login_password')
    password.send_keys(input("Enter your password: "))
    driver.find_element_by_id('static-login-btn').click()
    #wait until home page is loaded again
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'my-music')))
    data=(driver.find_element_by_xpath('//*[@id="my-music"]/div/ol/li[2]/ol').get_attribute('outerHTML'))
    soup=BeautifulSoup(data,features='html.parser')
    list=soup.find_all('a')
    i=1
    for playlist in list:
        print(str(i)+'. '+playlist.text)
        i+=1
    i=int(input('Enter the playlist number: '))
    assert i<=len(list) and i>0
    driver.get(list[i-1].get('href'))
    #start the music :p
    i=1
    time.sleep(2)
    list_of_songs=driver.find_elements_by_xpath('//*[@id="main"]/div/section/ol/li')
    no_of_songs=len(list_of_songs)
    print('no. of songs = '+str(no_of_songs))
    # soup=BeautifulSoup(list_of_songs[0].get_attribute('innerHTML'),'html.parser')
    # print(soup.prettify())
    # exit(5)
    driver.find_element_by_class_name('play').click()
    for i in range(1,no_of_songs+1):
        proxy.new_har('req', options={'captureHeaders': False, 'captureContent': False})
        time.sleep(3) # wait for music to start
        har_data = json.dumps(proxy.har['log']['entries'][:], indent=4)
        for entry in proxy.har['log']['entries']:
            if entry['response']['content'].get('mimeType','')=='audio/mpeg':
                url=entry['request']['url']
                song=requests.get(url,stream=True)
                with open('song'+str(i)+'.mp3','wb') as file:
                    file.write(song.content)
        driver.find_element_by_id('fwd').click()
    # with open('hardata.json','w') as file:
    #     file.write(har_data)
    driver.quit()
    server.stop()