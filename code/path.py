import sys
import os.path

path = input("Enter the path of the file or directory to add to PATH: ")
full_path = os.path.realpath(path)
sys.path.insert(0, full_path)
print(f"Added to PATH: {full_path}")