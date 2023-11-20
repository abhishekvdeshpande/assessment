# Image Object to hold Image properties
class Images:

    def __init__(self, iid, et, make, model):
        self.image_data = {
            "id": iid,
            "event_time": et,
            "camera_make": make,
            "camera_model": model
        }
