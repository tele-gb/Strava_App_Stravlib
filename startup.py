import subprocess

# Step 1: Create a virtual environment
subprocess.run(['python', '-m', 'venv', 'myenv'])

# # Step 2: Set the virtual environment as active
# if subprocess.call('source myenv/Scripts/activate', shell=True) != 0:
#     raise Exception('Failed to activate the virtual environment')

# # Step 3: Install requirements
# subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

# # Step 4: Run a Python script to initialize the web app
# subprocess.run(['python', 'basic_flask.py'])