# Customer Object to hold customer properties

from datetime import datetime
from heapq import heappush, heapify


class Customer:

    def __init__(self, et, ln, ct, st):
        self.details = {
            "event_time": et,
            "meta_data": {
                "last_name": ln,
                "adr_city": ct,
                "adr_state": st
            },
            "site_visits": [],
            "orders": [],
            "images": [],
            "created_on": et,
            "total_amount": 0
        }

    # Adds orders associated with the respective customer in an order where the latest order is stacked on top
    # Using max heap for the same here in order to easily fetch and update the update orders
    def add_order(self, order_event):
        order_date = datetime.strptime(order_event.order_data["event_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
        heappush(self.details["orders"], (-order_date.timestamp(), order_event))
        self.details["total_amount"] += order_event.order_data["amount"]

    # Method to pop the order thats required to be updated before re-inserting back as the latest order
    def pop_order_by_id(self, order_id):
        index_to_remove = None
        for i, (_, order) in enumerate(self.details["orders"]):
            if order.order_data["id"] == order_id:
                index_to_remove = i
                break
        if index_to_remove is not None:
            _, popped_order = self.details["orders"].pop(index_to_remove)
            heapify(self.details["orders"])  # Re-heapify after removal
            return popped_order

    # Update the existing Customer properties
    def update_customer(self, et, ln, ct, st):
        self.details["event_time"] = et
        self.details["meta_data"]["last_name"] = ln
        self.details["meta_data"]["adr_city"] = ct
        self.details["meta_data"]["adr_state"] = st
