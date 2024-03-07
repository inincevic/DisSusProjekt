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

# Route for listing all available workers
@app.get("/available_workers")
def available():
    return workers

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

# Task code that periodically tests if all the workers are still available
# Workers who aren't available are removed from the list
async def is_worker_available():
    global workers
    while True:
        updated_workers = []

        # For each worker who contacted the balancer and was registered,
        # the code checks if the worker is still available by contacting
        # them using a specialized route.
        for worker in workers:
            try:
                port_str = worker["port"]
                url = "http://127.0.0.1:" + port_str + "/check_in"
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
        print("------------------------------------")
        await asyncio.sleep(60)

# ----------------------------------------------------------------------------------- 
# Methods which send specific tasks to different workers depending on their ports
# While not useful yet, this will be used when sending work to multiple workers is implemented.

# Method for sending to /do_work/ route where the message is just inverted after sleeping.
async def sleep_work(port, message):
    port_str = str(port)
    url = "http://127.0.0.1:" + port_str + "/do_work/" + message
    print(url)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout = 25)
        return json.loads(response.text)

# Method which requests the contents of the file from the workers
async def get_file_contents(port):
    port_str = str(port)
    url = "http://127.0.0.1:" + port_str + "/read_from_file"
    print(url)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout = 25)
        return json.loads(response.text)

# Method for sending messages to workers, these messages need to be written into the file they colectivelly work on
async def write_message(port, message):
    port_str = str(port)
    url = "http://127.0.0.1:" + port_str + "/write_to_file/" + message
    print(url)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout = 25)
        return json.loads(response.text)



# -----------------------------------------------------------------------------------
# Routes which send different tasks to workers.

# Route which sends a message to the worker and expects the reversed message back after a certain 
# period of sleep on the workier
@app.get("/send_sleep/{message}")
async def send_work(message):
    # Print used for test purposes
    #print(f"Given message is: {message}.")
    ret_msg = await sleep_work(8001, message)
    return ret_msg

# Route for reading the contents of the file all workers write into
@app.get("/show_file")
async def show_file():
    file_contents = await get_file_contents(8001)
    return file_contents

# Route for sending messages to workers. These messages need to be written into the file
@app.get("/write_message/{message}")
async def send_work(message):
    # Print used for test purposes
    #print(f"Given message is: {message}.")
    ret_msg = await write_message(8001, message)
    return ret_msg


# -----------------------------------------------------------------------------------
# Code for deciding which worker should recieve the next task.