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
import eyed3 #to write MP3 tag data
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
    track_names=[]
    album_names=[]
    icon_urls=[]
    for li in list_of_songs:
        soup=BeautifulSoup(li.get_attribute('outerHTML'),'html.parser')
        div = soup.find('div', attrs={'itemprop': 'track'})
        trackname = trackname=div.find('meta',itemprop='name')['content']
        albumname=div.find('meta',itemprop='inAlbum')['content']
        iconurl = div.find('meta', itemprop='image')['content']
        #Higer quality :p
        iconurl = iconurl.replace('150x150', '500x500')
        track_names.append(trackname)
        album_names.append(albumname)
        icon_urls.append(iconurl)
        print('Found '+trackname+' from '+albumname)
    assert len(icon_urls)==len(track_names)==len(album_names)==no_of_songs
    driver.find_element_by_class_name('play').click()
    for i in range(1,no_of_songs+1):
        proxy.new_har('req', options={'captureHeaders': False, 'captureContent': False})
        time.sleep(3) # wait for music to start
        for entry in proxy.har['log']['entries']:
            if entry['response']['content'].get('mimeType','')=='audio/mpeg':
                url=entry['request']['url']
                song=requests.get(url,stream=True)
                # some track names are like Surviva (From "Vivegam" ) and the quotes are causing a problem
                index=track_names[i-1].find("(")
                if index!=-1:
                    track_names[i-1]=track_names[i-1][:index]
                index=album_names[i-1].find('"')
                if index!=-1:
                    album_names[i-1]=album_names[i-1].split('"')[1]
                with open(track_names[i-1]+'.mp3','wb') as file:
                    file.write(song.content)
                icon=requests.get(icon_urls[i-1])
                with open(album_names[i-1]+'.jpg','wb') as file:
                    file.write(icon.content)
                #write title and album name to downloaded mp3 file
                audiofile=eyed3.load(track_names[i-1]+'.mp3')
                audiofile.tag.album=album_names[i-1]
                audiofile.tag.title=track_names[i-1]
                audiofile.tag.images.set(3,img_data=None, mime_type=None,img_url=icon_urls[i-1])
                audiofile.tag.save()
                print('Downloaded '+track_names[i-1])
                break #exit the for loop and go on to the next song
        driver.find_element_by_id('fwd').click()
    driver.quit()
    server.stop()