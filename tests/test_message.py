import unittest
import json
import base64
import responses

from datetime import datetime


class TestMessages(unittest.TestCase):
    def setUp(self):
        from mib import create_app

        self.app = create_app()
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        from mib.dao.message_manager import Message_Manager
        from mib.models.message import Message
        from mib.resources.message import USER
        from mib import db

        self.message_manager = Message_Manager
        self.message = Message
        self.db = db
        self.user_service_endpoint = USER

    @responses.activate
    def test_delete_message(self):
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(1),
            json={"email": "recipient@example.com", "points": 50},
            status=200,
        )
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(3),
            json={"email": "recipient@example.com", "points": 50},
            status=200,
        )
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

        # wrong recipient id
        reply = self.client.delete(f"/api/message/received/{message_id}/{3}")
        # expect bad request
        assert reply.status_code == 400
        reply = self.client.delete(f"/api/message/received/{message_id}/{1}")

        assert reply.status_code == 200

        # now expect to not found the message
        reply = self.client.get(f"/api/message/{message_id}")

        assert reply.status_code == 404

    @responses.activate
    def test_save_message(self):
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(1),
            json={"email": "sender@example.com", "points": 60},
            status=200,
        )
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(2),
            json={"email": "recipient@example.com", "points": 50},
            status=200,
        )
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + "black_list/" + str(2),
            json={"blacklisted": []},
            status=200,
        )

        message = dict(
            sender=1,
            recipient=2,
            text="Hello hello fantastic",
            media=base64.b64encode(b"Fantastic picture!").decode("utf-8"),
            delivery_date=datetime(2222, 1, 1).isoformat(),
        )
        reply = self.client.post(
            "/api/message", data=json.dumps(message), content_type="application/json"
        )
        assert reply.status_code == 201

        # update message state
        reply = self.client.put(
            "/api/message",
            data=json.dumps(
                {"attribute": "is_delivered", "value": True, "message_id": 1}
            ),
            content_type="application/json",
        )
        assert reply.status_code == 200

        # retrieve received message
        reply = self.client.get(f"/api/message/{2}/received/metadata")
        assert reply.status_code == 200
        json_data = reply.get_json()
        # expect one message
        assert len(json_data) == 1
        assert json_data[0]["has_media"]

        # retrieve the message content
        reply = self.client.get(f"/api/message/{1}")
        json_data = reply.get_json()
        assert reply.status_code == 200
        assert json_data["text"] == "Hello hello fantastic"

        # check there's a message sent with that delivery date
        reply = self.client.get(f"/api/message/{1}/sent/{2222}/{1}/{1}")
        json_data = reply.get_json()
        assert len(json_data) == 1

        # retrieve the message attachment
        reply = self.client.get(f"/api/message/{1}/attachment")
        json_data = reply.get_json()
        assert reply.status_code == 200
        assert (
            base64.b64decode(bytearray(json_data["media"], "utf-8"))
            == b"Fantastic picture!"
        )

        reply = self.client.get(f"/api/message/{1337}/attachment")
        assert reply.status_code == 404

    @responses.activate
    def test_errors(self):
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(1),
            json={"email": "sender@example.com", "points": 50},
            status=200,
        )
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(2),
            json={"email": "sender@example.com", "points": 60},
            status=200,
            content_type="application/json",
        )
        responses.add(
            responses.PUT,
            url=self.user_service_endpoint + "user/points/" + str(2),
            status=200,
        )
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(252),
            json={"email": "recipient@example.com", "points": 50},
            status=404,
        )

        # update illegal attribute
        reply = self.client.put(
            "/api/message",
            data=json.dumps({"attribute": "sender", "value": True, "message_id": 1}),
            content_type="application/json",
        )
        # expect bad request
        assert reply.status_code == 400

        # update non-existing message
        reply = self.client.put(
            "/api/message",
            data=json.dumps(
                {"attribute": "is_read", "value": True, "message_id": 1005}
            ),
            content_type="application/json",
        )
        # expect message not found
        assert reply.status_code == 404

        # send messsage
        message = dict(
            sender=1,
            recipient=252,
            text="Hello hello fantastic",
            media=base64.b64encode(b"Fantastic picture!").decode("utf-8"),
            delivery_date=datetime(2222, 1, 1).isoformat(),
        )
        reply = self.client.post(
            "/api/message", data=json.dumps(message), content_type="application/json"
        )
        # expect user not found
        assert reply.status_code == 404

        reply = self.client.delete(f"/api/lottery/{1}")

        # expect message not found
        assert (
            reply.status_code == 404
            and reply.get_json()["message"] == "message not found"
        )

    @responses.activate
    def test_delete_lottery_message(self):
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(1),
            json={"email": "sender@example.com", "points": 50},
            status=200,
        )
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/" + str(2),
            json={"email": "sender@example.com", "points": 60},
            status=200,
            content_type="application/json",
        )
        responses.add(
            responses.PUT,
            url=self.user_service_endpoint + "user/points/" + str(2),
            status=200,
        )
        # send message
        message = dict(
            sender=2,
            recipient=1,
            text="Hello hello fantastic",
            media=base64.b64encode(b"Fantastic picture!").decode("utf-8"),
            delivery_date=datetime(2222, 1, 1).isoformat(),
        )

        reply = self.client.post(
            "/api/message",
            data=json.dumps(message),
            content_type="application/json",
        )
        # expect created
        assert reply.status_code == 201

        reply = self.client.delete(f"/api/lottery/{1}")
        # sender has enough points
        assert reply.status_code == 200
