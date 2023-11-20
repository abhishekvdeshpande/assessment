# Order Object to hold order properties
class Orders:

    def __init__(self, oid, et, amt):
        self.order_data = {
            "id": oid,
            "event_time": et,
            "amount": amt
        }
