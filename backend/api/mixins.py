from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet


class ListCreateRetrieveUpdateDestroyViewSet(
    CreateModelMixin, DestroyModelMixin,
    ListModelMixin, RetrieveModelMixin,
    UpdateModelMixin, GenericViewSet
):
    pass


class ListRetrieveViewSet(
    ListModelMixin, RetrieveModelMixin,
    GenericViewSet
):
    pass