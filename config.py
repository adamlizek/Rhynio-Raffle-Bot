from pathlib import Path
import os
import sys
import polling
from enum import Enum

class CaptchaSolver(Enum):
    TWO_CAPTCHA = 1,
    ANTI_CAPTCHA = 2,
    CAPMONSTER_CAPTCHA = 3,


RHYNIO_VERSION = 'Rhynio v0.3.30'

# ================
# ===== KEYS =====
# ================
two_captcha_api_key = ''
anticaptcha_api_key = ''
capmonster_api_key = ''
license_key = ''
global_webhook = ''
token = ''

# =======================
# ===== API Servers =====
# =======================
address_api_endpoint = ''
auth_api_endpoint = ''


'''
BOT OPTIONS (CHANGABLE IN UI)
'''
DESIRED_INSTANCES = 1
WEBHOOK = ''
GMAIL_EMAIL = ''
GMAIL_PASSWORD = ''
PROXY_LIST_NAME = 'main_list'
CAPTCHA_SOLVER = CaptchaSolver.TWO_CAPTCHA


# ========================
# ===== BOT SETTINGS =====
# ========================
DEBUG_MODE = True
SHOW_FAILURE = False
LOG_ENTRIES = True
USE_FAKER = False


# ==========================
# ===== CAPTCHA CONFIG =====
# ==========================
class CaptchaType(Enum):
    CAPTCHA_TYPE_TWO = 2

TWO_CAPTCHA_URL_IN = 'https://2captcha.com/in.php'
TWO_CAPTCHA_URL_OUT = 'https://2captcha.com/res.php'


# =========================
# ===== MISCELLANEOUS =====
# =========================
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    try:
        application_path = os.path.dirname(__file__)
    except NameError:
        application_path = os.getcwd()

ROOT = str(Path(application_path))
