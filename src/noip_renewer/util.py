from selenium.webdriver.common.by import By

def public_ip(driver) -> str:
    driver.get(url='https://api.ipify.org')
    return driver.find_element(By.XPATH, '//body/pre').text
