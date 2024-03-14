import subprocess

# Define the command as you would use it in the shell
command = ["python", "-m", "uvicorn", "worker:app", "--reload", "--port", "8001"]

# Run the command
subprocess.run(command)