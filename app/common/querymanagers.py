import json
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import F
from django.db import connection
from django.db.utils import OperationalError
from django.apps import apps


class CommonQueryManager(models.Manager):

    @staticmethod
    def fetch_rules(userprofile):
        function_rules = userprofile.permission_role.function_rules.all()

        function_rules_result = []
        for rule in function_rules:
            function_result = {
                "function_key": rule.function_key,
            }

            function_rules_result.append(function_result)

        return {
            "function_rules": function_rules_result
        }

    @staticmethod
    def json_object(actual_total_count, data):
        obj = {
            "actual_total_count": actual_total_count,
            "data": data
        }

        return obj

    @staticmethod
    def get_filtered_result(request, result):
        result_with_filter = None

        # used for table sorting/ordering
        order_by = []

        # parameters should be passed in the following format:
        # eg. : filters=[{"aisle_no":"1","operating_unit_aisle_detail__product__product_tag__id":[16,6,21],"operating_unit_aisle_detail__product__id":2749}]
        for param in request.query_params:
            if str(param) == "filters":
                try:
                    # list of dicts
                    filters_list = json.loads(request.query_params["filters"])
                    # basic additional filter ("and" single values)
                    for param_json in filters_list:
                        additional_filter = {}
                        for value in param_json:
                            if param_json[value] is not None and param_json[value] != "":
                                if value == "id" or "_id" in value and value != 'group_id':
                                    additional_filter[value] = param_json[value]
                                else:
                                    additional_filter[value +
                                                        "__icontains"] = param_json[value]
                        # apply filtering
                        filtered_result = result.filter(**additional_filter)

                        if result_with_filter is None:
                            result_with_filter = filtered_result
                        else:
                            result_with_filter = result_with_filter | filtered_result

                except json.decoder.JSONDecodeError as je:
                    logger.error("SERIALIZER SAVE ERROR MESSAGE: %s ", str(je))
                    return result.none()
                except FieldError as fe:
                    logger.error("SERIALIZER SAVE ERROR MESSAGE: %s ", str(fe))
                    return result.none()
                except ValueError as ve:
                    logger.error("SERIALIZER SAVE ERROR MESSAGE: %s ", str(ve))
                    return result.none()
                except TypeError as te:
                    logger.error("SERIALIZER SAVE ERROR MESSAGE: %s ", str(te))
                    return result.none()


            elif str(param) == "order_by":
                column = request.query_params[param]

                # collect the sorting/ordering column
                order_by.append(column)

        if result_with_filter is not None:
            result = result_with_filter

        try:
            # apply the sorting/ordering
            return result.order_by(*order_by)
        except FieldError as e:
            logger.error("Error on ordering the result: %s ", str(e))
            return result