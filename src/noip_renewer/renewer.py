"""
Confirm all noip hosts that are about to expire.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import List

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# from selenium.webdriver.common.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .log import logger


class NoipRenewer:
    """
    Uses a webdriver to renew all soon-to-expire noip hosts.

    """

    def __init__(self, driver: webdriver.Firefox, username: str, password: str):
        self._driver = driver
        self.username = username
        self.password = password

    def _is_logged_in(self) -> bool:
        return iter(self._driver.find_element(By.ID, value="username"))

    def login(self):
        """Load the noip login page and enter credentials"""
        self._driver.get(url="https://www.noip.com/login")
        logger.debug("Logging in...")
        user_input = self._driver.find_element(By.ID, value="username")
        user_input.click()
        user_input.send_keys(self.username)

        pass_input = self._driver.find_element(By.ID, value="password")
        pass_input.click()
        pass_input.send_keys(self.password)
        pass_input.send_keys(Keys.RETURN)

        # Wait for presence of account dropdown menu
        WebDriverWait(self._driver, 30).until(
            EC.presence_of_element_located((By.ID, "user-email-container"))
        )

    def _find_user_container(self):
        return self._driver.find_element(By.ID, "user-email-container")

    def logout(self):
        user_cont = self._find_user_container()
        user_cont.click()

        logout_cont = user_cont.find_element(By.XPATH, "//a/i[@class='fa fa-sign-out']")
        logout_cont.click()

        # Wait for login page to load
        WebDriverWait(self._driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

    def _find_host_confirm_buttons(self) -> List[WebElement]:
        return self._driver.find_elements(
            By.XPATH,
            "//button[@class='btn btn-labeled btn-success' and text()='Confirm']",
        )

    def run(self):
        """Start confirming hosts"""
        self.login()
        logger.info("Logged in!")
        self._driver.get(url="https://my.noip.com/dynamic-dns")

        # Wait for hosts table to load
        logger.debug("Waiting for hosts table to load...")
        WebDriverWait(self._driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//thead/tr/th/span[text()='Hostname']")
            )
        )

        self.confirm_hosts()

    def confirm_hosts(self):
        """Find all hosts that are expiring soon and click their confirm buttons for renewal"""
        confirm_buttons = self._find_host_confirm_buttons()
        logger.debug(f"{confirm_buttons=}")
        for confirm in confirm_buttons:
            confirm.click()
            logger.info(f"Clicked {confirm}")
            WebDriverWait(self._driver, 30).until_not(confirm.is_displayed)
        logger.info(f"Renewed {len(confirm_buttons)} hosts.")

    def exit(self):
        """Closes the webdriver."""
        self._driver.quit()


@contextmanager
def make_noip_renewer(driver, creds_path: Path) -> NoipRenewer:
    """
        Create a NoipConfirmer context that logs out then closes the webdriver
    when it goes out of scope
    """
    try:
        with open(creds_path, encoding="utf-8") as creds_file:
            creds = iter(creds_file.readline().split(":"))

        confirmer = NoipRenewer(driver, next(creds), next(creds))
        yield confirmer
    finally:
        confirmer.logout()
        confirmer.exit()


__ALL__ = ["make_noip_renewer", "NoipRenewer"]
