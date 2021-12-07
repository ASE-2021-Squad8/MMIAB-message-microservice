from mib import db
import datetime


class Message(db.Model):
    """Final message object, used for initial delivery, drafts, composition"""

    SERIALIZE_LIST = {
        "text",
        "sender",
        "recipient",
        "delivery_date",
        "is_draft",
        "is_deleted",
        "is_read",
        "is_delivered",
        "message_id",
    }
    message_id: int
    text: str
    sender: int
    recipient: int
    media: bytearray
    delivery_date: datetime
    is_draft: bool
    is_delivered: bool
    is_read: bool
    is_deleted: bool

    __tablename__ = "Message"

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String())
    delivery_date = db.Column(db.DateTime)
    sender = db.Column(db.Integer)
    recipient = db.Column(db.Integer)
    media = db.Column(db.LargeBinary)
    is_draft = db.Column(db.Boolean, default=True)
    is_delivered = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    # to take into account only to received message
    is_deleted = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def serialize(self):
        return dict([(k, self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
