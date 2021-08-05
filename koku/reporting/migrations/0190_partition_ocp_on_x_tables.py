#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
# Generated by Django 3.1.10 on 2021-05-17 19:48
import logging
import pkgutil

from django.db import migrations


LOG = logging.getLogger(__name__)


CACHE = {}


def check_partitioned(apps, schema_editor):
    conn = schema_editor.connection
    sql = """
SELECT c.relname::text,
       (c.relkind = 'p')::boolean as "is_partitioned"
  FROM pg_class c
  JOIN pg_namespace n
    ON n.oid = c.relnamespace
 WHERE n.nspname = current_schema
   AND c.relname = any(array['reporting_ocpawscostlineitem_daily_summary',
                             'reporting_ocpawscostlineitem_project_daily_summary',
                             'reporting_ocpazurecostlineitem_daily_summary',
                             'reporting_ocpazurecostlineitem_project_daily_summary']::text[]) ;
"""
    with conn.cursor() as cur:
        cur.execute(sql)
        for rec in cur.fetchall():
            CACHE[rec[0]] = rec[1]


def execute_sql_stmts(conn, sql_stmts):
    for stmts in sql_stmts:
        LOG.info(stmts.pop(0))
        for stmt in stmts:
            with conn.cursor() as cur:
                cur.execute(stmt)


def create_ocpaws_partitioned_table(apps, schema_editor):
    connection = schema_editor.connection
    if CACHE.get("reporting_ocpawscostlineitem_daily_summary"):
        LOG.warning("TABLE reporting_ocpawscostlineitem_daily_summary IS PARTITIONED. SKIP CREATE")
        return

    sql_stmts = [
        [
            "Creating partitioned table p_reporting_ocpawscostlineitem_daily_summary",
            """
CREATE TABLE p_reporting_ocpawscostlineitem_daily_summary
(
    LIKE reporting_ocpawscostlineitem_daily_summary
    INCLUDING DEFAULTS
    INCLUDING GENERATED
    INCLUDING IDENTITY
    INCLUDING STATISTICS
)
PARTITION BY RANGE (usage_start);
""",
        ],
        [
            """Creating constraints on p_reporting_ocpawscostlineitem_daily_summary""",
            """
ALTER TABLE p_reporting_ocpawscostlineitem_daily_summary
  ADD CONSTRAINT "ocpawscostlineitem_daily_summary_pk" PRIMARY KEY (usage_start, uuid),
  ADD CONSTRAINT "ocpawscost_account_alias_id_f19d2883_fk_reporting"
      FOREIGN KEY (account_alias_id) REFERENCES reporting_awsaccountalias (id)
                  DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "ocpawscost_cost_entry_bill_id_2a473151_fk_reporting"
      FOREIGN KEY (cost_entry_bill_id) REFERENCES reporting_awscostentrybill (id)
                  DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "ocpawscost_report_period_id_150c5620_fk_reporting"
      FOREIGN KEY (report_period_id) REFERENCES reporting_ocpusagereportperiod (id)
                  DEFERRABLE INITIALLY DEFERRED;
""",
        ],
        [
            "Creating indexes on p_reporting_ocpawscostlineitem_daily_summary",
            """CREATE INDEX "ocpawscostlineitem_daily_summa_cost_entry_bill_id_idx" ON p_reporting_ocpawscostlineitem_daily_summary (cost_entry_bill_id);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_account_alias_id_idx" ON p_reporting_ocpawscostlineitem_daily_summary (account_alias_id);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_instance_type_idx" ON p_reporting_ocpawscostlineitem_daily_summary (instance_type);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_namespace_idx" ON p_reporting_ocpawscostlineitem_daily_summary (namespace);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_node_idx" ON p_reporting_ocpawscostlineitem_daily_summary (node varchar_pattern_ops);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_product_family_idx" ON p_reporting_ocpawscostlineitem_daily_summary (product_family);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_report_period_id_idx" ON p_reporting_ocpawscostlineitem_daily_summary (report_period_id);"""
            """CREATE INDEX "ocpawscostlineitem_daily_summary_resource_id_idx" ON p_reporting_ocpawscostlineitem_daily_summary (resource_id);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_tags_idx" ON p_reporting_ocpawscostlineitem_daily_summary USING gin (tags);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_upper_idx" ON p_reporting_ocpawscostlineitem_daily_summary USING gin (upper(node::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_upper_idx1" ON p_reporting_ocpawscostlineitem_daily_summary USING gin (upper(product_family::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_upper_idx2" ON p_reporting_ocpawscostlineitem_daily_summary USING gin (upper(product_code::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpawscostlineitem_daily_summary_usage_start_idx" ON p_reporting_ocpawscostlineitem_daily_summary (usage_start);""",
        ],
        [
            "Creating default partitioin for p_reporting_ocpawscostlineitem_daily_summary",
            """
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
VALUES (
           current_schema,
           'reporting_ocpawscostlineitem_daily_default',
           'p_reporting_ocpawscostlineitem_daily_summary',
           'range',
           'usage_start',
           '{"default": true}'::jsonb,
           true
       )
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
        [
            "Creating needed monthly partitions for p_reporting_ocpawscostlineitem_daily_summary",
            r"""
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
WITH partition_start_values as (
SELECT DISTINCT
       to_char(usage_start, 'YYYY-MM-01') as usage_start
  FROM reporting_ocpawscostlineitem_daily_summary
)
SELECT current_schema,
       format(
           'reporting_ocpawscostlineitem_daily_summary_%s',
           regexp_replace(usage_start, '(\d{4}).(\d{2}).*', '\1_\2')
       )::text,
       'p_reporting_ocpawscostlineitem_daily_summary',
       'range',
       'usage_start',
       format(
           '{"default": false, "from": %I, "to": %I}',
           usage_start,
           to_char((usage_start::date + '1 month'::interval), 'YYYY-MM-01')
       )::jsonb,
       true
  FROM partition_start_values
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
    ]

    execute_sql_stmts(connection, sql_stmts)


def create_ocpaws_project_partitioned_table(apps, schema_editor):
    connection = schema_editor.connection
    if CACHE.get("reporting_ocpawscostlineitem_project_daily_summary"):
        LOG.warning("TABLE reporting_ocpawscostlineitem_project_daily_summary IS PARTITIONED. SKIP CREATE")
        return

    sql_stmts = [
        [
            "Creating partitioned table p_reporting_ocpawscostlineitem_project_daily_summary",
            """
CREATE TABLE p_reporting_ocpawscostlineitem_project_daily_summary
(
    LIKE reporting_ocpawscostlineitem_project_daily_summary
    INCLUDING DEFAULTS
    INCLUDING GENERATED
    INCLUDING IDENTITY
    INCLUDING STATISTICS
)
PARTITION BY RANGE (usage_start);
""",
        ],
        [
            "Creating constraints on p_reporting_ocpawscostlineitem_project_daily_summary",
            """
ALTER TABLE p_reporting_ocpawscostlineitem_project_daily_summary
  ADD CONSTRAINT "ocpawscostlineitem_project_daily_summary_pk" PRIMARY KEY (usage_start, uuid),
  ADD CONSTRAINT "ocpawscost_project_account_alias_id_f19d2883_fk_reporting"
      FOREIGN KEY (account_alias_id) REFERENCES reporting_awsaccountalias (id)
                  DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "ocpawscost_projectcost_entry_bill_id_2a473151_fk_reporting"
      FOREIGN KEY (cost_entry_bill_id) REFERENCES reporting_awscostentrybill (id)
                  DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "ocpawscost_projecct_report_period_id_150c5620_fk_reporting"
      FOREIGN KEY (report_period_id) REFERENCES reporting_ocpusagereportperiod (id)
                  DEFERRABLE INITIALLY DEFERRED;
""",
        ],
        [
            "Creating indexes on p_reporting_ocpawscostlineitem_project_daily_summary",
            """CREATE INDEX "ocpawscostlineitem_project_dai_cost_entry_bill_id_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (cost_entry_bill_id);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_account_alias_id_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (account_alias_id);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_report_period_id_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (report_period_id);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_s_product_family_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (product_family);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_su_instance_type_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (instance_type);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summ_resource_id_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (resource_id);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summ_usage_start_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (usage_start);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summa_pod_labels_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary USING gin (pod_labels);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summar_namespace_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (namespace varchar_pattern_ops);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summary_node_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary (node varchar_pattern_ops);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summary_upper_idx" ON p_reporting_ocpawscostlineitem_project_daily_summary USING gin (upper(namespace::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpawscostlineitem_project_daily_summary_upper_idx1" ON p_reporting_ocpawscostlineitem_project_daily_summary USING gin (upper(node::text) gin_trgm_ops);""",
        ],
        [
            "Creating default partition for p_reporting_ocpawscostlineitem_project_daily_summary",
            """
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
VALUES (
           current_schema,
           'reporting_ocpawscostlineitem_project_daily_summary_default',
           'p_reporting_ocpawscostlineitem_project_daily_summary',
           'range',
           'usage_start',
           '{"default": true}'::jsonb,
           true
       )
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
        [
            "Creating needed monthly partitions for p_reporting_ocpawscostlineitem_project_daily_summary",
            r"""
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
WITH partition_start_values as (
SELECT DISTINCT
       to_char(usage_start, 'YYYY-MM-01') as usage_start
  FROM reporting_ocpawscostlineitem_project_daily_summary
)
SELECT current_schema,
       format(
           'reporting_ocpawscostlineitem_project_daily_summary_%s',
           regexp_replace(usage_start, '(\d{4}).(\d{2}).*', '\1_\2')
       )::text,
       'p_reporting_ocpawscostlineitem_project_daily_summary',
       'range',
       'usage_start',
       format(
           '{"default": false, "from": %I, "to": %I}',
           usage_start,
           to_char((usage_start::date + '1 month'::interval), 'YYYY-MM-01')
       )::jsonb,
       true
  FROM partition_start_values
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
    ]

    execute_sql_stmts(connection, sql_stmts)


def create_ocpazure_partitioned_table(apps, schema_editor):
    connection = schema_editor.connection
    if CACHE.get("reporting_ocpazurecostlineitem_daily_summary"):
        LOG.warning("TABLE reporting_ocpazurecostlineitem_daily_summary IS PARTITIONED. SKIP CREATE")
        return

    sql_stmts = [
        [
            "Creating partitioned table p_reporting_ocpazurecostlineitem_daily_summary",
            """
CREATE TABLE p_reporting_ocpazurecostlineitem_daily_summary
(
    LIKE reporting_ocpazurecostlineitem_daily_summary
    INCLUDING DEFAULTS
    INCLUDING GENERATED
    INCLUDING IDENTITY
    INCLUDING STATISTICS
)
PARTITION BY RANGE (usage_start);
""",
        ],
        [
            "Creating constraints on p_reporting_ocpazurecostlineitem_daily_summary",
            """
ALTER TABLE p_reporting_ocpazurecostlineitem_daily_summary
  ADD CONSTRAINT "ocpazurecostlineitem_daily_summary_pk" PRIMARY KEY (usage_start, uuid),
  ADD CONSTRAINT "ocpazureco_cost_entry_bill_id_b12d05bd_fk_reporting"
      FOREIGN KEY (cost_entry_bill_id) REFERENCES reporting_azurecostentrybill (id)
                  DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "ocpazureco_report_period_id_e5bbf81f_fk_reporting"
      FOREIGN KEY (report_period_id) REFERENCES reporting_ocpusagereportperiod (id)
                  DEFERRABLE INITIALLY DEFERRED;
""",
        ],
        [
            "Creating indexes on p_reporting_ocpazurecostlineitem_daily_summary",
            """CREATE INDEX "ocpazurecostlineitem_daily_sum_cost_entry_bill_id_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (cost_entry_bill_id);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summa_report_period_id_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (report_period_id);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_instance_type_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (instance_type);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_namespace_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (namespace);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_node_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (node varchar_pattern_ops);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_resource_id_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (resource_id);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_service_name_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (service_name);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_tags_idx" ON p_reporting_ocpazurecostlineitem_daily_summary USING gin (tags);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_upper_idx" ON p_reporting_ocpazurecostlineitem_daily_summary USING gin (upper(node::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_upper_idx1" ON p_reporting_ocpazurecostlineitem_daily_summary USING gin (upper(service_name::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpazurecostlineitem_daily_summary_usage_start_idx" ON p_reporting_ocpazurecostlineitem_daily_summary (usage_start);""",
        ],
        [
            "Creating default partition for p_reporting_ocpazurecostlineitem_daily_summary",
            """
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
VALUES (
           current_schema,
           'reporting_ocpazurecostlineitem_daily_default',
           'p_reporting_ocpazurecostlineitem_daily_summary',
           'range',
           'usage_start',
           '{"default": true}'::jsonb,
           true
       )
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
        [
            "Creating needed monthly partitions for p_reporting_ocpazurecostlineitem_daily_summary",
            r"""
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
WITH partition_start_values as (
SELECT DISTINCT
       to_char(usage_start, 'YYYY-MM-01') as usage_start
  FROM reporting_ocpazurecostlineitem_daily_summary
)
SELECT current_schema,
       format(
           'reporting_ocpazurecostlineitem_daily_summary_%s',
           regexp_replace(usage_start, '(\d{4}).(\d{2}).*', '\1_\2')
       )::text,
       'p_reporting_ocpazurecostlineitem_daily_summary',
       'range',
       'usage_start',
       format(
           '{"default": false, "from": %I, "to": %I}',
           usage_start,
           to_char((usage_start::date + '1 month'::interval), 'YYYY-MM-01')
       )::jsonb,
       true
  FROM partition_start_values
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
    ]

    execute_sql_stmts(connection, sql_stmts)


def create_ocpazure_project_partitioned_table(apps, schema_editor):
    connection = schema_editor.connection
    if CACHE.get("reporting_ocpazurecostlineitem_project_daily_summary"):
        LOG.warning("TABLE reporting_ocpazurecostlineitem_project_daily_summary IS PARTITIONED. SKIP CREATE")
        return

    sql_stmts = [
        [
            "Creating partitioned table p_reporting_ocpazure_costlineitem_project_daily_summary",
            """
CREATE TABLE p_reporting_ocpazurecostlineitem_project_daily_summary
(
    LIKE reporting_ocpazurecostlineitem_project_daily_summary
    INCLUDING DEFAULTS
    INCLUDING GENERATED
    INCLUDING IDENTITY
    INCLUDING STATISTICS
)
PARTITION BY RANGE (usage_start);
""",
        ],
        [
            "Creating constraints on p_reporting_ocpazurecostlineitem_project_daily_summary",
            """
ALTER TABLE p_reporting_ocpazurecostlineitem_project_daily_summary
  ADD CONSTRAINT "ocpazurecostlineitem_project_daily_summary_pk" PRIMARY KEY (usage_start, uuid),
  ADD CONSTRAINT "ocpazurecost_projectcost_entry_bill_id_2a473151_fk_reporting"
      FOREIGN KEY (cost_entry_bill_id) REFERENCES reporting_azurecostentrybill (id)
                  DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "ocpazurecost_projecct_report_period_id_150c5620_fk_reporting"
      FOREIGN KEY (report_period_id) REFERENCES reporting_ocpusagereportperiod (id)
                  DEFERRABLE INITIALLY DEFERRED;
""",
        ],
        [
            "Creating indexes on p_reporting_ocpazurecostlineitem_project_daily_summary",
            """CREATE INDEX "ocpazurecostlineitem_project_d_cost_entry_bill_id_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (cost_entry_bill_id);""",
            """CREATE INDEX "ocpazurecostlineitem_project_dai_report_period_id_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (report_period_id);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily__instance_type_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (instance_type);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_s_service_name_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (service_name);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_su_resource_id_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (resource_id);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_su_usage_start_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (usage_start);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_sum_pod_labels_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary USING gin (pod_labels);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_summ_namespace_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (namespace varchar_pattern_ops);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_summary_node_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary (node varchar_pattern_ops);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_summary_upper_idx" ON p_reporting_ocpazurecostlineitem_project_daily_summary USING gin (upper(namespace::text) gin_trgm_ops);""",
            """CREATE INDEX "ocpazurecostlineitem_project_daily_summary_upper_idx1" ON p_reporting_ocpazurecostlineitem_project_daily_summary USING gin (upper(node::text) gin_trgm_ops);""",
        ],
        [
            "Creating default partition for p_reporting_ocpazurecostlineitem_project_daily_summary",
            """
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
VALUES (
           current_schema,
           'reporting_ocpazurecostlineitem_project_daily_summary_default',
           'p_reporting_ocpazurecostlineitem_project_daily_summary',
           'range',
           'usage_start',
           '{"default": true}'::jsonb,
           true
       )
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
        [
            "Creating needed monthly partitions for p_reporting_ocpazurecostlineitem_project_daily_summary",
            r"""
INSERT
  INTO partitioned_tables
       (
           schema_name,
           table_name,
           partition_of_table_name,
           partition_type,
           partition_col,
           partition_parameters,
           active
       )
WITH partition_start_values as (
SELECT DISTINCT
       to_char(usage_start, 'YYYY-MM-01') as usage_start
  FROM reporting_ocpazurecostlineitem_project_daily_summary
)
SELECT current_schema,
       format(
           'reporting_ocpazurecostlineitem_project_daily_summary_%s',
           regexp_replace(usage_start, '(\d{4}).(\d{2}).*', '\1_\2')
       )::text,
       'p_reporting_ocpazurecostlineitem_project_daily_summary',
       'range',
       'usage_start',
       format(
           '{"default": false, "from": %I, "to": %I}',
           usage_start,
           to_char((usage_start::date + '1 month'::interval), 'YYYY-MM-01')
       )::jsonb,
       true
  FROM partition_start_values
    ON CONFLICT (schema_name, table_name)
       DO NOTHING;
""",
        ],
    ]

    execute_sql_stmts(connection, sql_stmts)


class Migration(migrations.Migration):

    dependencies = [("reporting", "0189_auto_20210803_2056")]

    operations = [
        migrations.AlterModelOptions(name="ocpawscostlineitemdailysummary", options={"managed": False}),
        migrations.AlterModelOptions(name="ocpawscostlineitemprojectdailysummary", options={"managed": False}),
        migrations.AlterModelOptions(name="ocpazurecostlineitemdailysummary", options={"managed": False}),
        migrations.AlterModelOptions(name="ocpazurecostlineitemprojectdailysummary", options={"managed": False}),
        migrations.RunPython(code=check_partitioned),
        migrations.RunPython(code=create_ocpaws_partitioned_table),
        migrations.RunPython(code=create_ocpaws_project_partitioned_table),
        migrations.RunPython(code=create_ocpazure_partitioned_table),
        migrations.RunPython(code=create_ocpazure_project_partitioned_table),
    ]
