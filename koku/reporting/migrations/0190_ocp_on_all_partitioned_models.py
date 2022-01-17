# Generated by Django 3.1.13 on 2021-08-18 21:09
import pkgutil

import django.contrib.postgres.fields
import django.contrib.postgres.indexes
import django.db.models.deletion
from django.db import migrations
from django.db import models

from koku.database import set_pg_extended_mode
from koku.database import unset_pg_extended_mode


def create_new_ocpall_matviews(apps, schema_editor):
    pass


def drop_new_ocpall_matviews(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("reporting", "0001_initial-from-template")]

    operations = [
        migrations.RunPython(code=set_pg_extended_mode, reverse_code=unset_pg_extended_mode),
        migrations.CreateModel(
            name="OCPAllCostLineItemProjectDailySummaryP",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("source_type", models.TextField()),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("data_source", models.CharField(max_length=64, null=True)),
                ("namespace", models.CharField(max_length=253)),
                ("node", models.CharField(max_length=253, null=True)),
                ("pod_labels", models.JSONField(null=True)),
                ("resource_id", models.CharField(max_length=253, null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("usage_account_id", models.CharField(max_length=50)),
                ("product_code", models.CharField(max_length=50)),
                ("product_family", models.CharField(max_length=150, null=True)),
                ("instance_type", models.CharField(max_length=50, null=True)),
                ("region", models.CharField(max_length=50, null=True)),
                ("availability_zone", models.CharField(max_length=50, null=True)),
                ("usage_amount", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("unit", models.CharField(max_length=63, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("project_markup_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("pod_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("currency_code", models.CharField(max_length=10, null=True)),
                ("source_uuid", models.UUIDField(null=True)),
                (
                    "account_alias",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to="reporting.awsaccountalias"
                    ),
                ),
            ],
            options={"db_table": "reporting_ocpallcostlineitem_project_daily_summary_p"},
        ),
        migrations.RunSQL(
            """
ALTER TABLE reporting_ocpallcostlineitem_project_daily_summary_p
      ALTER COLUMN "id" SET DEFAULT uuid_generate_v4();
"""
        ),
        migrations.CreateModel(
            name="OCPAllCostLineItemDailySummaryP",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("source_type", models.TextField()),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                (
                    "namespace",
                    django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=253), size=None),
                ),
                ("node", models.CharField(max_length=253, null=True)),
                ("resource_id", models.CharField(max_length=253, null=True)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("usage_account_id", models.CharField(max_length=50)),
                ("product_code", models.CharField(max_length=50)),
                ("product_family", models.CharField(max_length=150, null=True)),
                ("instance_type", models.CharField(max_length=50, null=True)),
                ("region", models.CharField(max_length=50, null=True)),
                ("availability_zone", models.CharField(max_length=50, null=True)),
                ("tags", models.JSONField(null=True)),
                ("usage_amount", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("unit", models.CharField(max_length=63, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("currency_code", models.CharField(max_length=10, null=True)),
                ("shared_projects", models.IntegerField(default=1)),
                ("source_uuid", models.UUIDField(null=True)),
                (
                    "account_alias",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to="reporting.awsaccountalias"
                    ),
                ),
            ],
            options={"db_table": "reporting_ocpallcostlineitem_daily_summary_p"},
        ),
        migrations.RunSQL(
            """
ALTER TABLE reporting_ocpallcostlineitem_daily_summary_p
      ALTER COLUMN "id" SET DEFAULT uuid_generate_v4();
"""
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=models.Index(fields=["usage_start"], name="ocpallp_p_proj_usage_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=models.Index(fields=["namespace"], name="ocpallp_p_proj_namespace_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=models.Index(fields=["node"], name="ocpallp_p_proj_node_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=models.Index(fields=["resource_id"], name="ocpallp_p_proj_resource_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["pod_labels"], name="ocpallp_p_proj_pod_labels_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=models.Index(fields=["product_family"], name="ocpallp_p_proj_prod_fam_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemprojectdailysummaryp",
            index=models.Index(fields=["instance_type"], name="ocpallp_p_proj_inst_type_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=models.Index(fields=["usage_start"], name="ocpall_p_usage_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=models.Index(fields=["namespace"], name="ocpall_p_namespace_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=models.Index(fields=["node"], name="ocpall_p_node_idx", opclasses=["varchar_pattern_ops"]),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=models.Index(fields=["resource_id"], name="ocpall_p_resource_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=django.contrib.postgres.indexes.GinIndex(fields=["tags"], name="ocpall_p_tags_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=models.Index(fields=["product_family"], name="ocpall_p_product_family_idx"),
        ),
        migrations.AddIndex(
            model_name="ocpallcostlineitemdailysummaryp",
            index=models.Index(fields=["instance_type"], name="ocpall_p_instance_type_idx"),
        ),
        migrations.RunPython(code=unset_pg_extended_mode, reverse_code=set_pg_extended_mode),
        migrations.RunPython(code=create_new_ocpall_matviews, reverse_code=drop_new_ocpall_matviews),
        migrations.CreateModel(
            name="OCPAllComputeSummaryP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("product_code", models.CharField(max_length=50)),
                ("instance_type", models.CharField(max_length=50)),
                ("resource_id", models.CharField(max_length=253)),
                ("usage_amount", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("unit", models.CharField(max_length=63, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("currency_code", models.CharField(max_length=10, null=True)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_compute_summary_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllCostSummaryByAccountP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("unblended_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("currency_code", models.CharField(max_length=10)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_cost_summary_by_account_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllCostSummaryByRegionP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("region", models.CharField(max_length=50, null=True)),
                ("availability_zone", models.CharField(max_length=50, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("currency_code", models.CharField(max_length=10)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_cost_summary_by_region_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllCostSummaryByServiceP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("product_code", models.CharField(max_length=50)),
                ("product_family", models.CharField(max_length=150, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("currency_code", models.CharField(max_length=10)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_cost_summary_by_service_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllCostSummaryP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=9, max_digits=24, null=True)),
                ("currency_code", models.CharField(max_length=10)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_cost_summary_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllDatabaseSummaryP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("product_code", models.CharField(max_length=50)),
                ("usage_amount", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("unit", models.CharField(max_length=63, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("currency_code", models.CharField(max_length=10, null=True)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_database_summary_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllNetworkSummaryP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("product_code", models.CharField(max_length=50)),
                ("usage_amount", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("unit", models.CharField(max_length=63, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("currency_code", models.CharField(max_length=10, null=True)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_network_summary_p", "managed": False},
        ),
        migrations.CreateModel(
            name="OCPAllStorageSummaryP",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("cluster_id", models.CharField(max_length=50, null=True)),
                ("cluster_alias", models.CharField(max_length=256, null=True)),
                ("usage_account_id", models.CharField(max_length=50)),
                ("usage_start", models.DateField()),
                ("usage_end", models.DateField()),
                ("product_family", models.CharField(max_length=150, null=True)),
                ("product_code", models.CharField(max_length=50)),
                ("usage_amount", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("unit", models.CharField(max_length=63, null=True)),
                ("unblended_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("markup_cost", models.DecimalField(decimal_places=15, max_digits=30, null=True)),
                ("currency_code", models.CharField(max_length=10, null=True)),
                ("source_uuid", models.UUIDField(null=True)),
            ],
            options={"db_table": "reporting_ocpall_storage_summary_p", "managed": False},
        ),
    ]
