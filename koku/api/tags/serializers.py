#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""Tag serializers."""
from rest_framework import serializers

from api.report.serializers import add_operator_specified_fields
from api.report.serializers import handle_invalid_fields
from api.report.serializers import ParamSerializer
from api.report.serializers import StringOrListField
from api.report.serializers import validate_field


OCP_FILTER_OP_FIELDS = ["project", "enabled", "cluster"]
AWS_FILTER_OP_FIELDS = ["account"]
AZURE_FILTER_OP_FIELDS = ["subscription_guid"]
GCP_FILTER_OP_FIELDS = ["account", "gcp_project"]
OCI_FILTER_OP_FIELDS = ["payer_tenant_id"]
day_list = ["-10", "-30", "-90"]
month_list = [-1, -2, -3]
month_list_string = [str(m) for m in month_list]


class FilterSerializer(serializers.Serializer):
    """Serializer for handling tag query parameter filter."""

    RESOLUTION_CHOICES = (("daily", "daily"), ("monthly", "monthly"))
    TIME_CHOICES = (("-10", "-10"), ("-30", "-30"), ("-90", "-90"), ("-1", "-1"), ("-2", "-2"), ("-3", "-3"))
    TIME_UNIT_CHOICES = (("day", "day"), ("month", "month"))

    key = StringOrListField(required=False)
    value = StringOrListField(required=False)
    resolution = serializers.ChoiceField(choices=RESOLUTION_CHOICES, required=False)
    time_scope_value = serializers.ChoiceField(choices=TIME_CHOICES, required=False)
    time_scope_units = serializers.ChoiceField(choices=TIME_UNIT_CHOICES, required=False)

    def validate(self, data):
        """Validate incoming data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter inputs are invalid

        """
        handle_invalid_fields(self, data)

        resolution = data.get("resolution")
        time_scope_value = data.get("time_scope_value")
        time_scope_units = data.get("time_scope_units")

        if time_scope_units and time_scope_value:
            msg = "Valid values are {} when time_scope_units is {}"
            if time_scope_units == "day" and time_scope_value in month_list_string:  # noqa: W504
                valid_values = day_list
                valid_vals = ", ".join(valid_values)
                error = {"time_scope_value": msg.format(valid_vals, "day")}
                raise serializers.ValidationError(error)
            if time_scope_units == "day" and resolution == "monthly":
                valid_values = ["daily"]
                valid_vals = ", ".join(valid_values)
                error = {"resolution": msg.format(valid_vals, "day")}
                raise serializers.ValidationError(error)
            if time_scope_units == "month" and time_scope_value in day_list:  # noqa: W504
                valid_values = month_list_string
                valid_vals = ", ".join(valid_values)
                error = {"time_scope_value": msg.format(valid_vals, "month")}
                raise serializers.ValidationError(error)
        return data


class OCPFilterSerializer(FilterSerializer):
    """Serializer for handling tag query parameter filter."""

    TYPE_CHOICES = (("pod", "pod"), ("storage", "storage"), ("*", "*"))
    type = serializers.ChoiceField(choices=TYPE_CHOICES, required=False)
    project = StringOrListField(child=serializers.CharField(), required=False)
    enabled = serializers.BooleanField(default=True, required=False)
    cluster = StringOrListField(child=serializers.CharField(), required=False)

    def __init__(self, *args, **kwargs):
        """Initialize the OCPFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, OCP_FILTER_OP_FIELDS)


class AWSFilterSerializer(FilterSerializer):
    """Serializer for handling tag query parameter filter."""

    account = StringOrListField(child=serializers.CharField(), required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    def __init__(self, *args, **kwargs):
        """Initialize the AWSFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, AWS_FILTER_OP_FIELDS)


class OCPAWSFilterSerializer(AWSFilterSerializer, OCPFilterSerializer):
    """Serializer for handling tag query parameter filter."""

    def __init__(self, *args, **kwargs):
        """Initialize the AWSFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, AWS_FILTER_OP_FIELDS + OCP_FILTER_OP_FIELDS)


class AzureFilterSerializer(FilterSerializer):
    """Serializer for handling tag query parameter filter."""

    subscription_guid = StringOrListField(child=serializers.CharField(), required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    def __init__(self, *args, **kwargs):
        """Initialize the AzureFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, AZURE_FILTER_OP_FIELDS)


class OCPAzureFilterSerializer(AzureFilterSerializer, OCPFilterSerializer):
    """Serializer for handling tag query parameter filter."""

    def __init__(self, *args, **kwargs):
        """Initialize the AzureFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, AZURE_FILTER_OP_FIELDS + OCP_FILTER_OP_FIELDS)


class OCPAllFilterSerializer(AWSFilterSerializer, AzureFilterSerializer, OCPFilterSerializer):
    """Serializer for handling tag query parameter filter."""

    def __init__(self, *args, **kwargs):
        """Initialize the AWSFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(
            self.fields, AWS_FILTER_OP_FIELDS + AZURE_FILTER_OP_FIELDS + OCP_FILTER_OP_FIELDS
        )


class GCPFilterSerializer(FilterSerializer):
    """Serializer for handling tag query parameter filter."""

    account = StringOrListField(child=serializers.CharField(), required=False)
    gcp_project = StringOrListField(child=serializers.CharField(), required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    def __init__(self, *args, **kwargs):
        """Initialize the GCPFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, GCP_FILTER_OP_FIELDS)


class OCPGCPFilterSerializer(GCPFilterSerializer, OCPFilterSerializer):
    """Serializer for handling tag query parameter filter."""

    def __init__(self, *args, **kwargs):
        """Initialize the GCPFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, GCP_FILTER_OP_FIELDS + OCP_FILTER_OP_FIELDS)


class OCIFilterSerializer(FilterSerializer):
    """Serializer for handling tag query parameter filter."""

    payer_tenant_id = StringOrListField(child=serializers.CharField(), required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    def __init__(self, *args, **kwargs):
        """Initialize the OCIFilterSerializer."""
        super().__init__(*args, **kwargs)
        add_operator_specified_fields(self.fields, OCI_FILTER_OP_FIELDS)


class TagsQueryParamSerializer(ParamSerializer):
    """Serializer for handling query parameters."""

    filter = FilterSerializer(required=False)
    key_only = serializers.BooleanField(default=False)
    limit = serializers.IntegerField(required=False, min_value=1)
    offset = serializers.IntegerField(required=False, min_value=0)

    # DateField defaults: format='iso-8601', input_formats=['iso-8601']
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, data):
        """Validate incoming data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if field inputs are invalid

        """
        super().validate(data)
        handle_invalid_fields(self, data)

        return data


class OCPTagsQueryParamSerializer(TagsQueryParamSerializer):
    """Serializer for handling OCP tag query parameters."""

    filter = OCPFilterSerializer(required=False)

    def validate_filter(self, value):
        """Validate incoming filter data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter field inputs are invalid

        """
        validate_field(self, "filter", OCPFilterSerializer, value)
        return value


class AWSTagsQueryParamSerializer(TagsQueryParamSerializer):
    """Serializer for handling AWS tag query parameters."""

    filter = AWSFilterSerializer(required=False)

    def validate_filter(self, value):
        """Validate incoming filter data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter field inputs are invalid

        """
        validate_field(self, "filter", AWSFilterSerializer, value)
        return value


class OCPAWSTagsQueryParamSerializer(AWSTagsQueryParamSerializer, OCPTagsQueryParamSerializer):
    """Serializer for handling OCP-on-AWS tag query parameters."""

    filter = OCPAWSFilterSerializer(required=False)


class OCPAllTagsQueryParamSerializer(AWSTagsQueryParamSerializer, OCPTagsQueryParamSerializer):
    """Serializer for handling OCP-on-All tag query parameters."""

    filter = OCPAllFilterSerializer(required=False)


class AzureTagsQueryParamSerializer(TagsQueryParamSerializer):
    """Serializer for handling Azure tag query parameters."""

    filter = AzureFilterSerializer(required=False)

    def validate_filter(self, value):
        """Validate incoming filter data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter field inputs are invalid

        """
        validate_field(self, "filter", AzureFilterSerializer, value)
        return value


class OCPAzureTagsQueryParamSerializer(AzureTagsQueryParamSerializer, OCPTagsQueryParamSerializer):
    """Serializer for handling OCP-on-Azure tag query parameters."""

    filter = OCPAzureFilterSerializer(required=False)


class GCPTagsQueryParamSerializer(TagsQueryParamSerializer):
    """Serializer for handling GCP tag query parameters."""

    filter = GCPFilterSerializer(required=False)

    def validate_filter(self, value):
        """Validate incoming filter data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter field inputs are invalid

        """
        validate_field(self, "filter", GCPFilterSerializer, value)
        return value


class OCPGCPTagsQueryParamSerializer(GCPTagsQueryParamSerializer, OCPTagsQueryParamSerializer):
    """Serializer for handling OCP-on-GCP tag query parameters."""

    filter = OCPGCPFilterSerializer(required=False)


class OCITagsQueryParamSerializer(TagsQueryParamSerializer):
    """Serializer for handling OCI tag query parameters."""

    filter = OCIFilterSerializer(required=False)

    def validate_filter(self, value):
        """Validate incoming filter data.

        Args:
            data    (Dict): data to be validated
        Returns:
            (Dict): Validated data
        Raises:
            (ValidationError): if filter field inputs are invalid

        """
        validate_field(self, "filter", OCIFilterSerializer, value)
        return value
