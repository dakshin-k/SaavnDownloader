from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

if __name__=='__main__':
    driver=webdriver.Chrome()
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
    driver.find_element_by_class_name('play').click()
    # webdriver.Chrome().get('https://aa.cf.saavncdn.com/092/7778f356b2cc8a86545882cf96e8badc_64.mp3?Expires=1538309444&Signature=B2DVi96PDXuk6btPzF933Q0o2WWwTOYWRYfMQ5ojk-KOMQd1lEn-vUtkoBq1Xirr-E~RpzoJkd7HqwSd20PNqe0cgamEyDdLZMdjum~rSRQ~kd5IF1tgX8AkOECcV53jMQoQEn8TEUpZfdRh1NskrXJ06ztC-jhAy0Esz6HLGGt8TaeA5mG8LKV2BDELVzv41cf7hmdrT2k1gOjIi9LrwxlR2i93uNhbUH1yWhFd059QLEXptcBhNMuVlJB-yw5krdHFMr27Wt0xexOfNNjibXM7o310remNosQ1cz0nrhKx5K7Tpr77cJ6CBO2O0EOUDx3ZExgeErL-RuRvELYjRQ__&Key-Pair-Id=APKAJB334VX63D3WJ5ZQ')