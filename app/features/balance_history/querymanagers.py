from django.db.models import Q, Count
from app.common.querymanagers import CommonQueryManager
import uuid
from django.utils import timezone

class BalanceHistoryQueryManager(CommonQueryManager):
    def filter_by_permission_and_param(self, request):
        result = super().get_queryset().all()

        return CommonQueryManager.get_filtered_result(request, result)

    def get_all_by_limit(self, request):
        items = self.filter_by_permission_and_param(request)

        actual_total_count = items.count()

        if ('from' in request.query_params and 'to' in request.query_params) and (
                request.query_params["from"].isnumeric() and request.query_params["to"].isnumeric()):
                paginated_items = items[int(request.query_params["from"]):int(request.query_params["to"])]
                return paginated_items, actual_total_count

        return items, actual_total_count