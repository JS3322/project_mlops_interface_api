#!/bin/csh

set execute_pyfile_name = 'main_v0.0.1'

# check the current directory
set current_dir = `pwd`
echo "current directory: $current_dir"

# Install Python virtual environment (create it if the venv directory does not exist)
if (! -d "$current_dir/venv") then
    echo "creating virtual environment."
    python -m venv "$current_dir/venv"
endif

# Activate the virtual environment
source "$current_dir/venv/bin/activate.csh"
echo "virtual environment activated."

# Check if requirements.txt exists and install the libraries
if (-f "$current_dir/requirements.txt") then
    echo "installing libraries from requirements.txt."
    pip install -r "$current_dir/requirements.txt"
else
    echo "requirements.txt file not found."
endif

# Run main_v2.py (Python logs will be output to the terminal)
if (-f "$current_dir/main_v2.py") then
    echo "running main_v2.py."
    python "$current_dir/$execute_pyfile_name.py"
else
    echo "$execute_pyfile_name.py file not found."
endif

# Deactivate the virtual environment
deactivate