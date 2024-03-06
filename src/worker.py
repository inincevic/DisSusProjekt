import fastapi, time, httpx, sys, json

app = fastapi.FastAPI()

# Startup event that contacts the balancer and registers the worker, with the port it is running on
@app.on_event("startup")
async def contact_server():
    async with httpx.AsyncClient() as client:
        if "--port" in sys.argv:
            index = sys.argv.index("--port")
            port = int(sys.argv[index + 1])
        print(port)
        response = await client.get("http://127.0.0.1:8000/register_worker/" + str(port))
        return json.loads(response.text)

# Test route
@app.get("/")
def test_get():
    return "The worker code works."

# Message wait
@app.get("/do_work/{message}")
def do_work(message):
    print(f"I recieved the following message: {message}.")
    time.sleep(20)
    message2 = message[::-1]
    print(f"Reversed message: {message2}")
    print(f"Done sleeping, returning reversed message: {message2}")
    return message2
