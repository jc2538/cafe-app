#!/usr/bin/env python

# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import random

from datetime import datetime
from locust import HttpLocust, TaskSet, task


class MetricsTaskSet(TaskSet):
    # _location = None
    # _duration = None
    # _publishedTime = None

    # def on_start(self):
    #     self._location = str("0") # TODO: change once all locationIds established
    #     self._duration = str(random.randint(0,30))

    @task(1)
    def add(self):
        location = 0 # TODO: change once all locationIds established
        duration = random.randint(0,30)
        current_time = datetime.now()
        publishedTime = str(current_time.hour) + ":" + str(current_time.minute)

        self.client.post(
            '/add', {"location": location, "duration": duration, "publishedTime": publishedTime})

    @task(4)
    def query(self):
        location_id = 0 # TODO: change once all locationIds established
        current_time = datetime.now()
        publishedTime = str(current_time.hour) + ":" + str(current_time.minute)

        self.client.post(
            "/query", {"location_id": location_id, "publishedTime": publishedTime})

class MetricsLocust(HttpLocust):
    task_set = MetricsTaskSet