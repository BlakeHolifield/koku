#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""GCP Query Handling for Reports."""
from __future__ import annotations

import copy
import logging
from collections import defaultdict
from decimal import Decimal

import pandas as pd
from django.db.models import F
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from tenant_schemas.utils import tenant_context

from api.models import Provider
from api.report.gcp.provider_map import GCPProviderMap
from api.report.queries import check_if_valid_date_str
from api.report.queries import ReportQueryHandler

LOG = logging.getLogger(__name__)


class GCPReportQueryHandler(ReportQueryHandler):
    """Handles report queries and responses for GCP."""

    provider = Provider.PROVIDER_GCP

    network_services = {
        "Network",
        "VPC",
        "Firewall",
        "Route",
        "IP",
        "DNS",
        "CDN",
        "NAT",
        "Traffic Director",
        "Service Discovery",
        "Cloud Domains",
        "Private Service Connect",
        "Cloud Armor",
    }

    database_services = {"SQL", "Spanner", "Bigtable", "Firestore", "Firebase", "Memorystore", "MongoDB"}

    def __init__(self, parameters):
        """Establish GCP report query handler.

        Args:
            parameters    (QueryParameters): parameter object for query

        """
        # do not override mapper if its already set
        try:
            getattr(self, "_mapper")
        except AttributeError:
            self._mapper = GCPProviderMap(provider=self.provider, report_type=parameters.report_type)

        self.group_by_options = self._mapper.provider_map.get("group_by_options")
        self._limit = parameters.get_filter("limit")
        self.is_csv_output = parameters.accept_type and "text/csv" in parameters.accept_type
        self.group_by_alias = {"service": "service_alias", "gcp_project": "project_name"}

        # We need to overwrite the pack keys here to include the credit
        # dictionary in the endpoint returns.
        gcp_pack_keys = {
            "infra_raw": {"key": "raw", "group": "infrastructure"},
            "infra_markup": {"key": "markup", "group": "infrastructure"},
            "infra_usage": {"key": "usage", "group": "infrastructure"},
            "infra_credit": {"key": "credit", "group": "infrastructure"},
            "infra_total": {"key": "total", "group": "infrastructure"},
            "sup_raw": {"key": "raw", "group": "supplementary"},
            "sup_markup": {"key": "markup", "group": "supplementary"},
            "sup_usage": {"key": "usage", "group": "supplementary"},
            "sup_credit": {"key": "credit", "group": "supplementary"},
            "sup_total": {"key": "total", "group": "supplementary"},
            "cost_raw": {"key": "raw", "group": "cost"},
            "cost_markup": {"key": "markup", "group": "cost"},
            "cost_usage": {"key": "usage", "group": "cost"},
            "cost_credit": {"key": "credit", "group": "cost"},
            "cost_total": {"key": "total", "group": "cost"},
        }
        gcp_pack_definitions = copy.deepcopy(self._mapper.PACK_DEFINITIONS)
        gcp_pack_definitions["cost_groups"]["keys"] = gcp_pack_keys

        # super() needs to be called after _mapper and _limit is set
        super().__init__(parameters)
        self._mapper.PACK_DEFINITIONS = gcp_pack_definitions

    @property
    def annotations(self):
        """Create dictionary for query annotations.

        Returns:
            (Dict): query annotations dictionary

        """
        units_fallback = self._mapper.report_type_map.get("cost_units_fallback")
        annotations = {
            "date": self.date_trunc("usage_start"),
            "cost_units": Coalesce(self._mapper.cost_units_key, Value(units_fallback)),
        }
        if self._mapper.usage_units_key:
            units_fallback = self._mapper.report_type_map.get("usage_units_fallback")
            annotations["usage_units"] = Coalesce(self._mapper.usage_units_key, Value(units_fallback))
        fields = self._mapper.provider_map.get("annotations")
        for q_param, db_field in fields.items():
            annotations[q_param] = Concat(db_field, Value(""))
        group_by_fields = self._mapper.provider_map.get("group_by_annotations")
        for group_key in self._get_group_by():
            if group_by_fields.get(group_key):
                for q_param, db_field in group_by_fields[group_key].items():
                    annotations[q_param] = Concat(db_field, Value(""))
        return annotations

    def _format_query_response(self):
        """Format the query response with data.

        Returns:
            (Dict): Dictionary response of query params, data, and total

        """
        output = self._initialize_response_output(self.parameters)
        output["data"] = self.query_data
        output["total"] = self.query_sum

        if self._delta:
            output["delta"] = self.query_delta

        return output

    def _build_sum(self, query):
        """Build the sum results for the query."""
        sum_units = {}
        query_sum = self.initialize_totals()

        cost_units_fallback = self._mapper.report_type_map.get("cost_units_fallback")
        usage_units_fallback = self._mapper.report_type_map.get("usage_units_fallback")

        if query:
            sum_annotations = {"cost_units": Coalesce(self._mapper.cost_units_key, Value(cost_units_fallback))}
            if self._mapper.usage_units_key:
                units_fallback = self._mapper.report_type_map.get("usage_units_fallback")
                sum_annotations["usage_units"] = Coalesce(self._mapper.usage_units_key, Value(units_fallback))
            sum_query = query.annotate(**sum_annotations).order_by()

            units_value = sum_query.values("cost_units").first().get("cost_units", cost_units_fallback)
            sum_units = {"cost_units": units_value}
            if self._mapper.usage_units_key:
                units_value = sum_query.values("usage_units").first().get("usage_units", usage_units_fallback)
                sum_units["usage_units"] = units_value

            query_sum = self.calculate_total(**sum_units)
        else:
            sum_units["cost_units"] = cost_units_fallback
            if self._mapper.report_type_map.get("annotations", {}).get("usage_units"):
                sum_units["usage_units"] = usage_units_fallback
            query_sum.update(sum_units)
            self._pack_data_object(query_sum, **self._mapper.PACK_DEFINITIONS)
        return query_sum

    def execute_query(self):  # noqa: C901
        """Execute query and return provided data.

        Returns:
            (Dict): Dictionary response of query params, data, and total

        """
        data = []

        with tenant_context(self.tenant):
            query = self.query_table.objects.filter(self.query_filter)
            query_data = query.annotate(**self.annotations)
            query_group_by = ["date"] + self._get_group_by()
            initial_group_by = query_group_by + [self._mapper.cost_units_key]
            query_order_by = ["-date"]
            query_order_by.extend(self.order)  # add implicit ordering
            annotations = self._mapper.report_type_map.get("annotations")

            for alias_key, alias_value in self.group_by_alias.items():
                if alias_key in query_group_by:
                    annotations[f"{alias_key}_alias"] = F(alias_value)
            query_data = query_data.values(*initial_group_by).annotate(**annotations)
            query_sum = self._build_sum(query)
            skip_columns = ["clusters"]
            query_data = self.pandas_agg_for_currency(
                query_group_by, query_data, skip_columns, self.report_annotations
            )

            if self._limit:
                query_data = self._group_by_ranks(query, query_data)
                if not self.parameters.get("order_by"):
                    # override implicit ordering when using ranked ordering.
                    query_order_by[-1] = "rank"

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
                # &order_by[cost]=desc&order_by[date]=2021-08-02
                query_data = self.order_by(query_data, query_order_by)

            if is_csv_output:
                data = list(query_data)
            else:
                groups = copy.deepcopy(query_group_by)
                groups.remove("date")
                data = self._apply_group_by(list(query_data), groups)
                data = self._transform_data(query_group_by, 0, data)

        key_order = list(["units"] + list(annotations.keys()))
        ordered_total = {total_key: query_sum[total_key] for total_key in key_order if total_key in query_sum}
        ordered_total.update(query_sum)

        self.query_sum = ordered_total
        self.query_data = data
        return self._format_query_response()

    def calculate_total(self, **units):
        """Calculate aggregated totals for the query.

        Args:
            units (dict): The units dictionary

        Returns:
            (dict) The aggregated totals for the query

        """
        query_group_by = ["date"] + self._get_group_by()
        initial_group_by = query_group_by + [self._mapper.cost_units_key]
        query = self.query_table.objects.filter(self.query_filter)
        query_data = query.annotate(**self.annotations)
        query_data = query_data.values(*initial_group_by)
        aggregates = self._mapper.report_type_map.get("aggregates")

        query_data = query_data.annotate(**aggregates)
        # skip_columns = ["source_uuid", "gcp_project_alias", "clusters", "service_alias"]
        # total_query = self.pandas_agg_for_total(query_data, skip_columns, self.report_annotations, units)
        columns = list(aggregates.keys())

        if query_data:
            df = pd.DataFrame(query_data)
            exchange_rates = {
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
                "AUD": {"USD": Decimal(0.7194244604), "CAD": Decimal(1.34)},
                "USD": {"USD": Decimal(1.0)},
            }
            for column in columns:
                df[column] = df.apply(lambda row: row[column] * exchange_rates[row["currency"]][self.currency], axis=1)
                df["cost_units"] = self.currency
            skip_columns = ["source_uuid", "gcp_project_alias", "clusters", "service_alias"]
            if "count" not in df.columns:
                skip_columns.extend(["count", "count_units"])
            if "usage" in df.columns:
                df["usage_units"] = units.get("usage_units")
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
            total_query = dct
        else:
            total_query = query_data.aggregate(**aggregates)
        for unit_key, unit_value in units.items():
            total_query[unit_key] = unit_value
            if unit_key not in ["usage_units", "count_units"]:
                total_query[unit_key] = self.currency

        self._pack_data_object(total_query, **self._mapper.PACK_DEFINITIONS)

        return total_query
