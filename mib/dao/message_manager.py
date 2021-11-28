from flask.globals import request
from mib.dao.manager import Manager
from mib.models.message import Message
from mib import db, logger
import datetime


class Message_Manager(Manager):
    @staticmethod
    def create_message(message: Message):
        Manager.create(message=message)
        return message.message_id

    @staticmethod
    def retrieve_by_id(id_):
        Manager.check_none(id=id_)
        return Message.query.get(id_)

    @staticmethod
    def update_message(message: Message):
        Manager.update(message=message)

    @staticmethod
    def update_message_state(message_id, attr, state):
        Manager.check_none(id=message_id)
        result = False
        try:
            message = (
                db.session.query(Message)
                .filter(Message.message_id == message_id)
                .first()
            )
            if message is not None:
                setattr(message, attr, state)
                db.session.commit()
                result = True
        except Exception as e:
            db.session.rollback()
            logger.error("Exception in update_message_state ", e)

        return result

    @staticmethod
    def get_all_sent_messages_metadata(user_id):  # noqa: E501
        return (
            db.session.query(Message)
            .filter(
                Message.sender == user_id,
                Message.is_draft == False,
                Message.is_delivered == True,
            )
            .all()
        )

    @staticmethod
    def get_all_received_messages_metadata(user_id):
        return (
            db.session.query(Message)
            .filter(
                Message.recipient == user_id,
                Message.is_draft == False,
                Message.is_delivered == True,
            )
            .all()
        )

    @staticmethod
    def get_unsent_messages():
        return (
            db.session.query(Message)
            .filter(Message.is_delivered == False)
            .filter(Message.delivery_date < datetime.now())
            .filter(Message.is_draft == 0)
            .all()
        )
