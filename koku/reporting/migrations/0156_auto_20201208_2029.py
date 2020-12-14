# Generated by Django 3.1.3 on 2020-12-08 20:29
import pkgutil
import uuid

from django.db import connection
from django.db import migrations
from django.db import models


def add_views(apps, schema_editor):
    """Create database VIEWS from files."""
    views = (
        "reporting_ocp_pod_summary",
        "reporting_ocp_pod_summary_by_project",
        "reporting_ocp_volume_summary",
        "reporting_ocp_volume_summary_by_project",
    )
    for view in views:
        view_sql = pkgutil.get_data("reporting.provider.ocp", f"sql/views/{view}.sql")
        view_sql = view_sql.decode("utf-8")
        with connection.cursor() as cursor:
            cursor.execute(view_sql)


class Migration(migrations.Migration):

    dependencies = [("reporting", "0155_gcp_partitioned")]

    operations = [
        migrations.RemoveField(model_name="ocpawscostlineitemdailysummary", name="id"),
        migrations.RemoveField(model_name="ocpawscostlineitemdailysummary", name="pod"),
        migrations.RemoveField(model_name="ocpawscostlineitemprojectdailysummary", name="id"),
        migrations.RemoveField(model_name="ocpawscostlineitemprojectdailysummary", name="pod"),
        migrations.RemoveField(model_name="ocpazurecostlineitemdailysummary", name="id"),
        migrations.RemoveField(model_name="ocpazurecostlineitemprojectdailysummary", name="id"),
        migrations.AddField(
            model_name="ocpawscostlineitemdailysummary",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.AddField(
            model_name="ocpawscostlineitemprojectdailysummary",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.AddField(
            model_name="ocpazurecostlineitemdailysummary",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.AddField(
            model_name="ocpazurecostlineitemprojectdailysummary",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.RunSQL(
            """
            DROP RULE IF EXISTS ins_reporting_ocpusagelineitem_daily_summary_presto ON reporting_ocpusagelineitem_daily_summary_presto;
            DROP VIEW IF EXISTS reporting_ocpusagelineitem_daily_summary_presto;
            DROP MATERIALIZED VIEW IF EXISTS reporting_ocp_pod_summary;
            DROP MATERIALIZED VIEW IF EXISTS reporting_ocp_pod_summary_by_project;
            DROP MATERIALIZED VIEW IF EXISTS reporting_ocp_volume_summary;
            DROP MATERIALIZED VIEW IF EXISTS reporting_ocp_volume_summary_by_project;

            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN pod_usage_cpu_core_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN pod_request_cpu_core_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN pod_limit_cpu_core_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN pod_usage_memory_gigabyte_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN pod_request_memory_gigabyte_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN pod_limit_memory_gigabyte_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN node_capacity_cpu_cores TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN node_capacity_cpu_core_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN node_capacity_memory_gigabytes TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN node_capacity_memory_gigabyte_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN cluster_capacity_cpu_core_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN cluster_capacity_memory_gigabyte_hours TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN persistentvolumeclaim_capacity_gigabyte TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN persistentvolumeclaim_capacity_gigabyte_months TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN volume_request_storage_gigabyte_months TYPE numeric(18,6);
            ALTER TABLE reporting_ocpusagelineitem_daily_summary ALTER COLUMN persistentvolumeclaim_usage_gigabyte_months TYPE numeric(18,6);
            """
        ),
        migrations.RunPython(add_views),
    ]
