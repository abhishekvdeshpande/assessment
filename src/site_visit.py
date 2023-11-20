# Site Visit object to hold site visit properties
class SiteVisit:

    def __init__(self, sid, et, tags):
        self.site_visits_data = {
            "id": sid,
            "event_time": et,
            "tags": tags
        }
