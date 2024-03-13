import fastapi, time, httpx, sys, json, os, subprocess, asyncio

app = fastapi.FastAPI()
write_file_name = "./write_file.txt"


# Startup event that contacts the balancer and registers the worker, with the port it is running on
@app.on_event("startup")
async def contact_server():
    async with httpx.AsyncClient() as client:
        if "--port" in sys.argv:
            index = sys.argv.index("--port")
            port = int(sys.argv[index + 1])
        print(port)
        print("Registered on the balancer")
        response = await client.get("http://127.0.0.1:8000/register_worker/" + str(port))
        
        # ###newly added
        task = asyncio.create_task(is_balancer_online())
        return json.loads(response.text)
        return 200

    
# Startup event that checks if the file for writing exists, and creates it if it doesn't
@app.on_event("startup")
async def open_write_file():
    if not os.path.exists(write_file_name):
        with open(write_file_name, 'w') as write_file:
            print(f"File {write_file_name} created.")

# Route confirming that the worker is still available
@app.get("/check_in")
def check_in():
    return "This worker is still available."

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


'''
Part of code that will be the "core" of the worker.
Messages given from the user to the balancer will be forwarded to the worker, where they will be
written into the file. The data from this code can also be read out.
These operations take some time, just enough for the simulation of the system's work.
All workers will write into the same file, simulating a system communicating with a database.
'''
# Part of code that writes to file
@app.get("/write_to_file/{message}")
async def write_to_file(message):
    # Establishing the number of lines in the file, so that writing into the file can be confirmed.
    with open(write_file_name, "r") as file:
        lines = file.readlines()
        write_file_name_start_lenght = len(lines)

    # Adding a line break to the end of the message so that messages can be separated from each other.
    message_to_write = message + "\n"

    # Writing the message into the file
    with open(write_file_name, "a") as file:
            file.write(message_to_write)
    
    # Checking the current number of lines in the file.
    with open(write_file_name, "r") as file:
        lines = file.readlines()
        write_file_name_end_lenght = len(lines)

    # Checking if the message was added and returning an apropriate reply.
    if(write_file_name_end_lenght > write_file_name_start_lenght):
        return "The message has been written into the file."
    else:
        return "An error ocurred while writing into file."

# Part of code that reads from file
@app.get("/read_from_file")
def read_from_file():
    with open(write_file_name, "r") as file:
        lines = file.readlines()
    return lines



#### TO DELETE
# This code checks if the balancer is still available.
# The code starts after the worker registers with the load balancer and every minute after that, the worker checks if the balancer is still available.
# If the balancer is not available, the worker will try to start the balancer back up, thus giving it a failover
# In order to prevent multiple balancers being booted up on the same port, only the worker with the lowest port will preform the boot up.
balancer_registered_workers = []

async def is_balancer_online():
    # In order to know which worker should reboot the balancer, should it stop working
    # the list of all workers which were registered on the balaancer
    global balancer_registered_workers
    updated_worker_list = []

    # Task that periodically checks if the balancer is still online
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:8000/balancer_working", timeout = 25)
                print(response.json())
                updated_worker_list = response.json()

        except httpx.ReadTimeout:
            print(f"The balancer didn't reply, attempting to reboot.")
            command = ["python", "-m", "uvicorn", "balancer:app", "--reload", "--port", "8000"]

            # Run the command
            subprocess.run(command)
            asyncio.sleep(5)
            contact_server()
            continue
            
        except httpx.ConnectError:
            print(f"The balancer didn't reply, attempting to reboot.")
            command = ["python", "-m", "uvicorn", "balancer:app", "--reload", "--port", "8000"]

            # Run the command
            subprocess.run(command)
            asyncio.sleep(5)
            contact_server()
            continue
        
        balancer_registered_workers = updated_worker_list
        print(balancer_registered_workers)
        await asyncio.sleep(60)