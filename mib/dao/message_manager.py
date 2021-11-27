from mib.dao.manager import Manager
from mib.models.message import Message
from mib import db, logger


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
    def retrieve_by_user_id(user_id):
        Manager.check_none(id=user_id)
        return db.session.query(Message).filter(Message.sender == user_id).all()


# TODO: add all queries here
