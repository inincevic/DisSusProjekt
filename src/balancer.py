import fastapi

app = fastapi.FastAPI()
import httpx
import json

# Test route
@app.get("/")
def test_get():
    return "The code works."

# Function which connects to a different code
async def contact_worker(port, message):
    port_str = str(port)
    url = "http://127.0.0.1:" + port_str + "/fib/" + message
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return json.loads(response.text)


# Ruta which sends tasks to the worker
@app.get("/send_work")
def send_work():
    pass
