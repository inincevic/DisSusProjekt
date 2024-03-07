import fastapi, httpx, json, asyncio

app = fastapi.FastAPI()

# List of all available workers
workers = [] 

# Startup tasks
@app.on_event("startup")
async def start_periodic_task():
    # Empty the list of a vailable workers
    global workers
    workers = []

    # Continual task that check if the workers in the list are still available
    task = asyncio.create_task(is_worker_available())

# Test route
@app.get("/")
def test_get():
    return "The code works."

# Route for listing all available servers
@app.get("/available_workers")
def available():
    return workers

# Task code that periodically tests which of the workers are available
async def is_worker_available():
    global workers
    while True:
        updated_workers = []
        for worker in workers:
            try:
                port_str = worker["port"]
                url = "http://127.0.0.0:" + port_str + "/check_in"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
            except httpx.ReadTimeout:
                print(f"Worker {worker['worker']} did not reply. Removing from the list of available workers.")
                continue
            except httpx.ConnectError:
                print(f"Worker {worker['worker']} did not reply. Removing from the list of available workers.")
                continue
            updated_workers.append(worker)
        workers = updated_workers
        print("Updated the list of available workers")
        print(workers)
        print("---------------HAHAHAH NOOOB---------------------")
        await asyncio.sleep(60)

# Route on which the workers register in the load balancer
@app.get("/register_worker/{port}")
def new_worker(request: fastapi.Request, port):
    client_ip = request.client.host
    client_port = port

    # Prints out from which IP and which Port the registration request came from. Used for testing
    # print(f"Request from {client_ip}:{client_port}")

    worker_name = "worker" + str(client_port)
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
