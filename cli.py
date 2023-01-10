"""Noip Renewer command line"""
from pathlib import Path

from selenium import webdriver

from noip_renewer.renewer import make_noip_renewer

options = webdriver.FirefoxOptions()
options.headless = True
creds_path = Path("/home/owner/.config/noip-creds")

driver = webdriver.Firefox(options=options)
with make_noip_renewer(driver, creds_path) as confirmer:
    confirmer.run()
