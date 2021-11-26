def delete_draft(draft_id):  # noqa: E501
    """Delete a draft by id

     # noqa: E501

    :param draft_id: Message Unique ID
    :type draft_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_all_user_drafts(user_id):  # noqa: E501
    """Retrieve all user&#x27;s drafts

     # noqa: E501

    :param user_id: User Unique ID
    :type user_id: int

    :rtype: List[MessageMetadata]
    """
    return 'do some magic!'


def get_draft_by_id(draft_id):  # noqa: E501
    """Get a draft by id

     # noqa: E501

    :param draft_id: Message Unique ID
    :type draft_id: int

    :rtype: Draft
    """
    return 'do some magic!'


def save_draft(body):  # noqa: E501
    """Save a new draft

     # noqa: E501

    :param body: Create a new draft
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = DraftSave.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def update_draft(text, sender, recipient, media, draft_id):  # noqa: E501
    """Updates a draft

     # noqa: E501

    :param text: 
    :type text: str
    :param sender: 
    :type sender: int
    :param recipient: 
    :type recipient: int
    :param media: 
    :type media: strstr
    :param draft_id: Message Unique ID
    :type draft_id: int

    :rtype: None
    """
    return 'do some magic!'
