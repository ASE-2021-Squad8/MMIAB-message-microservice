def delete_message_lottery_points(message_id):  # noqa: E501
    """Deschedule a message spending points

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_all_received_messages_metadata(user_id):  # noqa: E501
    """Get all received messages metadata of an user

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


def get_all_sent_messages_metadata(user_id):  # noqa: E501
    """Get all sent messages metadata of an user

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


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
    return 'do some magic!'


def get_message_attachment(message_id):  # noqa: E501
    """Retrieves an attachment for a message

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: InlineResponse200
    """
    return 'do some magic!'


def get_message_by_id(message_id):  # noqa: E501
    """Get a message by id

     # noqa: E501

    :param message_id: Message Unique ID
    :type message_id: int

    :rtype: Message
    """
    return 'do some magic!'


def get_unsent_messages():  # noqa: E501
    """Retrieve all message that should have been sent

     # noqa: E501


    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


def send_message(body):  # noqa: E501
    """Save and schedule a new message to send

     # noqa: E501

    :param body: Create a new message
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = MessageSave.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def update_message_state(body):  # noqa: E501
    """Updates the message state

     # noqa: E501

    :param body: Update message state
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = MessageState.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
