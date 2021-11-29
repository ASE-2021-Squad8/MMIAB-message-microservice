import unittest
import json
import base64

from datetime import datetime


class TestDrafts(unittest.TestCase):
    def setUp(self):
        from mib import create_app

        self.app = create_app()
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        from mib.dao.message_manager import Message_Manager

        self.message_manager = Message_Manager

    def test_empty_draft(self):
        reply = self.client.post(
            "/api/message/draft",
            data=json.dumps(dict(sender=1, text="")),
            content_type="application/json",
        )
        assert reply.status_code == 400

    def test_insert_delete_draft(self):
        reply = self.client.get("/api/message/0/draft")
        assert reply.status_code == 200

        # Save a draft
        data = {"text": "Lorem ipsum dolor...", "sender": 1, "recipient": 69}
        data["delivery_date"] = datetime(2222, 1, 1).strftime("%m/%d/%Y, %H:%M:%S")
        data["media"] = base64.b64encode(b"Fantastic picture!").decode("utf-8")
        reply = self.client.post(
            "/api/message/draft",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert reply.status_code == 200

        reply = self.client.get("/api/message/1/draft")
        data = reply.get_json()
        assert reply.status_code == 200
        assert data[0]["id"] != ""
        assert data[0]["has_media"]

        draft_id = data[0]["id"]

        # Update a draft
        data = {"text": "Lorem ipsum dolor...", "sender": 1, "recipient": 1337}
        data["delivery_date"] = datetime(2222, 1, 1).strftime("%m/%d/%Y, %H:%M:%S")
        data["media"] = base64.b64encode(b"Fantastic picture!").decode("utf-8")
        reply = self.client.put(
            f"/api/message/draft/{draft_id}",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert reply.status_code == 200

        # Update a non-existing draft
        data = {"text": "Lorem ipsum dolor...", "sender": 1, "recipient": 1337}
        data["delivery_date"] = datetime(2222, 1, 1).strftime("%m/%d/%Y, %H:%M:%S")
        data["media"] = base64.b64encode(b"Fantastic picture!").decode("utf-8")
        reply = self.client.put(
            f"/api/message/draft/{1337}",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert reply.status_code == 404

        reply = self.client.get(f"/api/message/draft/{draft_id}")
        data = reply.get_json()
        assert reply.status_code == 200
        assert data["text"] == "Lorem ipsum dolor..."
        assert (
            base64.b64decode(bytearray(data["media"], "utf-8")) == b"Fantastic picture!"
        )

        reply = self.client.get(f"/api/message/draft/{1337}")
        data = reply.get_json()
        assert reply.status_code == 404

        reply = self.client.delete("/api/message/draft/1")
        data = reply.get_json()
        assert reply.status_code == 200

        reply = self.client.delete("/api/message/draft/1")
        data = reply.get_json()
        assert reply.status_code == 404
