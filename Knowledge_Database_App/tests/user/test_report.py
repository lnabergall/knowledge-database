"""
Report Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.tests.storage import PostgresTest
from Knowledge_Database_App.tests.content.test_redis import RedisTest
from Knowledge_Database_App.storage import orm_core as orm
from Knowledge_Database_App.storage.action_queries import delete_user
from Knowledge_Database_App.user.admin import Admin
from Knowledge_Database_App.user.report import Report


class ReportTest(PostgresTest, RedisTest):
    failure = False

    @classmethod
    def setUpClass(cls):
        PostgresTest.setUpClass.__func__(cls)
        RedisTest.setUpClass.__func__(cls)
        cls.content_id = 1
        cls.report_text = "There is a problem."
        cls.report_type = "content"
        cls.author_type = "104.156.240.197"
        cls.admin = Admin(email="kyloren121323@gmail.com",
                           password="darthvader123",
                           user_name="Kylo Ren")
        cls.admin.register()
        cls.admin_report = "The problem was that, I fixed it by doing this."

    @classmethod
    def tearDownClass(cls):
        PostgresTest.tearDownClass.__func__(cls)
        RedisTest.tearDownClass.__func__(cls)

    @skipIf(failure, "Previous test failed!")
    def test_01_create(self):
        try:
            self.__class__.report = Report(
                content_id=self.__class__.content_id,
                report_text=self.__class__.report_text,
                report_type=self.__class__.report_type,
                author_type=self.__class__.author_type
            )
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.report.report_text, 
                                 self.__class__.report_text)
                self.assertEqual(self.__class__.report.content_id, 
                                 self.__class__.content_id)
                self.assertEqual(self.__class__.report.report_type, 
                                 self.__class__.report_type)
                self.assertEqual(self.__class__.report.report_status, 
                                 "pending")
                self.assertEqual(self.__class__.report.author_type, 
                                 self.__class__.author_type)
                self.assertIsInstance(self.__class__.report.timestamp, 
                                      datetime)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_02_submit(self):
        try:
            self.__class__.report.submit()
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.report.admin_id, int)
                self.assertEqual(self.__class__.report.report_status, "open")
                self.assertIsInstance(self.__class__.report.report_id, int)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_03_bulk_retrieve(self):
        try:
            admin_reports = Report.bulk_retrieve(
                admin_id=self.__class__.admin.user_id, page_num=0)
            content_reports = Report.bulk_retrieve(
                content_id=self.__class__.content_id, page_num=0)
            with self.assertRaises(NotImplementedError):
                author_reports = Report.bulk_retrieve(
                    ip_address=self.__class__.author_type, page_num=0)
            admin_reports_resolved = Report.bulk_retrieve(
                admin_id=self.__class__.admin.user_id,
                report_status="resolved", page_num=0)
            content_reports_resolved = Report.bulk_retrieve(
                content_id=self.__class__.content_id,
                report_status="resolved", page_num=0)
            author_reports_resolved = Report.bulk_retrieve(
                ip_address=self.__class__.author_type,
                report_status="resolved", page_num=0)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                for report in admin_reports:
                    self.assertIsInstance(report, Report)
                self.assertIn(self.__class__.report, admin_reports)
                for report in content_reports:
                    self.assertIsInstance(report, Report)
                self.assertIn(self.__class__.report, content_reports)
                for report in admin_reports_resolved:
                    self.assertIsInstance(report, Report)
                for report in content_reports_resolved:
                    self.assertIsInstance(report, Report)
                for report in author_reports_resolved:
                    self.assertIsInstance(report, Report)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_04_resolve(self):
        try:
            self.__class__.report.resolve(self.__class__.admin_report)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.report.admin_report, 
                                 self.__class__.admin_report)
                self.assertIsInstance(self.__class__.report.res_timestamp, 
                                      datetime)
                self.assertEqual(self.__class__.report.report_status, 
                                 "resolved")
                admin_reports_resolved = Report.bulk_retrieve(
                    admin_id=self.__class__.admin.user_id,
                    report_status="resolved", page_num=0)
                content_reports_resolved = Report.bulk_retrieve(
                    content_id=self.__class__.content_id,
                    report_status="resolved", page_num=0)
                author_reports_resolved = Report.bulk_retrieve(
                    ip_address=self.__class__.author_type,
                    report_status="resolved", page_num=0)
                self.assertIn(self.__class__.report, admin_reports_resolved)
                self.assertIn(self.__class__.report, content_reports_resolved)
                self.assertIn(self.__class__.report, author_reports_resolved)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_05_json_ready(self):
        try:
            json_ready_dict = self.__class__.report.json_ready
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_dict["report_id"],
                                 self.__class__.report.report_id)
                self.assertEqual(json_ready_dict["content_id"],
                                 self.__class__.report.content_id)
                self.assertEqual(json_ready_dict["report_text"],
                                 self.__class__.report.report_text)
                self.assertEqual(json_ready_dict["report_type"],
                                 self.__class__.report.report_type)
                self.assertEqual(json_ready_dict["author_type"],
                                 self.__class__.report.author_type)
                self.assertEqual(json_ready_dict["author_id"],
                                 self.__class__.report.author_id)
                self.assertEqual(json_ready_dict["admin_report"],
                                 self.__class__.report.admin_report)
                self.assertEqual(json_ready_dict["admin_id"],
                                 self.__class__.report.admin_id)
                self.assertEqual(json_ready_dict["report_status"],
                                 self.__class__.report.report_status)
                self.assertEqual(json_ready_dict["timestamp"],
                                 self.__class__.report.timestamp)
                self.assertEqual(json_ready_dict["res_timestamp"],
                                 self.__class__.report.res_timestamp)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))
