from locust import HttpUser, TaskSet, task, between
import random
import string

def random_email():
    return ''.join(random.choices(string.ascii_lowercase, k=5)) + "@test.com"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

class UserBehavior(TaskSet):
    def on_start(self):
        self.email = random_email()
        self.password = "testpassword"

        self.client.post("/auth/register", json={
            "email": self.email,
            "password": self.password,
            "firstname": "Test",
            "lastname": "User"
        })

        response = self.client.post("/auth/login", json={
            "email": self.email,
            "password": self.password
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.user_id = data.get("user", {}).get("_id")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.user_id = None
            self.headers = {}

    @task(3)
    def view_timeline(self):
        if not self.user_id:
            return

        res = self.client.get(f"/post/{self.user_id}/timeline", headers=self.headers)
        if res.status_code == 200:
            self.timeline_posts = res.json()

    @task(2)
    def create_post(self):
        if not self.user_id:
            return

        self.client.post("/post", json={
            "userId": self.user_id,
            "desc": random_string(20)
        }, headers=self.headers)

    @task(1)
    def follow_random_user(self):
        if not self.user_id:
            return

        res = self.client.get("/user", headers=self.headers)
        if res.status_code == 200:
            all_users = res.json()
            other_users = [u for u in all_users if u["_id"] != self.user_id]
            if other_users:
                target = random.choice(other_users)
                self.client.put(f"/user/{target['_id']}/follow", json={
                    "_id": self.user_id
                }, headers=self.headers)

    @task(1)
    def like_random_post_from_timeline(self):
        if not self.user_id:
            return

        res = self.client.get(f"/post/{self.user_id}/timeline", headers=self.headers)
        if res.status_code != 200:
            return

        posts = res.json()
        if posts:
            post = random.choice(posts)
            self.client.put(f"/post/{post['_id']}/like_dislike", json={
                "userId": self.user_id
            }, headers=self.headers)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
