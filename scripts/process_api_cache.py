#!/usr/bin/python3

# Standard library imports
import hashlib
import os
import shutil

# Third party imports

# Local imports

# Globals
TARGET_DIRECTORY = 'api'
TARGET_PATH = '../src/ebay_rest/' + TARGET_DIRECTORY
SOURCE_PATH = './' + TARGET_DIRECTORY + '_cache'   # must match the TARGET_PATH in generate_api_cache.py

# Run this script from the command line to relocate and generate python code.
# Before you must run generate_api_cache.py.


class Process:
    """ The processing steps are split into bite sized methods. """
    def __init__(self):
        self.file_ebay_rest = os.path.abspath('../src/ebay_rest/ebay_rest.py')
        self.file_setup = os.path.abspath('../setup.cfg')

        self.path_cache = os.path.abspath(SOURCE_PATH)
        self.path_final = os.path.abspath(TARGET_PATH)
        self.path_ebay_rest = os.path.abspath('../src/ebay_rest')

        assert os.path.isdir(self.path_cache),\
            'Fatal error. Prior, you must run the script generate_api_cache.py.'
        for (_root, dirs, _files) in os.walk(self.path_cache):
            dirs.sort()
            self.names = dirs
            break

    def copy_libraries(self):
        """ Copy essential parts of the generated eBay libraries to within the src folder. """
        # purge what might already be there
        for filename in os.listdir(self.path_final):
            file_path = os.path.join(self.path_final, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # copy each library's directory
        for name in self.names:
            src = os.path.join(self.path_cache, name, name)
            dst = os.path.join(self.path_final, name)
            _destination = shutil.copytree(src, dst)

    def fix_imports(self):
        """ The deeper the directory, the more dots are needed to make the correct relative path. """
        for name in self.names:
            self._fix_imports_recursive(name, '..', os.path.join(self.path_final, name))

    def _fix_imports_recursive(self, name, dots, path):
        """ This does the recursive part of fix_imports. """

        for (_root, dirs, files) in os.walk(path):

            swaps = [   # order is crucial, put more specific swaps before less
                (f'import {name}.models', f'from {dots}{name} import models'),
                (f'from models', f'from {dots}{name}.models'),
                (f'import {name}', f'import {dots}{name}'),
                (f'from {name}', f'from {dots}{name}'),
                (f'{name}.models', f'models'),
            ]
            for file in files:
                target_file = os.path.join(path, file)
                new_lines = ''
                with open(target_file) as file_handle:
                    for old_line in file_handle:
                        for (original, replacement) in swaps:
                            if original in old_line:
                                old_line = old_line.replace(original, replacement)
                                break   # only the first matching swap should happen
                        new_lines += old_line
                with open(target_file, 'w') as file_handle:
                    file_handle.write(new_lines)

            dots += '.'
            for directory in dirs:
                self._fix_imports_recursive(name, dots, os.path.join(path, directory))

            break

    def merge_setup(self):
        """ Merge the essential bits of the generated setup files into the master. """

        # compile a list of all unique requirements from the generated libraries
        start_tag = 'REQUIRES = ['
        end_tag = ']\n'
        requirements = set()
        for name in self.names:
            src = os.path.join(self.path_cache, name, 'setup.py')
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
            lines.append(f'from .{TARGET_DIRECTORY} import {name}')
            lines.append(f'from .{TARGET_DIRECTORY}.{name}.rest import ApiException as {self._camel(name)}Exception')
        insert_lines = '\n'.join(lines) + '\n'
        self._put_anchored_lines(target_file=self.file_ebay_rest, anchor='er_imports', insert_lines=insert_lines)

    def get_methods(self):
        """ For all modules, get all methods. """

        # catalog the module files that contain all method implementations
        modules = []
        for name in self.names:
            path = os.path.join(self.path_cache, name, name, 'api')
            for (root, _dirs, files) in os.walk(path):
                for file in files:
                    if file != '__init__.py':
                        modules.append((name, file.replace('.py', ''), os.path.join(root, file)))

        # catalog all methods in all modules
        methods = []
        method_marker_part = '_with_http_info'
        method_marker_whole = method_marker_part + '(self,'
        docstring_marker = '"""'
        bad_docstring_markers = (
            '>>> ',
            'synchronous',
            'async_req',
            'request thread',
        )
        typo_remedy = (             # pairs of typos found in docstrings and their remedy
            ('cerate', 'create'),               # noqa: - suppress flake8 compatible linters, misspelling is intended
            ('distibuted', 'distributed'),      # noqa:
            ('http:', 'https:'),                # noqa:
            ('identfier', 'identifier'),        # noqa:
            ('Limt', 'Limit'),                  # noqa:
            ('lisitng', 'listing'),             # noqa:
            ('maketplace', 'marketplace'),      # noqa:
            ('motorcyles', 'motorcycles'),      # noqa:
            ('parmeter', 'parameter'),          # noqa:
            ('publlish', 'publish'),            # noqa:
        )
        for (name, module, path) in modules:
            step = 0
            with open(path) as file_handle:
                for line in file_handle:

                    if step == 0:   # looking for the next method
                        if method_marker_whole in line:
                            (method_and_params, _junk) = line.split(')')
                            (method, params) = method_and_params.split('(')
                            method = method.replace('    def ', '')
                            method = method.replace(method_marker_part, '')
                            params = params.replace('self, ', '')
                            step += 1

                    elif step == 1:  # looking for the start of the docstring block
                        if docstring_marker in line:
                            docstring = line
                            step += 1

                    elif step == 2:  # looking for the end of the docstring block
                        if docstring_marker not in line:
                            bad = False
                            for bad_docstring_marker in bad_docstring_markers:
                                if bad_docstring_marker in line:
                                    bad = True
                                    break
                            if not bad:
                                docstring += line
                        else:
                            docstring += line
                            for (typo, remedy) in typo_remedy:
                                docstring = docstring.replace(typo, remedy)
                            methods.append((name, module, path, method, params, docstring))
                            step = 0

        methods.sort()

        return methods

    def make_methods(self, methods):
        """ Make all the python methods and insert them where needed. """

        code = "\n"
        for method in methods:
            code += self._make_method(method)
        self._put_anchored_lines(target_file=self.file_ebay_rest, anchor='er_methods', insert_lines=code)

    def _make_method(self, method):
        """ Return the code for one python method. """

        (name, module, path, method, params, docstring) = method
        base_path = '{basePath}'
        ignore_long = '  # noqa: E501'  # flake8 compatible linters should not warn about long lines

        # Fix how the docstring expresses optional parameters then end up in **kwargs
        # catalog all parameters listed in the docstring
        docstring_params = set()
        for line in docstring.split('\n'):
            if ':param' in line:
                for word in line.split(' '):
                    if word.endswith(':'):
                        docstring_params.add(word.replace(':', ''))
                        break
        # determine if any docstring parameters are method parameters
        has_docstring_problem = False
        for docstring_param in docstring_params:
            if docstring_param not in params:
                has_docstring_problem = True
                break
        # if we found an optional parameter, then add a provision for 'optionals' aka *args in the right spot
        if has_docstring_problem:
            pass    # TODO Do something to make the comments aka docstring handle optional parameters properly

        code = f"    def {name}_{method}(self, {params}):{ignore_long}\n"
        code += docstring
        code += f"        # Configure OAuth2 access token for authorization: api_auth\n"
        code += f"        configuration = {name}.Configuration()\n"
        code += f"        configuration.access_token = self._token.get()\n"
        code += f"\n"
        code += f"        # Configure the host endpoint\n"
        code += f"        if self._use_sandbox:\n"
        code += f"            configuration.host = configuration.host.replace('api.ebay.com',\n"
        code += f"                                                            'api.sandbox.ebay.com')\n"
        code += f"        # check for host has flaws and then then compensate\n"
        code += f"        if '{base_path}' in configuration.host:\n"
        code += f"            configuration.host = configuration.host.replace('{base_path}',\n"
        code += f"                                                            '/{name.replace('_', '/')}')\n"
        code += f"            if 'developer/analytics' in configuration.host:\n"
        code += f"                configuration.host += '/v1_beta'\n"
        code += f"        else:\n"
        code += f"            logging.debug('eBay has fixed the flaw so remove the compensating code.')\n"
        code += f"\n"
        code += f"        # create an instance of the API class\n"
        code += f"        api_instance = \\\n"
        code += f"            {name}.{self._camel(module)}({name}.ApiClient(configuration))\n"
        code += f"        api_instance.api_client.default_headers['X-EBAY-C-MARKETPLACE-ID'] = self._site_id\n"
        code += f"\n"
        code += f"        result = None\n"
        code += f"        try:\n"
        code += f"            api_response = api_instance.{method}(\n"
        code += f"                {params}{ignore_long}\n"
        code += f"            )\n"
        code += f"\n"
        code += f"        except {self._camel(name)}Exception as error:\n"
        code += f"            logging.critical('APIException status ' + error.status + ' reason '\n"
        code += f"                             + error.reason + ' body ' + error.body + '.')\n"
        code += f"\n"
        code += f"        else:\n"
        code += f"            result = api_response\n"
        code += f"\n"
        code += f"        return result\n"
        code += f"\n"

        return code

    def remove_duplicates(self):
        """ Deduplicate identical .py files found in all APIs.
        for example when comments are ignored the rest.py files appear identical. """

        # build a catalog that includes a hashed file signature
        catalog = []
        for name in self.names:
            catalog.extend(self._remove_duplicates_recursive_catalog(name, os.path.join(self.path_final, name)))

        # count how many times each signature appears
        signature_tally = {}
        for (name, file, path, signature) in catalog:
            if signature in signature_tally:
                signature_tally[signature] = + 1
            else:
                signature_tally[signature] = 1

        # make a sub catalog that just includes signature repeaters
        catalog_repeaters = []
        for values in catalog:
            (name, file, path, signature) = values
            if signature_tally[signature] > 1:
                catalog_repeaters.append(values)

        # TODO apply the DRY principle to the repeaters

    def _remove_duplicates_recursive_catalog(self, name, path):
        """ This does the recursive part of cataloging for remove_duplicates. """

        catalog = []
        for (_root, dirs, files) in os.walk(path):
            for file in files:
                if file != '__init__.py' and file.endswith('.py'):
                    target_file = os.path.join(path, file)
                    with open(target_file) as file_handle:
                        code_text = file_handle.read()
                        # TODO Remove whitespace and comments from the Python code before hashing.
                        m = hashlib.sha256()
                        m.update(code_text.encode())
                        catalog.append((name, file, target_file, m.digest()))

            for directory in dirs:
                catalog.extend(self._remove_duplicates_recursive_catalog(name, os.path.join(path, directory)))

            return catalog

    @staticmethod
    def _camel(name):
        """ Convert a name with underscore separators to camel case. """
        camel = ''
        for part in name.split('_'):
            camel += part.capitalize()
        return camel

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

    # Refrain from altering the sequence of the method calls because there may be dependencies.
    p = Process()
    p.copy_libraries()
    p.fix_imports()
    p.merge_setup()
    p.make_includes()
    # p.remove_duplicates()     # uncomment the method call when work on the method resumes
    p.make_methods(p.get_methods())


if __name__ == "__main__":
    main()
