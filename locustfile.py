from locust import HttpUser, task, between, LoadTestShape

TARGET_URL = "https://hijididi.in/api"   # Change this

LOOP_DURATION = 1200  # 20 minutes cycle

class AggressiveLoadShape(LoadTestShape):
    stages = [
        (30,     5_000,   300),
        (90,    20_000,   800),
        (180,   50_000,  1200),
        (300,   80_000,  1500),
        (600,  120_000,   800),
        (900,  120_000,   600),
        (1080,  60_000,   800),
        (1200,  10_000,   500),
    ]

    def tick(self):
        run_time = self.get_run_time()
        cycle_time = run_time % LOOP_DURATION
        for stage_end, users, spawn_rate in self.stages:
            if cycle_time < stage_end:
                return (users, spawn_rate)
        return None


class VercelAppUser(HttpUser):
    host = TARGET_URL
    wait_time = between(0.5, 1.5)

    @task(5)
    def homepage(self):
        with self.client.get("/", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Home fail: {res.status_code}")

    @task(3)
    def about_page(self):
        with self.client.get("/about", catch_response=True) as res:
            res.success() if res.status_code in [200, 404] else res.failure(...)

    @task(4)
    def api_endpoint(self):
        with self.client.post("/api/hello", json={"test": "data"}, catch_response=True) as res:
            res.success() if res.status_code in [200, 201] else res.failure(...)

    @task(2)
    def heavy_api(self):
        with self.client.post("/api/heavy", json={"load": "test"}, catch_response=True) as res:
            res.success() if res.status_code < 400 else res.failure(...)
