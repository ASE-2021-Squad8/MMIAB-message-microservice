from flask import request, jsonify, abort
import requests
from mib import logger
from mib.models.message import Message
from mib.dao.message_manager import Message_Manager
from mib.tasks.send_message import send_message as put_message_in_queue
import json
import pytz
import json
from datetime import datetime

USER = "http://127.0.0.1:5000/api/"


def delete_message_lottery_points(message_id):  # noqa: E501
    """Deschedule a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    message = Message_Manager.retrieve_by_id(message_id)
    if message is None:
        return jsonify({"message": "message not found"}), 404

    if message.delivery_date < datetime.now():
        return jsonify({"message": "message already sent"}), 404

    sender = _check_user(message.sender)

    if sender["points"] < 60:
        abort(jsonify({"message": "no enough points"}), 400)

    response = requests.put(
        USER + "user/points/" + str(message.sender),
        json={"points": sender["points"] - 60},
    )

    if response.status_code != 200:
        return jsonify({"message": "an error occured"}), 500

    Message_Manager.delete(msg=message)
    return jsonify({"message": "message deleted"}), 200


def get_all_received_messages_metadata(user_id):  # noqa: E501
    """Get all received messages metadata of an user

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    _check_user(user_id)
    response = requests.get(USER + "user" + "/black_list/" + str(user_id))

    json_response = response.json()
    black_list = [obj["id"] for obj in json_response["blacklisted"]]

    tmp_list = Message_Manager.get_all_received_messages_metadata(user_id)
    messages_list = []
    for msg in tmp_list:
        if msg.sender not in black_list:
            messages_list.append(msg)

    body = _build_metadata_list(messages_list)

    return jsonify(body), 200


def get_all_sent_messages_metadata(user_id):  # noqa: E501
    """Get all sent messages metadata of an user


    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    _check_user(user_id)

    messages_list = Message_Manager.get_all_sent_messages_metadata(user_id=user_id)

    body = _build_metadata_list(messages_list)
    return jsonify(body), 200


def get_message_attachment(message_id):  # noqa: E501
    """Retrieves an attachment for a message

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: JSON
    """
    message = Message_Manager.retrieve_by_id(message_id)
    if message is None:
        return jsonify({"message": "message not found"}), 404

    return jsonify({"media": message.media.decode("utf-8")})


def get_message_by_id(message_id):  # noqa: E501
    """Get a message by id

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: Message
    """
    message = Message_Manager.retrieve_by_id(message_id)
    if message is None:
        return jsonify({"message": "message not found"}), 404

    return jsonify(message.serialize())


def get_unsent_messages():  # noqa: E501
    """Retrieve all message that should have been sent

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    messages = Message_Manager.get_unsent_messages()
    return jsonify(_build_metadata_list(messages)), 200


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
    media = bytearray(post_data.get("media"), "utf-8")
    recipient = post_data.get("recipient")
    sender = post_data.get("sender")
    text = post_data.get("text")

    valid_users = False
    email_r = None
    email_s = None
    id = None
    response = requests.get(USER + "user/" + str(sender))
    if response.status_code == 200:
        email_s = response.json()["email"]
        response = requests.get(USER + "user/" + str(recipient))
        if response.status_code == 200:
            email_r = response.json()["email"]
            valid_users = True

    if not valid_users:
        return jsonify({"message": "user not found"}), 404

    msg = Message()
    msg.delivery_date = datetime.strptime(delivery_date, "%m/%d/%Y, %H:%M:%S")
    msg.is_draft = False
    msg.recipient = recipient
    msg.sender = sender
    msg.media = media
    msg.text = text
    if message_id is not None and message_id > 0:  # I have to sent a draft
        msg.message_id = message_id
        id = Message_Manager.update(msg)
    else:
        id = Message_Manager.create_message(msg)

    # send message via celery
    """
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
            eta=msg.delivery_date.astimezone(pytz.utc),  # task execution time
        )
    except Exception as e:
        logger.exception("Send message task raised!")
    """
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
    state = put_body["value"]

    if attribute not in ["is_draft", "is_read", "is_delivered"]:
        return jsonify({"message": "cannot update " + str(attribute)}), 400

    msg = Message_Manager.retrieve_by_id(message_id)

    if msg is None:
        return (
            jsonify({"message": "message with id: " + str(attribute) + " not found"}),
            404,
        )

    Message_Manager.update_message_state(message_id, attribute, state)
    return jsonify({"message": "message state updated"}), 200


def get_messages_for_day(user_id, year, month, day):
    """Returns messages sent in a specific day

    :param year: year
    :type year: int
    :param month: month
    :type month: int
    :param day: day
    :type day: int
    """

    _check_user(user_id)

    specified_date = datetime.strptime(
        f"{month}/{day}/{year}, 00:00:00", "%m/%d/%Y, %H:%M:%S"
    )
    end_date = datetime.strptime(
        f"{month}/{day}/{year}, 23:59:59", "%m/%d/%Y, %H:%M:%S"
    )

    messages = Message_Manager.retrieve_by_user_id(user_id)
    messages = filter(
        lambda x: x.delivery_date >= specified_date and x.delivery_date <= end_date,
        messages,
    )

    return jsonify(list(map(lambda x: x.serialize(), messages)))


def delete_received_message(message_id, user_id):
    _check_user(user_id)
    message = Message_Manager.retrieve_by_id(message_id)
    if message is None or message.recipient != user_id:
        return jsonify({"message": "Wrong received message id"}), 400

    Message_Manager.delete(msg=message)
    return jsonify({"message": "Received message has beed deleted"}), 200


def _valid_string(text):
    return not (text is None or text == "" or text.isspace())


def _build_metadata_list(messages):
    body = []
    d = {}
    for msg in messages:
        d.update({"recipient": msg.recipient})
        d.update({"sender": msg.sender})
        d.update({"has_media": msg.media is not None and len(msg.media) > 0})
        d.update({"id": msg.message_id})
        body.append(d)

    return body


def _check_user(user_id):
    response = requests.get(USER + "user/" + str(user_id))

    if response.status_code != 200:
        abort(jsonify({"message": "user not found"}), 404)

    return response.json()
