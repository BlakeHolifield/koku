#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""Views for Masu API `manifest`."""
from django.forms.models import model_to_dict
from django.utils.encoding import force_text
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from api.provider.models import Provider
from api.provider.models import Sources
from masu.api.sourceproviders.sources.serializers import SourceSerializer


class SourcePermission(permissions.BasePermission):
    """Determines if a user has access to SourceProvider APIs."""

    def has_permission(self, request, view):
        """Check permission based on the defined access."""
        return True


class SourceException(APIException):
    """Invalid query value"""

    def __init__(self, message):
        """Initialize with status code 404."""
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = {"detail": force_text(message)}


class SourceInvalidFilterException(APIException):
    """Invalid parameter value"""

    def __init__(self, message):
        """Initialize with status code 400."""
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = {"detail": force_text(message)}


class SourcesView(viewsets.ModelViewSet):
    """Manifest View class."""

    queryset = Sources.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [SourcePermission]
    http_method_names = ["get"]

    def get_provider_UUID(request, provider):
        """returns provider uuid based on provider name"""
        provider = Provider.objects.filter(name=provider).first()
        if provider is None:
            raise SourceException("Invalid provider name.")
        return model_to_dict(provider)

    @staticmethod
    def check_filters(dict_):
        """Check if filter parameters are valid"""
        valid_query_params = ["name", "limit", "offset"]
        params = {k: dict_.get(k) for k in dict_.keys() if k not in valid_query_params}
        if params:
            raise SourceException("Invalid Filter Parameter")

    def set_pagination(self, request, queryset, serializer):
        """Sets up pagination"""
        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized = serializer(page, many=True).data
            return serialized

    def get_all_sources(self, request, *args, **kwargs):
        """API list all Manifests, filter by: provider name"""
        param = self.request.query_params
        self.check_filters(param.dict())
        if request.GET.get("name"):
            providers = self.get_provider_UUID(param["name"])
            queryset = self.queryset.filter(provider_id=providers["uuid"])
            pagination = self.set_pagination(self, queryset, SourceSerializer)
            if pagination is not None:
                return self.get_paginated_response(pagination)
            return Response(SourceSerializer(queryset).data, many=True)
        else:
            return super().list(request)

    def get_sources_by_account_id(self, request, *args, **kwargs):
        """Get source by schema"""
        sourceuuidParam = kwargs
        try:
            queryset = self.queryset.filter(account_id=sourceuuidParam["account_id"])
        except Exception:
            raise SourceException("Invalid source uuid.")

        pagination = self.set_pagination(self, queryset, SourceSerializer)
        if pagination is not None:
            return self.get_paginated_response(pagination)

        queryset = SourceSerializer(queryset, many=True).data
        return Response(queryset)