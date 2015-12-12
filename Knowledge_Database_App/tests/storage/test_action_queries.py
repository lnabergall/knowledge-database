"""

"""

from unittest import TestCase
from datetime import datetime

import Knowledge_Database_App.storage.action_queries as action
import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class ActionQueryTest(TestCase, StorageTest):

    def __init__(self):
        super().__init__()
        self.content = {
            "user_id": self.session.query(orm.User.user_id).first(),
            "name": orm.Name(name="The Force", name_type="primary",
                             timestamp=datetime.utcnow()),
            "text": "The Force surrounds us and penetrates us. " +
                    "It binds the galaxy together.",
            "content_type": self.session.query(orm.ContentType).first(),
            "keywords": [orm.Keyword(keyword="Star Wars",
                                    timestamp=datetime.utcnow()),
                         orm.Keyword(keyword="Invisible force",
                                    timestamp=datetime.utcnow())],
            "citations": [orm.Citation(citation_text="Lucas, George. " +
                                       "Star Wars: A New Hope. 1977.",
                                       timestamp=datetime.utcnow())],
            "alternate_names": []
        }

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def test_store_content_piece(self):
        
