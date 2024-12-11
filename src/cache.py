import threading

class MeetingCache:
    def __init__(self):
        self.lock = threading.Lock()
        self.meetings = []  # list of meetings
        self.last_update = None

    def update_meetings(self, new_meetings):
        with self.lock:
            self.meetings = new_meetings

    def get_meetings(self):
        with self.lock:
            return list(self.meetings)

cache = MeetingCache()
