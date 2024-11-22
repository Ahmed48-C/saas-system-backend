
from django.utils import timezone
from app.features.inventory_log.models import InventoryLog, ActionLog


class InventoryLogService:

    @staticmethod
    def add_inventory_log(
        userprofile_id,
        product_id,
        store_id,
        stock,
        action,
        auto_generated_note,
        stock_before_action,
        stock_after_action,
    ):
        new_log = InventoryLog.objects.create(
            userprofile_id = userprofile_id,
            product_id = product_id,
            store_id = store_id,
            action = action,
            action_date = timezone.now(),
            auto_generated_note = auto_generated_note,
            stock = stock,
            stock_before_action = stock_before_action,
            stock_after_action = stock_after_action,
        )
        new_log.save()

        return True