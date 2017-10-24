from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
    @task(1)
    def shorten_url(self):
        self.client.post("/shorten_url", data='{"url":"google.com"}')

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 2000
