import os

from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


DOWNLOAD_TIMEOUT = 15

url = "https://tabs.ultimate-guitar.com/tab/linkin-park/faint-guitar-pro-224026"
destination = "./tabs"
options = Options()
options.headless = True

nFiles = 1

os.mkdir(destination)

profile = FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", destination)
profile.set_preference(
    "browser.helperApps.neverAsk.saveToDisk",
    "application/octet-stream"
)

driver = webdriver.Firefox(
    options=options,
    firefox_profile=profile,
    executable_path="geckodriver.exe"
)
driver.get(url)
button = driver.find_element_by_xpath(
    '//button/span[text()="DOWNLOAD Guitar Pro TAB" '
    'or text()="DOWNLOAD Power TAB"]'
)
driver.execute_script("arguments[0].click();", button)

# kill firefox process after download completes or a timeout is reached
downloading = True
timeout = DOWNLOAD_TIMEOUT
while downloading and timeout > 0:
    sleep(0.5)
    if len(os.listdir(destination)) > nFiles:
        downloading = False
    timeout -= 0.5
driver.quit()
