#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""API views for import organization"""
# flake8: noqa
from api.cloud_accounts.views import cloud_accounts
from api.currency.view import get_currency
from api.dataexport.views import DataExportRequestViewSet
from api.forecast.views import AWSCostForecastView
from api.forecast.views import AzureCostForecastView
from api.forecast.views import GCPForecastCostView
from api.forecast.views import OCPAllCostForecastView
from api.forecast.views import OCPAWSCostForecastView
from api.forecast.views import OCPAzureCostForecastView
from api.forecast.views import OCPCostForecastView
from api.metrics.views import metrics
from api.openapi.view import openapi
from api.organizations.aws.view import AWSOrgView
from api.report.all.openshift.view import OCPAllCostView
from api.report.all.openshift.view import OCPAllInstanceTypeView
from api.report.all.openshift.view import OCPAllStorageView
from api.report.aws.openshift.view import OCPAWSCostView
from api.report.aws.openshift.view import OCPAWSInstanceTypeView
from api.report.aws.openshift.view import OCPAWSStorageView
from api.report.aws.view import AWSCostView
from api.report.aws.view import AWSInstanceTypeView
from api.report.aws.view import AWSStorageView
from api.report.azure.openshift.view import OCPAzureCostView
from api.report.azure.openshift.view import OCPAzureInstanceTypeView
from api.report.azure.openshift.view import OCPAzureStorageView
from api.report.azure.view import AzureCostView
from api.report.azure.view import AzureInstanceTypeView
from api.report.azure.view import AzureStorageView
from api.report.gcp.view import GCPCostView
from api.report.gcp.view import GCPInstanceTypeView
from api.report.gcp.view import GCPStorageView
from api.report.ocp.view import OCPCostView
from api.report.ocp.view import OCPCpuView
from api.report.ocp.view import OCPMemoryView
from api.report.ocp.view import OCPVolumeView
from api.resource_types.aws_accounts.view import AWSAccountView
from api.resource_types.aws_org_unit.view import AWSOrganizationalUnitView
from api.resource_types.aws_regions.view import AWSAccountRegionView
from api.resource_types.aws_services.view import AWSServiceView
from api.resource_types.azure_subscription_guid.view import AzureSubscriptionGuidView
from api.resource_types.cost_models.view import CostModelResourceTypesView
from api.resource_types.gcp_accounts.view import GCPAccountView
from api.resource_types.gcp_projects.view import GCPProjectsView
from api.resource_types.openshift_clusters.view import OCPClustersView
from api.resource_types.openshift_nodes.view import OCPNodesView
from api.resource_types.openshift_projects.view import OCPProjectsView
from api.resource_types.view import ResourceTypeView
from api.settings.view import SettingsView
from api.status.views import StatusView
from api.tags.all.openshift.view import OCPAllTagView
from api.tags.aws.openshift.view import OCPAWSTagView
from api.tags.aws.view import AWSTagView
from api.tags.azure.openshift.view import OCPAzureTagView
from api.tags.azure.view import AzureTagView
from api.tags.gcp.view import GCPTagView
from api.tags.ocp.view import OCPTagView
from api.user_access.view import UserAccessView
