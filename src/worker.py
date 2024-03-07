import fastapi, time, httpx, sys, json, os

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
        response = await client.get("http://127.0.0.1:8000/register_worker/" + str(port))
        return json.loads(response.text)
@app.on_event("startup")
async def open_write_file():
    # This part of code will prepare the file for work
    if not os.path.exists(write_file_name):
        with open(write_file_name, 'w') as write_file:
            #write_file.write(f"Log file created on {datetime.now()}\n")
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

# Part of code that will be the "core" of the worker.
# Messages given from the user to the balancer will be forwarded to the worker, where they will be
# written into the file. The data from this code can also be read out.
# These operations take some time, just enough for the simulation of the system's work.
# All workers will write into the same file, simulating a system communicating with a database.
@app.get("/write_to_file/{message}")
def write_to_file(message):
    write_file_name_start_lenght = len(write_file_name)
    message_to_write = message + "\n"
    with open(write_file_name, "a") as file:
            file.write(message_to_write)
    if(len(write_file_name) > write_file_name_start_lenght):
        return "The message has been written into the file."
    else:
        return "An error ocurred while writing into file."

@app.get("/read_from_file")
def read_from_file():
    with open(write_file_name, "r") as file:
        lines = file.readlines()
    return lines
    
