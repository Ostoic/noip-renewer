"""
Confirm all noip hosts that are about to expire.
"""

from contextlib import contextmanager
from typing import Generator, List

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# from selenium.webdriver.common.
from selenium.webdriver.support.ui import WebDriverWait


class Creds:
    """Credentials used to login to noip account"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class LoginError(Exception):
    """Error thrown when logging in fails"""


def _is_logged_in(driver) -> bool:
    return len(driver.find_elements(By.ID, "user-email-container")) > 0


def _account_container_appeared(driver):
    if len(driver.find_elements(By.XPATH, "//div[@class='alert alert-error row']")) > 0:
        raise LoginError("Incorrect username or password")

    return _is_logged_in(driver)


class NoipRenewer:
    """
    Uses a webdriver to renew all soon-to-expire noip hosts.

    """

    RENEWER_TIMEOUT = 60

    def __init__(self, driver: webdriver.Firefox, credentials: Creds):
        self._driver = driver
        self.credentials = credentials

    def login(self):
        """Load the noip login page and enter credentials"""
        self._driver.get(url="https://www.noip.com/login")
        logger.debug(f"Logging in as {self.credentials.username}...")
        user_input = self._driver.find_element(By.ID, value="username")
        user_input.click()
        user_input.send_keys(self.credentials.username)

        pass_input = self._driver.find_element(By.ID, value="password")
        pass_input.click()
        pass_input.send_keys(self.credentials.password)
        pass_input.send_keys(Keys.RETURN)

        # Wait for presence of account dropdown menu
        WebDriverWait(self._driver, NoipRenewer.RENEWER_TIMEOUT).until(
            _account_container_appeared
        )

    def logout(self):
        """Logout by clicking through the account container"""
        if not _is_logged_in(self._driver):
            return

        account_container = self._driver.find_element(By.ID, "user-email-container")
        account_container.click()

        logout_icon = account_container.find_element(
            By.XPATH, "//a/i[@class='fa fa-sign-out']"
        )

        logout_icon.click()

        # Wait for login page to load
        WebDriverWait(self._driver, NoipRenewer.RENEWER_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

    def _find_host_confirm_buttons(self) -> List[WebElement]:
        return self._driver.find_elements(
            By.XPATH,
            "//button[@class='btn btn-labeled btn-success' and text()='Confirm']",
        )

    def run(self) -> int:
        """Run hosts renewal"""
        self._driver.get(url="https://my.noip.com/dynamic-dns")

        # Wait for hosts table to load
        logger.debug("Waiting for hosts table to load...")
        WebDriverWait(self._driver, NoipRenewer.RENEWER_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//thead/tr/th/span[text()='Hostname']")
            )
        )

        num_renewed = self.renew_hosts()
        logger.info(f"Renewed {num_renewed} hosts.")
        return num_renewed

    def renew_hosts(self) -> int:
        """Find all hosts that are expiring soon and click their confirm buttons for renewal"""
        confirm_buttons = self._find_host_confirm_buttons()
        logger.debug(f"{confirm_buttons=}")
        if len(confirm_buttons) == 0:
            return 0

        for confirm in confirm_buttons:
            confirm.click()
            logger.info(f"Clicked {confirm}")

        # Wait for all buttons to disappear before finishing.
        WebDriverWait(self._driver, NoipRenewer.RENEWER_TIMEOUT).until(
            lambda _: all(map(lambda b: not b.is_displayed(), confirm_buttons))
        )

        return len(confirm_buttons)

    def exit(self):
        """Closes the webdriver."""
        self._driver.quit()


@contextmanager
def make_noip_renewer(driver, credentials: Creds) -> Generator[NoipRenewer, None, None]:
    """
        Create a NoipConfirmer context that logs out then closes the webdriver
    when it goes out of scope
    """
    try:

        confirmer = NoipRenewer(driver, credentials)
        confirmer.login()
        yield confirmer
    finally:
        confirmer.logout()
        confirmer.exit()


__ALL__ = ["make_noip_renewer", "NoipRenewer"]
