from celery.utils.log import get_logger
import json

from celery import decorators
import requests
from mib import app 

from mib.dao.message_manager import Message_Manager


_APP = None
logger = get_logger(__name__)
USER_MS = app.config["USERS_MS_URL"]
SEND_NOTIFICATION_MS = app.config["NOTIFICATIONS_MS_URL"]


@decorators.task(name="mib.tasks.send_message.send_message")
# Don't include towards coverage as this needs to be tested via its endpoint
def send_message(json_message):  # pragma: no cover
    """Deliver a message updating is_delivered to 1
    :param json_message: data to execute the task
    :type json_message: json format string
    :raises Exception: if an error occurs
    :returns: True in case update succeed otherwise False
    :rtype: bool
    """
    logger.info("Start send_message json_message: " + json_message)
    global _APP
    tmp = json.loads(json_message)
    # lazy init
    if _APP is None:
        from mib import create_app

        app = create_app()
    else:
        app = _APP
    result = False

    try:
        with app.app_context():
            # update message state
            result = Message_Manager.update_message_state(
                tmp["message_id"], "is_delivered", True
            )
            # send email
            if result:
                email_r = tmp["recipient"]
                email_s = tmp["sender"]
                # send notification via email microservice
                _send_email(email_s, email_r, "You have just received a message!")

    except Exception as e:
        logger.exception("save_message raised ", e)
        raise e
    logger.info("End send_message result: " + str(result))
    return result


def _send_email(email_s, email_r, body):  # pragma: no cover
    # send notification via email microservice
    requests.put(
        SEND_NOTIFICATION_MS + "email",
        json={
            "sender": email_s,
            "recipient": email_r,
            "body": body,
        },
    )
