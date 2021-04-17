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
    """ The processing steps are split into bite sized methods. """
    def __init__(self):
        self.file_ebay_rest = os.path.abspath('../src/ebay_rest/ebay_rest.py')
        self.file_setup = os.path.abspath('../setup.cfg')

        self.path_api_cache = os.path.abspath('./api_cache')
        self.path_api_final = os.path.abspath('../src/ebay_rest/api')
        self.path_ebay_rest = os.path.abspath('../src/ebay_rest')

        assert os.path.isdir(self.path_api_cache), 'Fatal error. Prior, you must run the script generate_api_cache.py.'
        for (_root, dirs, _files) in os.walk(self.path_api_cache):
            dirs.sort()
            self.names = dirs
            break

    def copy_api_libraries(self):
        """ Copy essential parts of the generated eBay libraries to within the src folder. """
        # purge what might already be there
        if os.path.isdir(self.path_api_final):
            shutil.rmtree(self.path_api_final)

        # create or re-create the directory where libraries will be stored
        os.mkdir(self.path_api_final)

        # copy each library's directory
        for name in self.names:
            src = os.path.join(self.path_api_cache, name, name)
            dst = os.path.join(self.path_api_final, name)
            _destination = shutil.copytree(src, dst)

        # put a programmer friendly warning
        dst = os.path.join(self.path_api_final, 'README.md')
        with open(dst, "w") as file:
            file.write("# Read Me\n")
            file.write("Refrain from altering the directory contents.\n")
            file.write("The script process_api_cache.py generates contents.")

    def merge_toml(self):
        """ Merge the essential bits of the generated toml files into the master. """
        pass    # TODO

    def merge_setup(self):
        """ Merge the essential bits of the generated setup files into the master. """

        # compile a list of all unique requirements from the generated libraries
        start_tag = 'REQUIRES = ['
        end_tag = ']\n'
        requirements = set()
        for name in self.names:
            src = os.path.join(self.path_api_cache, name, 'setup.py')
            with open(src) as file:
                for line in file:
                    if line.startswith(start_tag):
                        line = line.replace(start_tag, '')
                        line = line.replace(end_tag, '')
                        parts = line.split(', ')
                        for part in parts:
                            requirements.add(part)
                        break
        requirements = list(requirements)
        requirements.sort()

        # include these with the other requirements for our package
        insert_lines = ''
        for requirement in requirements:
            insert_lines += f'    {requirement}\n'
        self._put_anchored_lines(target_file=self.file_setup, anchor='setup.cfg', insert_lines=insert_lines)

    def make_includes(self):
        """ Make includes for all the libraries. """

        lines = []
        for name in self.names:
            lines.append(f'import api.{name}')
            lines.append(f'from api.{name}.rest import ApiException')
        insert_lines = '\n'.join(lines) + '\n'
        self._put_anchored_lines(target_file=self.file_ebay_rest, anchor='er_imports', insert_lines=insert_lines)

    @staticmethod
    def _put_anchored_lines(target_file, anchor, insert_lines):
        """ In the file replace what is between anchors with new lines of code. """

        if os.path.isfile(target_file):
            new_lines = ''
            start = f"ANCHOR-{anchor}-START"
            end = f"ANCHOR-{anchor}-END"
            start_found = False
            end_found = False

            with open(target_file) as file:
                for old_line in file:
                    if not start_found:
                        new_lines += old_line
                        if start in old_line:
                            start_found = True
                            new_lines += insert_lines
                    elif start_found and not end_found:
                        if end in old_line:
                            end_found = True
                            new_lines += old_line
                    else:
                        new_lines += old_line

            if start_found and end_found:
                with open(target_file, 'w') as file:
                    file.write(new_lines)

            else:
                print(f"Can't find proper start or end anchors for {anchor} in {target_file}.")
        else:
            print(f"Can't find {target_file}")


def main():

    # TODO uncomment all methods calls when finished debugging.

    # Refrain from altering the sequence of the method calls because there may be dependencies.
    p = Process()
    # p.copy_api_libraries()
    p.merge_toml()
    # p.merge_setup()
    # p.make_includes()


if __name__ == "__main__":
    main()
