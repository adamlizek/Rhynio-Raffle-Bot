import cloudscraper
import config as CONFIG
from helheim import helheim
import cryptography
import msgpack
import lzstring

key = ''

# Helheim is closed-sourced, removed their injection method and will not work without their package.
def injection(session, response):
   pass


def create_scraper(debug=False, mobile=False):
    if CONFIG.CAPTCHA_SOLVER == CONFIG.CaptchaSolver.TWO_CAPTCHA:
        session = cloudscraper.create_scraper(
            debug=debug,
            requestPostHook=injection,
            captcha={
                'provider': '2captcha',
                'api_key': CONFIG.two_captcha_api_key
            }
        )
    else:
        session = cloudscraper.create_scraper(
            debug=debug,
            requestPostHook=injection,
            captcha={
                'provider': '2captcha',
                'api_key': CONFIG.two_captcha_api_key
            }
        )

    if mobile:
        session = cloudscraper.create_scraper(
            debug=debug,
            browser={
                'mobile': True
            },
            requestPostHook=injection,
            captcha={
                'provider': '2captcha',
                'api_key': CONFIG.two_captcha_api_key
            }
        )

    return session
