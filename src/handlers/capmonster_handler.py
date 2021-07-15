from python_capmonster import NoCaptchaTaskProxyless, RecaptchaV3TaskProxyless
import config


def handle_captcha(captcha_url, captcha_data_site_key, action=None):
    print("Using Capmonster!")
    if action is None:
        capmonster = NoCaptchaTaskProxyless(client_key=config.capmonster_api_key)
        taskId = capmonster.createTask(website_key=captcha_data_site_key, website_url=captcha_url)
        response = capmonster.joinTaskResult(taskId=taskId)
    else:
        capmonster = RecaptchaV3TaskProxyless(client_key=config.capmonster_api_key)
        taskId = capmonster.createTask(website_key=captcha_data_site_key, website_url=captcha_url, minimum_score=0.7,
                                       page_action=action)
        response = capmonster.joinTaskResult(taskId=taskId)

    print(response)
    return response