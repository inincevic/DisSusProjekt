import fastapi

app = fastapi.FastAPI()

# Test route
@app.get("/")
def test_get():
    return "The code works."