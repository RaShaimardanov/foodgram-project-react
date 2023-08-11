import json
from django.db import transaction
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


class WritableNestedThroughMixin():
    @transaction.atomic
    def create(self, validated_data):
        validated_data_no_nested = validated_data.copy()
        for key, value in self.get_fields().items():
            if isinstance(value, serializers.ListSerializer):
                validated_data_no_nested.pop(value.source if value.source is not None else key)

        main_obj = self.Meta.model.objects.create(**validated_data_no_nested)

        for key, value in self.get_fields().items():
            if isinstance(value, serializers.ListSerializer):
                items = validated_data.pop(value.source if value.source is not None else key, None)
                if items is not None:
                    ItemModel = value.child.Meta.model
                    link_field = None
                    for field in ItemModel._meta.fields:
                        if field.related_model == self.Meta.model:
                            link_field = field.name
                    if link_field is not None:
                        for item in items:
                            item[link_field] = main_obj
                            ItemModel.objects.create(**item)
        return main_obj


class MultipartNestedSupportMixin:

    def transform_request_data(self, data):
        # transform data sctructure to dictionnary
        force_dict_data = data
        if type(force_dict_data) == QueryDict:
            force_dict_data = force_dict_data.dict()
        

        # transform JSON string to dictionnary for each many field
        serializer = self.get_serializer()
        #print(force_dict_data)

        for key, value in serializer.get_fields().items():
            if isinstance(value, serializers.ListSerializer) or isinstance(value, serializers.ModelSerializer):
                if key in force_dict_data and type(force_dict_data[key]) == str:
                    if force_dict_data[key] == '':
                        force_dict_data[key] = None
                    else:
                        try:
                            force_dict_data[key] = json.loads(force_dict_data[key])
                        except:
                            pass

        return force_dict_data

    def create(self, request, *args, **kwargs):
        force_dict_data = self.transform_request_data(request.data)
        serializer = self.get_serializer(data=force_dict_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        force_dict_data = self.transform_request_data(request.data)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=force_dict_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
