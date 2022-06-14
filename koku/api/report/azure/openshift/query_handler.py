#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""OCP Query Handling for Reports."""
import copy
import logging
from collections import defaultdict
from decimal import Decimal

import pandas as pd
from django.db.models import F
from tenant_schemas.utils import tenant_context

from api.models import Provider
from api.report.azure.openshift.provider_map import OCPAzureProviderMap
from api.report.azure.query_handler import AzureReportQueryHandler
from api.report.queries import check_if_valid_date_str
from api.report.queries import is_grouped_by_project

LOG = logging.getLogger(__name__)


class OCPAzureReportQueryHandler(AzureReportQueryHandler):
    """Handles report queries and responses for OCP on Azure."""

    provider = Provider.OCP_AZURE

    def __init__(self, parameters):
        """Establish OCP report query handler.

        Args:
            parameters    (QueryParameters): parameter object for query

        """
        self._mapper = OCPAzureProviderMap(provider=self.provider, report_type=parameters.report_type)
        # Update which field is used to calculate cost by group by param.
        if is_grouped_by_project(parameters):
            self._report_type = parameters.report_type + "_by_project"
            self._mapper = OCPAzureProviderMap(provider=self.provider, report_type=self._report_type)

        self.group_by_options = self._mapper.provider_map.get("group_by_options")
        self._limit = parameters.get_filter("limit")

        # super() needs to be called after _mapper and _limit is set
        super().__init__(parameters)
        # super() needs to be called before _get_group_by is called

    @property
    def annotations(self):
        """Create dictionary for query annotations.

        Returns:
            (Dict): query annotations dictionary

        """
        annotations = {"date": self.date_trunc("usage_start")}
        # { query_param: database_field_name }
        fields = self._mapper.provider_map.get("annotations")
        for q_param, db_field in fields.items():
            annotations[q_param] = F(db_field)
        if (
            "project" in self.parameters.parameters.get("group_by", {})
            or "and:project" in self.parameters.parameters.get("group_by", {})
            or "or:project" in self.parameters.parameters.get("group_by", {})
        ):
            annotations["project"] = F("namespace")

        return annotations

    def execute_query(self):  # noqa: C901
        """Execute query and return provided data.

        Returns:
            (Dict): Dictionary response of query params, data, and total

        """
        query_sum = self.initialize_totals()
        data = []

        with tenant_context(self.tenant):
            query = self.query_table.objects.filter(self.query_filter)
            query_data = query.annotate(**self.annotations)
            group_by_value = self._get_group_by()
            query_group_by = ["date"] + group_by_value
            query_order_by = ["-date"]
            initial_group_by = query_group_by + [self._mapper.cost_units_key]
            query_order_by.extend(self.order)  # add implicit ordering
            annotations = self._mapper.report_type_map.get("annotations")
            query_data = query_data.values(*initial_group_by).annotate(**annotations)
            aggregates = self._mapper.report_type_map.get("aggregates")
            query_sum_data = query_data.annotate(**aggregates)
            if query_data:
                df = pd.DataFrame(query_data)
                aggregates = self._mapper.report_type_map.get("aggregates")
                columns = list(aggregates.keys())
                if "cost_units" in columns:
                    columns.remove("cost_units")
                if "usage_units" in columns:
                    columns.remove("usage_units")
                exchange_rates = {
                    "USD": {"USD": Decimal(1.0)},
                    "EUR": {
                        "USD": Decimal(1.0718113612004287471535235454211942851543426513671875),
                        "CAD": Decimal(1.25),
                    },
                    "GBP": {
                        "USD": Decimal(1.25470514429109147869212392834015190601348876953125),
                        "CAD": Decimal(1.34),
                    },
                    "JPY": {
                        "USD": Decimal(0.007456565505927968857957655046675427001900970935821533203125),
                        "CAD": Decimal(1.34),
                    },
                }
                for column in columns:
                    df[column] = df.apply(
                        lambda row: row[column] * exchange_rates[row[self._mapper.cost_units_key]][self.currency],
                        axis=1,
                    )
                    df["cost_units"] = self.currency
                skip_columns = ["gcp_project_alias", "clusters"]
                if "count" not in df.columns:
                    skip_columns.extend(["count", "count_units"])
                aggs = {
                    col: ["max"] if "units" in col else ["sum"]
                    for col in self.report_annotations
                    if col not in skip_columns
                }

                grouped_df = df.groupby(query_group_by).agg(aggs, axis=1)
                columns = grouped_df.columns.droplevel(1)
                grouped_df.columns = columns
                grouped_df.reset_index(inplace=True)
                query_data = grouped_df.to_dict("records")

            if self._limit and query_data:
                query_data = self._group_by_ranks(query, query_data)
                if not self.parameters.get("order_by"):
                    # override implicit ordering when using ranked ordering.
                    query_order_by[-1] = "rank"

            if query.exists():
                # aggregates = self._mapper.report_type_map.get("aggregates")
                # query_sum_data = query_data.annotate(**aggregates)
                # pandas stuff?
                aggregates = self._mapper.report_type_map.get("aggregates")
                columns = list(aggregates.keys())
                if "usage" in columns:
                    columns.remove("usage")
                if "cost_units" in columns:
                    columns.remove("cost_units")
                if "usage_units" in columns:
                    columns.remove("usage_units")
                df = pd.DataFrame(query_sum_data)
                exchange_rates = {
                    "USD": {"USD": Decimal(1.0)},
                    "EUR": {
                        "USD": Decimal(1.0718113612004287471535235454211942851543426513671875),
                        "CAD": Decimal(1.25),
                    },
                    "GBP": {
                        "USD": Decimal(1.25470514429109147869212392834015190601348876953125),
                        "CAD": Decimal(1.34),
                    },
                    "JPY": {
                        "USD": Decimal(0.007456565505927968857957655046675427001900970935821533203125),
                        "CAD": Decimal(1.34),
                    },
                }
                for column in columns:
                    df[column] = df.apply(
                        lambda row: row[column] * exchange_rates[row[self._mapper.cost_units_key]][self.currency],
                        axis=1,
                    )
                    df["cost_units"] = self.currency
                skip_columns = [
                    "source_uuid",
                    "gcp_project_alias",
                    "clusters",
                    "usage_units",
                    "count_units",
                    "cost_units",
                ]
                if "count" not in df.columns:
                    skip_columns.extend(["count", "count_units"])
                aggs = {
                    col: ["max"] if "units" in col else ["sum"]
                    for col in self.report_annotations
                    if col not in skip_columns
                }
                grouped_df = df.groupby(["currency"]).agg(aggs, axis=1)
                columns = grouped_df.columns.droplevel(1)
                grouped_df.columns = columns
                grouped_df.reset_index(inplace=True)
                total_query = grouped_df.to_dict("records")
                dct = defaultdict(Decimal)

                for element in total_query:
                    for key, value in element.items():
                        if type(value) != str:
                            dct[key] += value
                        else:
                            dct[key] = value
                dct.pop("currency")
                query_sum = dct
                # metric_sum = query.aggregate(**aggregates)
                # query_sum = {key: metric_sum.get(key) for key in aggregates}

            if self._delta:
                query_data = self.add_deltas(query_data, query_sum)

            is_csv_output = self.parameters.accept_type and "text/csv" in self.parameters.accept_type

            order_date = None
            for i, param in enumerate(query_order_by):
                if check_if_valid_date_str(param):
                    order_date = param
                    break
            # Remove the date order by as it is not actually used for ordering
            if order_date:
                sort_term = self._get_group_by()[0]
                query_order_by.pop(i)
                filtered_query_data = []
                for index in query_data:
                    for key, value in index.items():
                        if (key == "date") and (value == order_date):
                            filtered_query_data.append(index)
                ordered_data = self.order_by(filtered_query_data, query_order_by)
                order_of_interest = []
                for entry in ordered_data:
                    order_of_interest.append(entry.get(sort_term))
                # write a special order by function that iterates through the
                # rest of the days in query_data and puts them in the same order
                # return_query_data = []
                sorted_data = [item for x in order_of_interest for item in query_data if item.get(sort_term) == x]
                query_data = self.order_by(sorted_data, ["-date"])
            else:
                query_data = self.order_by(query_data, query_order_by)

            # cost_units_value = self._mapper.report_type_map.get("cost_units_fallback", "USD")
            usage_units_value = self._mapper.report_type_map.get("usage_units_fallback")
            count_units_value = self._mapper.report_type_map.get("count_units_fallback")
            if query_data:
                # cost_units_value = query_data[0].get("cost_units")
                if self._mapper.usage_units_key:
                    usage_units_value = query_data[0].get("usage_units")
                if self._mapper.report_type_map.get("annotations", {}).get("count_units"):
                    count_units_value = query_data[0].get("count_units")

            if is_csv_output:
                data = list(query_data)
            else:
                groups = copy.deepcopy(query_group_by)
                groups.remove("date")
                data = self._apply_group_by(list(query_data), groups)
                data = self._transform_data(query_group_by, 0, data)

        init_order_keys = []
        query_sum["cost_units"] = self.currency
        if self._mapper.usage_units_key and usage_units_value:
            init_order_keys = ["usage_units"]
            query_sum["usage_units"] = usage_units_value
        if self._mapper.report_type_map.get("annotations", {}).get("count_units") and count_units_value:
            query_sum["count_units"] = count_units_value
        key_order = list(init_order_keys + list(annotations.keys()))
        ordered_total = {total_key: query_sum[total_key] for total_key in key_order if total_key in query_sum}
        ordered_total.update(query_sum)
        self._pack_data_object(ordered_total, **self._mapper.PACK_DEFINITIONS)

        self.query_sum = ordered_total
        self.query_data = data
        return self._format_query_response()
