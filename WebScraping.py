import requests
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
import image_processing_test

webbrowser = webdriver.Edge('msedgedriver.exe')
webbrowser.get('http://app.vr.org.vn/ptpublic/ThongtinptPublic.aspx')
fill_in_license_plate = webbrowser.find_element_by_id('txtBienDK')
fill_in_license_plate.send_keys('51F86840T')
fill_in_license_code = webbrowser.find_element_by_id('TxtSoTem')
fill_in_license_code.send_keys('KD-2688613')
captcha_img = webbrowser.find_element_by_id('captchaImage')
src = captcha_img.get_attribute('src')
urllib.request.urlretrieve(src, "captcha.png")

submit_btn = webbrowser.find_element_by_id('CmdTraCuu')
submit_btn.submit()
webbrowser.close()
image_processing_test.CV2_test()