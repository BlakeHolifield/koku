#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""Test the HCS task."""
import logging
from datetime import timedelta
from unittest.mock import patch

from api.models import Provider
from api.utils import DateHelper
from hcs.test import HCSTestCase

LOG = logging.getLogger(__name__)


def enable_hcs_processing_mock(schema=True):
    tf = schema

    return tf


@patch("hcs.tasks.enable_hcs_processing", enable_hcs_processing_mock)
@patch("hcs.daily_report.ReportHCS.generate_report")
class TestHCSTasks(HCSTestCase):
    """Test cases for HCS Celery tasks."""

    @classmethod
    def setUpClass(cls):
        """Set up the class."""
        super().setUpClass()
        cls.today = DateHelper().today
        cls.yesterday = cls.today - timedelta(days=1)
        cls.provider = Provider.PROVIDER_AWS
        cls.provider_uuid = "cabfdddb-4ed5-421e-a041-311b75daf235"

    def test_get_report_dates(self, mock_report):
        """Test with start and end dates provided"""
        from hcs.tasks import collect_hcs_report_data

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            start_date = self.yesterday
            end_date = self.today
            collect_hcs_report_data(self.schema, self.provider, self.provider_uuid, start_date, end_date)

            self.assertIn("[collect_hcs_report_data]", _logs.output[0])

    def test_get_report_no_start_date(self, mock_report):
        """Test no start or end dates provided"""
        from hcs.tasks import collect_hcs_report_data

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            collect_hcs_report_data(self.schema, self.provider, self.provider_uuid)

            self.assertIn("[collect_hcs_report_data]", _logs.output[0])

    def test_get_report_no_end_date(self, mock_report):
        """Test no start end provided"""
        from hcs.tasks import collect_hcs_report_data

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            start_date = self.yesterday
            collect_hcs_report_data(self.schema, self.provider, self.provider_uuid, start_date)

            self.assertIn("[collect_hcs_report_data]", _logs.output[0])

    def test_get_report_invalid_provider(self, mock_report):
        """Test invalid provider"""
        from hcs.tasks import collect_hcs_report_data

        enable_hcs_processing_mock.tf = False

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            start_date = self.yesterday
            collect_hcs_report_data(self.schema, "bogus", self.provider_uuid, start_date)

            self.assertIn("[SKIPPED] HCS report generation", _logs.output[0])

    def test_schema_no_acct_prefix(self, mock_report):
        """Test no start end provided"""
        from hcs.tasks import collect_hcs_report_data

        collect_hcs_report_data("10001", self.provider, self.provider_uuid, self.yesterday)

        self.assertEqual("acct10001", self.schema)

    @patch("hcs.tasks.collect_hcs_report_data")
    def test_get_report_with_manifest(self, mock_report, rd):
        """Test invalid provider"""
        from hcs.tasks import collect_hcs_report_data_from_manifest

        manifests = [
            {
                "schema_name": self.schema,
                "provider_type": self.provider,
                "provider_uuid": self.provider_uuid,
                "tracing_id": self.provider_uuid,
            }
        ]

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            collect_hcs_report_data_from_manifest(manifests)

            self.assertIn("[collect_hcs_report_data_from_manifest]", _logs.output[0])
            self.assertIn(f"schema_name: {self.schema}", _logs.output[0])
            self.assertIn(f"provider_type: {self.provider}", _logs.output[0])
            self.assertIn(f"provider_uuid: {self.provider_uuid}", _logs.output[0])
            self.assertIn("start:", _logs.output[0])
            self.assertIn("end:", _logs.output[0])

    @patch("hcs.tasks.collect_hcs_report_data")
    def test_get_report_with_manifest_and_dates(self, mock_report, rd):
        """Test HCS reports using manifest"""
        from hcs.tasks import collect_hcs_report_data_from_manifest

        manifests = [
            {
                "schema_name": self.schema,
                "provider_type": self.provider,
                "provider_uuid": self.provider_uuid,
                "start": self.today.strftime("%Y-%m-%d"),
                "end": self.yesterday.strftime("%Y-%m-%d"),
            }
        ]

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            collect_hcs_report_data_from_manifest(manifests)
            self.assertIn("using start and end dates from the manifest for HCS processing", _logs.output[0])

    @patch("hcs.tasks.collect_hcs_report_data")
    @patch("api.provider.models")
    def test_get_collect_hcs_report_finalization(self, mock_report, rd, provider):
        """Test hcs finalization"""
        from hcs.tasks import collect_hcs_report_finalization

        provider.customer.schema_name.return_value = provider(side_effect=Provider.objects.filter(type="AWS"))

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            collect_hcs_report_finalization()

            self.assertIn("[collect_hcs_report_finalization]:", _logs.output[0])
            self.assertIn("schema_name:", _logs.output[0])
            self.assertIn("provider_type:", _logs.output[0])
            self.assertIn("provider_uuid:", _logs.output[0])
            self.assertIn("dates:", _logs.output[0])

    @patch("hcs.tasks.collect_hcs_report_data")
    @patch("api.provider.models")
    def test_get_collect_hcs_report_finalization_month(self, mock_report, rd, provider):
        """Test hcs finalization for a given month"""
        from hcs.tasks import collect_hcs_report_finalization

        provider.customer.schema_name.return_value = provider(side_effect=Provider.objects.filter(type="AWS"))

        start_date = "2022-10-01"
        end_date = "2022-10-31"

        with self.assertLogs("hcs.tasks", "INFO") as _logs:
            collect_hcs_report_finalization(10)

            self.assertIn("[collect_hcs_report_finalization]:", _logs.output[0])
            self.assertIn("schema_name:", _logs.output[0])
            self.assertIn("provider_type:", _logs.output[0])
            self.assertIn("provider_uuid:", _logs.output[0])
            self.assertIn(f"dates: {start_date} - {end_date}", _logs.output[0])
