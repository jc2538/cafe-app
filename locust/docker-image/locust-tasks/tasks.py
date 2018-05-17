import random

from datetime import datetime
from locust import HttpLocust, TaskSet, task


class MetricsTaskSet(TaskSet):

    @task(1)
    def add(self):
        location = 0 # TODO: change once all locationIds established
        
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        publishedTime = str(hour) + ":" + str(minute)

        if hour < 8 | hour >= 21:
            duration = 0
        elif hour >= 8 & hour < 9:
            duration = 1
        elif hour >= 9 & hour < 10:
            duration = 4
        elif hour >= 10 & hour < 11:
            duration = 6
        elif hour >= 11 & hour < 12:
            duration = 12
        elif hour >= 12 & hour < 13:
            duration = 17
        elif hour >= 13 & hour < 14:
            duration = 11
        elif hour >= 14 & hour < 15:
            duration = 8
        elif hour >= 15 & hour < 16:
            duration = 7
        elif hour >= 16 & hour < 17:
            duration = 7
        elif hour >= 17 & hour < 18:
            duration = 8
        elif hour >= 18 & hour < 19:
            duration = 10
        elif hour >= 19 & hour < 20:
            duration = 10
        elif hour >= 20 & hour < 21:
            duration = 9
        else:
            duration = random.randint(0,30)

        self.client.post(
            '/add', {"location": location, "duration": duration, "publishedTime": publishedTime})

    @task(5)
    def query(self):
        location_id = "Mattins" # TODO: change once all locationIds established
        current_time = datetime.now()
        publishedTime = str(current_time.hour) + ":" + str(current_time.minute)

        self.client.post(
            "/query", {"location": location_id, "publishedTime": publishedTime})

class MetricsLocust(HttpLocust):
    task_set = MetricsTaskSet