"""
Run this to see what folders exist in your kmvtechug directory.
This helps us find the correct path to the EVL1 files.
"""
import os

print("Current directory:", os.getcwd())
print()
print("Folders and files here:")
for item in sorted(os.listdir(".")):
    print(" ", item)

print()
print("Looking for education folder...")
if os.path.exists("education"):
    print("  Found: education/")
    for item in sorted(os.listdir("education")):
        print("    education/" + item)
    if os.path.exists("education/courses"):
        print()
        print("  Found: education/courses/")
        for item in sorted(os.listdir("education/courses")):
            print("    education/courses/" + item)
else:
    print("  NOT FOUND - education folder does not exist here")
    print("  Try looking in subfolders:")
    for item in os.listdir("."):
        if os.path.isdir(item):
            sub = os.listdir(item)
            if "education" in sub:
                print(f"  FOUND education inside: {item}/education")
