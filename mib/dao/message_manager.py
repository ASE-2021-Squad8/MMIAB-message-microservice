from mib.dao.manager import Manager
from mib.models.message import Message


class Message_Manager(Manager):
    @staticmethod
    def create_user(message: Message):
        Manager.create(user=message)

    @staticmethod
    def retrieve_by_id(id_):
        Manager.check_none(id=id_)
        return Message.query.get(id_)

    # TODO: add all queries here
