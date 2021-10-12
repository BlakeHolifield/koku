#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""Models for OCP on GCP tables."""
from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import JSONField


class OCPGCPCostLineItemDailySummary(models.Model):
    """A summarized view of OCP on GCP cost."""

    class PartitionInfo:
        partition_type = "RANGE"
        partition_cols = ["usage_start"]

    class Meta:
        """Meta for OCPGCPCostLineItemDailySummary."""

        db_table = "reporting_ocpgcpcostlineitem_daily_summary"

        indexes = [
            models.Index(fields=["usage_start"], name="ocpgcp_usage_start_idx"),
            models.Index(fields=["namespace"], name="ocpgcp_namespace_idx"),
            models.Index(fields=["node"], name="ocpgcp_node_idx", opclasses=["varchar_pattern_ops"]),
            models.Index(fields=["resource_id"], name="ocpgcp_resource_idx"),
            GinIndex(fields=["tags"], name="ocpgcp_tags_idx"),
            models.Index(fields=["project_id"], name="ocpgcp_id_idx"),
            models.Index(fields=["project_name"], name="ocpgcp_name_idx"),
            models.Index(fields=["service_id"], name="ocpgcp_service_id_idx"),
            models.Index(fields=["service_alias"], name="ocpgcp_service_alias_idx"),
        ]

    uuid = models.UUIDField(primary_key=True, default=uuid4)

    # OCP Fields
    report_period = models.ForeignKey("OCPUsageReportPeriod", on_delete=models.CASCADE, null=True)

    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = ArrayField(models.CharField(max_length=253, null=False))

    node = models.CharField(max_length=253, null=True)

    resource_id = models.CharField(max_length=253, null=True)

    usage_start = models.DateField(null=False)

    usage_end = models.DateField(null=False)

    # GCP Fields
    cost_entry_bill = models.ForeignKey("GCPCostEntryBill", on_delete=models.CASCADE)

    account_id = models.CharField(max_length=20)

    project_id = models.CharField(max_length=256)

    project_name = models.CharField(max_length=256)

    instance_type = models.CharField(max_length=50, null=True)

    service_id = models.CharField(max_length=256, null=True)

    service_alias = models.CharField(max_length=256, null=True, blank=True)

    region = models.TextField(null=True)

    tags = JSONField(null=True)

    usage_amount = models.DecimalField(max_digits=24, decimal_places=9, null=True)

    # Cost breakdown can be done by cluster, node, project, and pod.
    # Cluster and node cost can be determined by summing the GCP unblended_cost
    # with a GROUP BY cluster/node.
    # Project cost is a summation of pod costs with a GROUP BY project
    # The cost of un-utilized resources = sum(unblended_cost) - sum(project_cost)
    unblended_cost = models.DecimalField(max_digits=24, decimal_places=9, null=True)

    markup_cost = models.DecimalField(max_digits=17, decimal_places=9, null=True)

    currency = models.TextField(null=True)

    unit = models.TextField(null=True)

    # This is a count of the number of projects that share a GCP resource
    # It is used to divide cost evenly among projects
    shared_projects = models.IntegerField(null=False, default=1)

    # A JSON dictionary of the project cost, keyed by project/namespace name
    # See comment on pretax_cost for project cost explanation
    project_costs = JSONField(null=True)

    source_uuid = models.UUIDField(unique=False, null=True)


class OCPGCPCostLineItemProjectDailySummary(models.Model):
    """A summarized view of OCP on GCP cost by OpenShift project."""

    class PartitionInfo:
        partition_type = "RANGE"
        partition_cols = ["usage_start"]

    class Meta:
        """Meta for OCPGCPCostLineItemProjectDailySummary."""

        db_table = "reporting_ocpgcpcostlineitem_project_daily_summary"

        indexes = [
            models.Index(fields=["usage_start"], name="ocpgcp_proj_usage_start_idx"),
            models.Index(fields=["namespace"], name="ocpgcp_proj_namespace_idx"),
            models.Index(fields=["node"], name="ocpgcp_proj_node_idx", opclasses=["varchar_pattern_ops"]),
            models.Index(fields=["resource_id"], name="ocpgcp_proj_resource_idx"),
            GinIndex(fields=["tags"], name="ocpgcp_proj_tags_idx"),
            models.Index(fields=["project_id"], name="ocpgcp_proj_id_idx"),
            models.Index(fields=["project_name"], name="ocpgcp_proj_name_idx"),
            models.Index(fields=["service_id"], name="ocpgcp_proj_service_id_idx"),
            models.Index(fields=["service_alias"], name="ocpgcp_proj_service_alias_idx"),
        ]

    uuid = models.UUIDField(primary_key=True, default=uuid4)

    # OCP Fields
    report_period = models.ForeignKey("OCPUsageReportPeriod", on_delete=models.CASCADE, null=True)

    cluster_id = models.CharField(max_length=50, null=True)

    cluster_alias = models.CharField(max_length=256, null=True)

    # Whether the data comes from a pod or volume report
    data_source = models.CharField(max_length=64, null=True)

    # Kubernetes objects by convention have a max name length of 253 chars
    namespace = models.CharField(max_length=253, null=False)

    node = models.CharField(max_length=253, null=True)

    persistentvolumeclaim = models.CharField(max_length=253, null=True)

    persistentvolume = models.CharField(max_length=253, null=True)

    storageclass = models.CharField(max_length=50, null=True)

    pod_labels = JSONField(null=True)

    resource_id = models.CharField(max_length=253, null=True)

    usage_start = models.DateField(null=False)

    usage_end = models.DateField(null=False)

    # GCP Fields
    cost_entry_bill = models.ForeignKey("GCPCostEntryBill", on_delete=models.CASCADE)

    account_id = models.CharField(max_length=20)

    project_id = models.CharField(max_length=256)

    project_name = models.CharField(max_length=256)

    instance_type = models.CharField(max_length=50, null=True)

    service_id = models.CharField(max_length=256, null=True)

    service_alias = models.CharField(max_length=256, null=True, blank=True)

    sku_id = models.CharField(max_length=256, null=True)

    sku_alias = models.CharField(max_length=256, null=True)

    region = models.TextField(null=True)

    unit = models.CharField(max_length=63, null=True)

    usage_amount = models.DecimalField(max_digits=30, decimal_places=15, null=True)

    currency = models.CharField(max_length=10, null=True)

    invoice_month = models.CharField(max_length=256, null=True, blank=True)

    unblended_cost = models.DecimalField(max_digits=30, decimal_places=15, null=True)

    markup_cost = models.DecimalField(max_digits=30, decimal_places=15, null=True)

    project_markup_cost = models.DecimalField(max_digits=30, decimal_places=15, null=True)

    pod_cost = models.DecimalField(max_digits=30, decimal_places=15, null=True)

    tags = JSONField(null=True)

    source_uuid = models.UUIDField(unique=False, null=True)

    credit_amount = models.DecimalField(max_digits=24, decimal_places=9, null=True, blank=True)


class OCPGCPTagsValues(models.Model):
    class Meta:
        """Meta for OCPGCPTagsValues."""

        db_table = "reporting_ocpgcptags_values"
        unique_together = ("key", "value")
        indexes = [models.Index(fields=["key"], name="ocp_gcp_tags_value_key_idx")]

    uuid = models.UUIDField(primary_key=True, default=uuid4)

    key = models.TextField()
    value = models.TextField()
    account_ids = ArrayField(models.TextField())
    project_ids = ArrayField(models.TextField())
    project_names = ArrayField(models.TextField())
    cluster_ids = ArrayField(models.TextField())
    cluster_aliases = ArrayField(models.TextField())
    namespaces = ArrayField(models.TextField())
    nodes = ArrayField(models.TextField(), null=True)


class OCPGCPTagsSummary(models.Model):
    """A collection of all current existing tag key and values."""

    class Meta:
        """Meta for GCPTagsSummary."""

        db_table = "reporting_ocpgcptags_summary"
        unique_together = (
            "key",
            "cost_entry_bill",
            "account_id",
            "project_id",
            "project_name",
            "report_period",
            "namespace",
            "node",
        )

    uuid = models.UUIDField(primary_key=True, default=uuid4)

    key = models.CharField(max_length=253)
    values = ArrayField(models.TextField())
    cost_entry_bill = models.ForeignKey("GCPCostEntryBill", on_delete=models.CASCADE)
    report_period = models.ForeignKey("OCPUsageReportPeriod", on_delete=models.CASCADE)
    account_id = models.TextField()
    project_id = models.TextField()
    project_name = models.TextField()
    namespace = models.TextField()
    node = models.TextField(null=True)