import json
import os
from datetime import datetime

import pytz
import requests
from circuitbreaker import circuit
from flask import abort, jsonify, request

from mib import app, logger
from mib.dao.message_manager import Message_Manager
from mib.models.message import Message
from mib.tasks.send_message import send_message as put_message_in_queue

USER_MS = app.config["USERS_MS_URL"]


@circuit(expected_exception=requests.RequestException)
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
        return jsonify({"message": "message already sent"}), 400

    sender = _check_user(message.sender)

    if sender["points"] < 60:
        abort(jsonify({"message": "no enough points"}), 401)

    response = requests.put(
        USER_MS + "user/points/" + str(message.sender),
        json={"points": sender["points"] - 60},
    )

    if response.status_code != 200:
        return jsonify({"message": "an error occurred"}), 500

    Message_Manager.delete(msg=message)
    return jsonify({"message": "message deleted"}), 200


@circuit(expected_exception=requests.RequestException)
def get_all_received_messages_metadata(user_id):  # noqa: E501
    """Get all received messages metadata of an user

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    _check_user(user_id)
    response = requests.get(USER_MS + "user" + "/black_list/" + str(user_id))

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


@circuit(expected_exception=requests.RequestException)
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
    _id = None

    response = requests.get(USER_MS + "user/" + str(sender))
    if response.status_code == 200:
        email_s = response.json()["email"]
        response = requests.get(USER_MS + "user/" + str(recipient))
        if response.status_code == 200:
            email_r = response.json()["email"]
            valid_users = True

    if not valid_users:
        return jsonify({"message": "user not found"}), 404

    if message_id is not None and message_id > 0:  # I have to sent a draft
        msg = Message_Manager.retrieve_by_id(message_id)
    else:
        msg = Message()

    msg.delivery_date = datetime.fromisoformat(delivery_date)  # t.localize()
    msg.is_draft = False
    msg.recipient = recipient
    msg.sender = sender
    msg.media = media
    msg.text = text

    if message_id is not None and message_id > 0:  # I have to sent a draft
        Message_Manager.update_message(msg)
        _id = msg.message_id
    else:
        _id = Message_Manager.create_message(msg)

    # send message via celery
    if os.getenv("FLASK_ENV") != "testing":  # pragma: no cover
        try:
            put_message_in_queue.apply_async(
                args=[
                    json.dumps(
                        {
                            "message_id": _id,
                            "body": "You have just received a massage",
                            "recipient": email_r,
                            "sender": email_s,
                        }
                    )
                ],  # convert to utc
                eta=msg.delivery_date.astimezone(pytz.utc),  # task execution time
                routing_key="message",  # to specify the queue
                queue="message",
            )
        except Exception as e:
            logger.exception("Send message task raised!")

    return jsonify({"id": _id}), 201


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

    if attribute not in ["is_draft", "is_read", "is_delivered", "is_deleted"]:
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

    specified_date = datetime.strptime(f"{year}-{month}-{day}T00:00", "%Y-%m-%dT%H:%M")
    end_date = datetime.strptime(f"{year}-{month}-{day}T23:59", "%Y-%m-%dT%H:%M")

    messages = Message_Manager.retrieve_by_user_id(user_id)
    messages = filter(
        lambda x: (not x.is_draft) and specified_date <= x.delivery_date <= end_date,
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
    for msg in messages:
        d = {}
        d.update({"recipient": msg.recipient})
        d.update({"sender": msg.sender})
        d.update({"has_media": msg.media is not None and len(msg.media) > 0})
        d.update({"id": msg.message_id})
        body.append(d)

    return body


@circuit(expected_exception=requests.RequestException)
def _check_user(user_id):
    response = requests.get(USER_MS + "user/" + str(user_id))

    if response.status_code != 200:
        abort(404, {"message": "user not found"})

    return response.json()
