from flask import jsonify, abort
from mib.dao.message_manager import Message_Manager
import connexion

def delete_draft(draft_id):  # noqa: E501
    """Delete a draft by id

    :param draft_id: Message Unique ID
    :type draft_id: int

    :rtype: JSON
    """

    message = Message_Manager.retrieve_by_id(draft_id)
    if message is not None and message.is_draft:
        Message_Manager.delete(message)
    else:
        return jsonify({"message": "draft not found"}), 404

    return jsonify({"message": "success"}), 200


def get_all_user_drafts(user_id):  # noqa: E501
    """Retrieve all user's drafts

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """

    messages = Message_Manager.retrieve_by_user_id(user_id)
    messages = filter(lambda x: x.is_draft, messages)

    result = []
    for message in messages:
        result.append(
            {
                "sender": message.sender,
                "recipient": message.recipient,
                "has_media": message.media is not None and len(message.media) > 0,
            }
        )

    return jsonify(result)


def get_draft_by_id(draft_id):  # noqa: E501
    """Get a draft by id

     # noqa: E501

    :param draft_id: Message Unique ID
    :type draft_id: int

    :rtype: Draft
    """

    message = Message_Manager.retrieve_by_id(draft_id)
    if message is None or not message.is_draft:
        return jsonify({"message": "draft not found"}), 404

    draft = {"sender": message.sender, "recipient": message.recipient, "text": message.text, "media": message.media}    

    return jsonify(draft)


def save_draft(body):  # noqa: E501
    """Save a new draft

    :param body: Create a new draft
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()
        draft = Message()
        draft.text = body["text"]
        draft.sender = body["sender"]
        
        if "recipient" in body and body["recipient"] != "":
            draft.recipient = body["recipient"]
        
        if "media" in body and body["media"] != "":
            draft.media = body["media"]
        
        if "delivery_date" in body and body["delivery_date"] != "":
            draft.delivery_date = body["delivery_date"]

        Message_Manager.create_message(draft)
    else:
        abort(400)

    return jsonify({"message": "success"})


def update_draft(draft_id, body):  # noqa: E501
    """Updates a draft

    :param body: Create a new draft
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        draft = Message_Manager.retrieve_by_id(draft_id)
        if not draft.is_draft:
            jsonify({"message": "not a draft"}), 400

        body = connexion.request.get_json()
        draft.text = body["text"]
        draft.sender = body["sender"]
        
        if "recipient" in body and body["recipient"] != "":
            draft.recipient = body["recipient"]
        
        if "media" in body and body["media"] != "":
            draft.media = body["media"]
        
        if "delivery_date" in body and body["delivery_date"] != "":
            draft.delivery_date = body["delivery_date"]

        Message_Manager.create_message(draft)
    else:
        abort(400)

    return jsonify({"message": "success"})
