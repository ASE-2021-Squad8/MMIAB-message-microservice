import unittest
import json
import base64
import responses

from datetime import datetime
from unittest import mock

USER = "http://127.0.0.1:5000/api/"

class TestMessages(unittest.TestCase):
    def setUp(self):
        from mib import create_app
        self.app = create_app()
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        from mib.dao.message_manager import Message_Manager
        from mib.models.message import Message
        self.message_manager = Message_Manager
        self.message = Message

    def test_delete_message(self):
        # inserting a test message in the db that must be deleted to test
        # the functionality of delete message
        test_msg = self.message()
        test_msg.sender = 2
        test_msg.recipient = 1
        test_msg.text = "test_delete"
        test_msg.is_draft = False
        test_msg.is_delivered = True
        test_msg.is_read = True
        test_msg.is_deleted = False
        self.message_manager.create_message(test_msg)
        message_id = test_msg.message_id

        reply = self.client.delete(f"/api/message/{message_id}")
        data = reply.get_json()
        assert reply.status_code == 200
        assert int(data["message_id"]) == message_id

        reply = self.client.delete("/api/message/-1")
        data = reply.get_json()
        assert reply.status_code == 404

    @responses.activate
    def test_save_message(self):
        responses.add(responses.GET, USER + "user/" + str(1),
                  json={'email': 'sender@example.com', 'points': 60}, status=200)
        responses.add(responses.GET, USER + "user/" + str(2),
                  json={'email': 'recipient@example.com', 'points': 50}, status=200)

        message = dict(
            sender=1,
            recipient=2,
            text="Hello hello fantastic",
            media="",
            delivery_date=datetime(2222, 1, 1).strftime("%m/%d/%Y, %H:%M:%S")
        )
        reply = self.client.post("/api/message", data=json.dumps(message), content_type="application/json")
        assert reply.status_code == 201


