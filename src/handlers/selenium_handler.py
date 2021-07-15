import zipfile
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import config
from enum import Enum

'''
SELENIUM CONFIG
'''
class OperatingSystem(Enum):
    WINDOWS = 1
    LINUX = 2
    MAC = 3


OPERATING_SYSTEM = OperatingSystem.WINDOWS
USE_PROXY = True
USE_HEADLESS = False
USE_USER_AGENT = False
FULL_PAGE_LOAD = True


# Setting proxy for Selenium to connect through
def set_proxy(proxy):
    p_parsed = [x.strip() for x in proxy.split(':')]

    global CURRENT_HOST
    global CURRENT_PORT
    global CURRENT_USER
    global CURRENT_PASS
    global background_js

    CURRENT_HOST = p_parsed[0]
    CURRENT_PORT = p_parsed[1]
    CURRENT_USER = p_parsed[2]
    CURRENT_PASS = p_parsed[3]

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (CURRENT_HOST, CURRENT_PORT, CURRENT_USER, CURRENT_PASS)


# Used to dynamically set the proxy every run
manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""


def get_proxy():
    return {
        'HOST': CURRENT_HOST,
        'PORT': CURRENT_PORT,
        'USER': CURRENT_USER,
        'PASS': CURRENT_PASS
    }


def get_chromedriver(proxy, user_agent=None, fast_load=False):
    print("Initializing bot, setting options...")

    if OPERATING_SYSTEM == OperatingSystem.WINDOWS:
        chrome_path = config.ROOT + '/data/driver/chromedriver.exe'
    elif OPERATING_SYSTEM == OperatingSystem.MAC:
        chrome_path = config.ROOT + '/data/driver/chromedriver'

    chrome_options = webdriver.ChromeOptions()

    if len([x.strip() for x in proxy.split(':')]) == 2:
        proxy += ":user:pass"

    set_proxy(proxy)
    plugin_file = config.ROOT + '/data/driver/proxy_auth_plugin.zip'

    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    chrome_options.add_extension(plugin_file)

    print("     Proxy Enabled Using Address: [" +
          CURRENT_HOST + ":" +
          CURRENT_PORT + ":" +
          CURRENT_USER + ":" +
          CURRENT_PASS + "]")

    print("     User Agents Enabled")
    if user_agent is None:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    chrome_options.add_argument('--user-agent=%s' % user_agent)

    caps = DesiredCapabilities().CHROME

    if fast_load:
        caps["pageLoadStrategy"] = "none"  # complete
    else:
        caps["pageLoadStrategy"] = "normal"  # complete

    driver = webdriver.Chrome(desired_capabilities=caps, executable_path=chrome_path, chrome_options=chrome_options)

    print("Bot initialized!\n")

    return driver
