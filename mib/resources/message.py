from flask import request, jsonify
import requests
from mib import logger
from mib.models.message import Message
from mib.dao.message_manager import Message_Manager
from mib.tasks import send_message as put_message_in_queue
import json
import pytz

USER = "127.0.0.1:5000/api/"


def delete_message_lottery_points(message_id):  # noqa: E501
    """Deschedule a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    return "do some magic!"


def get_all_received_messages_metadata(user_id):  # noqa: E501
    """Get all received messages metadata of an user

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    return "do some magic!"


def get_all_sent_messages_metadata(user_id):  # noqa: E501
    """Get all sent messages metadata of an user

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    return "do some magic!"


def get_daily_messages(user_id, day, month, year):  # noqa: E501
    """Gets all messages sent in a time interval (includes yet to be delivered)

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int
    :param day: day
    :type day: int
    :param month: month
    :type month: int
    :param year: year
    :type year: int

    :rtype: List[InlineResponse2001]
    """
    return "do some magic!"


def get_message_attachment(message_id):  # noqa: E501
    """Retrieves an attachment for a message

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: InlineResponse200
    """
    return "do some magic!"


def get_message_by_id(message_id):  # noqa: E501
    """Get a message by id

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: Message
    """
    return "do some magic!"


def get_unsent_messages():  # noqa: E501
    """Retrieve all message that should have been sent

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    return "do some magic!"


def send_message(body):  # noqa: E501
    """Save and schedule a new message to send

     # noqa: E501

    :param body: Create a new message
    :type body: dict | bytes

    :rtype: None
    """
    post_data = request.get_json()
    delivery_date = post_data.get("delivery_date")
    # expect it populated only when I have to send a draft
    message_id = post_data.get("message_id")
    media = post_data.get("media")
    recipient = post_data.get("recipient")
    sender = post_data.get("sender")
    text = post_data.get("text")

    valid_users = False
    email_r = None
    email_s = None
    id = None
    response = requests.get(USER + "user/" + str(sender))
    if response.status_code == 200:
        email_s = response.get_json()["email"]
        response = requests.get(USER + "user/" + str(recipient))
        if response.status_code == 200:
            email_r = response.get_json()["email"]
            valid_users = True

    if not valid_users:
        return jsonify({"message": "user not found"}), 404

    msg = Message()
    msg.delivery_date = delivery_date
    msg.is_draft = False
    msg.recipient = recipient
    msg.sender = sender
    msg.media = media
    msg.text = text
    if message_id is not None and message_id > 0:  # I have to sent a draft
        msg.message_id = message_id
        id = Message_Manager.update(msg)
    else:
        id = Message_Manager.create(msg)

        # send message via celery
        try:
            put_message_in_queue.apply_async(
                args=[
                    json.dumps(
                        {
                            "id": id,
                            "body": "You have just received a massage",
                            "recipient": email_r,
                            "sender": email_s,
                        }
                    )
                ],  #  convert to utc
                eta=delivery_date.astimezone(pytz.utc),  # task execution time
            )
        except put_message_in_queue.OperationalError as e:
            logger.exception("Send message task raised: ", e)

    return jsonify({"message": "message scheduled"}), 201


def update_message_state(body):  # noqa: E501
    """Updates the message state

    :param body: Update message state
    :type body: dict | bytes

    :rtype: None
    """
    put_body = request.get_json()
    attribute = put_body["attribute"]
    message_id = put_body["message_id"]
    state = put_body["state"]

    if attribute not in ["is_draft", "is_read", "is_delivered"]:
        return jsonify({"message": "cannot update " + str(attribute)}), 400

    msg = Message_Manager.retrieve_by_id(message_id)

    if msg is None:
        return (
            jsonify({"message": "message with id: " + str(attribute) + " not found"}),
            404,
        )

    Message_Manager.update_message_state(message_id, "attribute", state)
    return jsonify({"message": "message state updated"}), 200


def _valid_string(text):
    return not (text is None or text == "" or text.isspace())
