from celery.utils.log import get_logger
import json

from flask import current_app

from mib import create_celery, db
from mib.dao.message_manager import Message_Manager

_APP = None
logger = get_logger(__name__)
celery = create_celery(current_app)

@celery.task
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
        db.init_app(app)
    else:
        app = _APP
    # update message state
    try:
        with app.app_context():
            result = Message_Manager.update_message_state(
                tmp["message_id"], "is_delivered", True
            )
            if result:
                # TODO send notification via celery
                logger.info("Ok")

    except Exception as e:
        logger.exception("save_message raised ", e)
        raise e
    logger.info("End send_message result: " + str(result))
    return result
