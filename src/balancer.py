import fastapi

app = fastapi.FastAPI()
import httpx
import json

# List of all available workers
workers = [] 

# Test route
@app.get("/")
def test_get():
    return "The code works."

# Route for checking all available servers
@app.get("/available_workers")
def available():
    return workers

# Route on which the workers register in the load balancer
@app.get("/register_worker/{port}")
def new_worker(request: fastapi.Request, port):
    client_ip = request.client.host
    client_port = port

    print(f"Request from {client_ip}:{client_port}")

    worker_name = "worker" + str(len(workers))
    workers.append({
        "worker": worker_name,
        "port": str(client_port),
        "running": 0,
        "total_tasks_done": 0
    })
    return 201

# Function which connects to a different code
async def contact_worker(port, message):
    port_str = str(port)
    url = "http://127.0.0.1:" + port_str + "/do_work/" + message
    print(url)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout = 25)
        return json.loads(response.text)


# Ruta which sends tasks to the worker
@app.get("/send_work/{message}")
async def send_work(message):
    print(f"Given message is: {message}.")
    ret_msg = await contact_worker(8001, message)
    return ret_msg
