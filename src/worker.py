import fastapi

app = fastapi.FastAPI()


# Test route
@app.get("/")
def test_get():
    return "The worker code works."