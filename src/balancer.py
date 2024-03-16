import fastapi, httpx, json, asyncio, random, sys, subprocess

app = fastapi.FastAPI()

# List of all available workers
workers = []

# Startup tasks
@app.on_event("startup")
async def start_periodic_task():
    global workers

    # Empty the list of available workers when the balancer starts
    workers = []
    
    # Continual task that check if the workers in the list are still available
    task = asyncio.create_task(is_worker_available())


# -----------------------------------------------------------------------
# Management Routes

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
    global workers
    client_ip = request.client.host
    client_port = port

    # Prints out from which IP and which Port the registration request came from. Used for testing
    # print(f"Request from {client_ip}:{client_port}")

    # Checking if the worker has already been registered on the load balancer
    for worker in workers:
        if client_port == worker["port"]:
            return "This worker has already been registered."

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

        # Prints that show what the list of workers after checking the connections looks like. Used in testing.
        # print("Updated the list of available workers")
        # print(workers)
        # print("------------------------------------")
        await asyncio.sleep(20)


# Route for sharing the current list of available workers with the workers
# when they check if the balancer is still online
@app.get("/balancer_working")
async def balancer_working():
    global workers
    # Print that confirms when a worker has checked if the balaancer is still online.
    # print("A worker has checked in on the health of this balancer.")
    return workers


# ----------------------------------------------------------------------------------- 
# Methods which send specific tasks to different workers depending on their ports

# Method for sending to /do_work/ route where the message is just inverted after sleeping.
async def sleep_work(message):
    task_worker = await choose_worker()
    port = task_worker["port"]
    # Print that confirms to which worker was the task sent.
    # print(f"Working on port {port}")
    
    url = "http://127.0.0.1:" + port + "/do_work/" + message
    # Print that confirms the final URL on which the task will be sent. Used for testing purposes.
    # print(url)
    
    async with httpx.AsyncClient() as client:
        task_worker["running"] += 1
        response = await client.get(url, timeout = 40)
        task_worker["running"] -= 1
        task_worker["total_tasks_done"] += 1
        return json.loads(response.text)

# Method which requests the contents of the file from the workers
async def get_file_contents():
    task_worker = await choose_worker()
    port = task_worker["port"]
    # Print that confirms to which worker was the task sent.
    # print(f"Working on port {port}")

    url = "http://127.0.0.1:" + port + "/read_from_file"
    # Print that confirms the final URL on which the task will be sent. Used for testing purposes.
    # print(url)
    
    async with httpx.AsyncClient() as client:
        task_worker["running"] += 1
        response = await client.get(url, timeout = 25)
        task_worker["running"] -= 1
        task_worker["total_tasks_done"] += 1
        return json.loads(response.text)

# Method for sending messages to workers, these messages need to be written into the file they colectivelly work on
async def write_message(message):
    task_worker = await choose_worker()
    port = task_worker["port"]
    # Print that confirms to which worker was the task sent.
    # print(f"Working on port {port}")

    url = "http://127.0.0.1:" + port + "/write_to_file/" + message
    # Print that confirms the final URL on which the task will be sent. Used for testing purposes.
    # print(url)
    
    async with httpx.AsyncClient() as client:
        task_worker["running"] += 1
        response = await client.get(url, timeout = 25)
        task_worker["running"] -= 1
        task_worker["total_tasks_done"] += 1
        return json.loads(response.text)



# -----------------------------------------------------------------------------------
# Routes which send different tasks to workers.

# Route which sends a message to the worker and expects the reversed message back after a certain 
# period of sleep on the workier
@app.get("/send_sleep/{message}")
async def send_work(message):
    # Print used for test purposes
    # print(f"Given message is: {message}.")
    ret_msg = await sleep_work(message)
    return ret_msg

# Route for reading the contents of the file all workers write into
@app.get("/show_file")
async def show_file():
    file_contents = await get_file_contents()
    return file_contents

# Route for sending messages to workers. These messages need to be written into the file
@app.get("/write_message/{message}")
async def send_work(message):
    # Print used for test purposes
    # print(f"Given message is: {message}.")
    ret_msg = await write_message(message)
    return ret_msg


# -----------------------------------------------------------------------------------
# Code for deciding which worker should recieve the next task.
'''
Thought process:
- in order to choose the next best worker, we need some criteria to choose by
- the best criteria  in order to choose this is the number of  currently preforming tasks
- which means that I need to count active tasks
- in order to do that, I can use the "running" field in each of the workers
- so at the start of each of the tasks, the "running" argument needs to be increased
- and at the end of each task, the "running" argument needs to be decreased

- with this in mind, the next chosen worker should be the one with the least number of running tasks
- if they all have the same number of tasks running, they should be chosen by random
'''

async def choose_worker():
    lowest_number_of_tasks = workers[0]["running"]
    lowest_running = workers[0]
    all_equal_flag = True

    for worker in workers:
        if(worker["running"] < lowest_number_of_tasks):
            lowest_number_of_tasks = worker["running"]
            lowest_running = worker
            all_equal_flag = False
        elif(worker["running"] == lowest_number_of_tasks):
            all_equal_flag = False
    
    if all_equal_flag:
        random_worker = random.choice(workers)
        return random_worker 

    print(lowest_running)
    return lowest_running