import fastapi, httpx, json, asyncio, random, sys, subprocess

app = fastapi.FastAPI()

# List of all available workers
workers = []
port = 0

# Startup tasks
@app.on_event("startup")
async def start_periodic_task():
    global workers
    global port

    # Empty the list of a vailable workers
    workers = []
    
    # Depending on the port on which the balancer is running, a different continual task will be started
    port = port_check()
    # Continual task that check if the workers in the list are still available
    if port == 8000:
        task = asyncio.create_task(is_worker_available())
    # Continual task that check if the the main balancer is still available
    elif port == 7999:
        task = asyncio.create_task(check_on_main())
        ...


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
async def sleep_work(message):
    task_worker = await choose_worker()
    port = task_worker["port"]
    print(f"Working on port {port}")
    
    url = "http://127.0.0.1:" + port + "/do_work/" + message
    print(url)
    async with httpx.AsyncClient() as client:
        task_worker["running"] += 1
        response = await client.get(url, timeout = 25)
        task_worker["running"] -= 1
        task_worker["total_tasks_done"] += 1
        return json.loads(response.text)

# Method which requests the contents of the file from the workers
async def get_file_contents():
    task_worker = await choose_worker()
    port = task_worker["port"]
    print(f"Working on port {port}")

    url = "http://127.0.0.1:" + port + "/read_from_file"
    print(url)
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
    print(f"Working on port {port}")

    url = "http://127.0.0.1:" + port + "/write_to_file/" + message
    print(url)
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
    #print(f"Given message is: {message}.")
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
    #print(f"Given message is: {message}.")
    ret_msg = await write_message(message)
    return ret_msg


# -----------------------------------------------------------------------------------
# Code for deciding which worker should recieve the next task.

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


# -------------------------------------------------------------------------------------------------------
# Code for ensuring that the balancer is always running.
# Decided upon mode of working.
# Two balancers will be running at the same time, one on the default port of 8000
# the other will be on the port 7999 and constantly checking on the main balancer.
# IF the main balancer does not reply, the secondary balancer will switch it's port to 8000
# and then try to reboot the first balancer on the port 7999

# Method for taking the port argument and printing it out
def port_check():
    if "--port" in sys.argv:
        index = sys.argv.index("--port")
        port = int(sys.argv[index + 1])
        print(port)
        return port
    
# Route for sharing the current list of available workers with the workers
# when they check if the balancer is still online
@app.get("/balancer_working")
async def balancer_working():
    global workers
    print("Backup balancer has checked in on the health of this balancer.")
    return workers

# Method that makes sure that the main balancer at port 8000 is running
async def check_on_main():
    global workers
    global port
    updated_worker_list = workers

    while True:
        print("Pinging main balancer")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:8000/balancer_working", timeout = 25)
                print(response.json())
                updated_worker_list = response.json()
        
        # WIP
        except httpx.ReadTimeout:
            print(f"The balancer didn't reply, attempting to reboot.")
            command = ["python", "-m", "uvicorn", "balancer:app", "--reload", "--port", "8000"]

            subprocess.run(command)

            continue
                
        except httpx.ConnectError:
            print(f"The balancer didn't reply, attempting to reboot.")
            command = ["python", "-m", "uvicorn", "balancer:app", "--reload", "--port", "8000"]

            subprocess.run(command)
            continue

        workers = updated_worker_list
        print(workers)
        await asyncio.sleep(60)
    ...