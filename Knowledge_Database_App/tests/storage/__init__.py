
from Knowledge_Database_App.storage import action_queries
from Knowledge_Database_App.storage.orm_core import StorageHandler


class StorageTest(StorageHandler):
    """
    Base class for storage tests. Automatically manages sessions and
    resets the Postgres database after each test.
    """

    def setup(self):
        self.session.begin_nested()

    def call(self, function, *args, **kwargs):
        if function.__name__ in dir(action_queries):
            self.session.begin_nested()
        return super().call(self, function, *args, **kwargs)

    def teardown(self):
        self.session.rollback()
        self._close()
