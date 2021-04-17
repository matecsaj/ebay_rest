#!/usr/bin/python3

# Standard library imports
import os
import shutil

# Third party imports

# Local imports

# Globals

# Run this script from the command line to relocate and generate python code.
# Before you must run generate_api_cache.py.


class Process:
    def __init__(self):
        self.path_api_cache = os.path.abspath('./api_cache')
        self.path_ebay_rest = os.path.abspath('../src/ebay_rest')
        self.file_ebay_rest = os.path.abspath('../src/ebay_rest/ebay_rest.py')
        self.path_api_final = os.path.abspath('../src/ebay_rest/api')
        assert os.path.isdir(self.path_api_cache), 'Fatal error. Prior, you must run the script generate_api_cache.py.'
        for (root, dirs, files) in os.walk(self.path_api_cache):
            self.names = dirs
            break

    def copy_api_libraries(self):
        # purge what might already be there
        if os.path.isdir(self.path_api_final):
            shutil.rmtree(self.path_api_final)

        # create or re-create the directory where libraries will be stored
        os.mkdir(self.path_api_final)

        # copy each library's directory
        for name in self.names:
            src = os.path.join(self.path_api_cache, name, name)
            dst = os.path.join(self.path_api_final, name)
            destination = shutil.copytree(src, dst)

        # put a programmer friendly warning
        dst = os.path.join(self.path_api_final, 'README.md')
        with open(dst, "w") as file:
            file.write("# Read Me\n")
            file.write("Refrain from altering the directory contents.\n")
            file.write("The script process_api_cache.py generates contents.")


def main():
    p = Process()
    p.copy_api_libraries()

    return


if __name__ == "__main__":
    main()
