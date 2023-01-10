"""Noip Renewer command line"""
from argparse import ArgumentParser
from pathlib import Path

from selenium import webdriver

from loguru import logger
from noip_renewer import Creds, make_noip_renewer

parser = ArgumentParser(
    prog="noip-renewer",
    description="Selenium-based noip host renewal automation",
)

parser.add_argument("-u", "--username", required=True)
parser.add_argument("-p", "--password", required=True)
parser.add_argument("-v", "--verbose", action="store_true")

args = parser.parse_args()

try:
    pw_path = Path(args.password)
    logger.debug(f"{pw_path=}")
    with open(pw_path, mode="r", encoding="utf-8") as pw_file:
        args.password = pw_file.read()

except FileNotFoundError as e:
    logger.debug(
        f"Treating {args.password} as a string since the path it refers to is invalid"
    )

if args.username is None or len(args.username) == 0:
    parser.print_help()
    raise ValueError(f"Invalid username: {args.username=}")

if args.password is None or len(args.password) == 0:
    parser.print_help()
    raise ValueError(f"Invalid password: {args.password=}")


credentials = Creds(args.username, args.password)
options = webdriver.FirefoxOptions()
# options.headless = True

driver = webdriver.Firefox(options=options)
with make_noip_renewer(driver, credentials) as confirmer:
    logger.info("Logged in!")
    confirmer.run()
