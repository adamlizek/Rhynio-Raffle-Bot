import config as CONFIG
from src.handlers import anticaptcha_handler, two_captcha_handler, capmonster_handler
from python_capmonster.exceptions import CapmonsterException


def handle_captcha(captcha_url, captcha_data_site_key, action=None, invisible=False, hcaptcha=False):
    if CONFIG.CAPTCHA_SOLVER == CONFIG.CaptchaSolver.TWO_CAPTCHA:
        return two_captcha_handler.handle_captcha(captcha_url, captcha_data_site_key, action=action, invisible=invisible, hcaptcha=hcaptcha)

    elif CONFIG.CAPTCHA_SOLVER == CONFIG.CaptchaSolver.ANTI_CAPTCHA:
        return anticaptcha_handler.handle_captcha(captcha_url, captcha_data_site_key, action=action, invisible=invisible)

    else:
        try:
            return capmonster_handler.handle_captcha(captcha_url, captcha_data_site_key, action=action)
        except CapmonsterException:
            return 'error'


def handle_image_captcha(base64_image):
    return two_captcha_handler.handle_image_captcha(base64_image)
