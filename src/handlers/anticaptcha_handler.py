from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask, RecaptchaV3TaskProxyless
from python_anticaptcha.exceptions import AnticaptchaException
import config as CONFIG


def handle_captcha(captcha_url, captcha_data_site_key, action=None, invisible=False):
    try:
        print('Handling Anticaptcha!')
        client = AnticaptchaClient(CONFIG.anticaptcha_api_key)

        if action is None:
            task = NoCaptchaTaskProxylessTask(captcha_url, captcha_data_site_key, is_invisible=invisible)
        else:
            task = RecaptchaV3TaskProxyless(
                website_url=captcha_url, website_key=captcha_data_site_key, page_action=action, min_score=0.3
            )

        job = client.createTask(task)
        job.join()
        response = job.get_solution_response()

        if len(response) > 10:
            return response
        else:
            return 'Failed'

    except AnticaptchaException as e:
        print(str(e))
        return 'Failed'
