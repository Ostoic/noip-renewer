"""Noip Renewer command line"""
from argparse import ArgumentParser
from pathlib import Path

from loguru import logger
from selenium import webdriver

from noip_renewer.renewer import Creds, make_noip_renewer


def cli():
    parser = ArgumentParser(
        prog="noip_renewer",
        description="Selenium-based noip host renewal automation",
    )

    parser.add_argument("-u", "--username", required=True, help="Your No-IP account username")

    parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="A path to a file containing the password, or the actual password",
    )

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--headless", default=False, action="store_true", help="Hide the web browser window"
    )

    args = parser.parse_args()
    logger.debug(f"{args=}")

    try:
        pw_path = Path(args.password)
        with open(pw_path, mode="r", encoding="utf-8") as pw_file:
            args.password = pw_file.read()

    except FileNotFoundError as e:
        logger.debug("Treating password as a string since the path it refers to is invalid")

    if args.username is None or len(args.username) == 0:
        parser.print_help()
        raise ValueError(f"Invalid username: {args.username=}")

    if args.password is None or len(args.password) == 0:
        parser.print_help()
        raise ValueError(f"Invalid password: {args.password=}")

    credentials = Creds(args.username, args.password)
    options = webdriver.FirefoxOptions()
    options.headless = args.headless

    driver = webdriver.Firefox(options=options)

    with make_noip_renewer(driver, credentials) as renewer:
        logger.info("Logged in!")
        renewer.run()
