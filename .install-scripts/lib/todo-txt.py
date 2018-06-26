#!/usr/bin/python3

""" todotxt-cli addon installer
USAGE:
    todo-txt.py [addon SOURCE file]

USAGE NOTES:
    Expects two parameters
    - one text file defining the scripts to be installed, their source and
    the retrieval method (see below)
    - the full path to the todo-txt extensions dir (typically
    ~/.todo.actions.d)

    The text file should be formatted as follows:
    [addon1[,addon2,...]]=[wget|git];[retrieval url](;[target directory within
    .todo.actions.d])
    - if wget is passed as the retrieval parameter, the retrieval url must be
    a raw githubusercontent url to the directory containing all the addons,
    addon1, addon2 etc
    - if git is passed as the retrieval parameter, the retrieval url must be
    a valid clone target. The repository must contain the addon script in its
    root directory.
    - the 3rd parameter is optional. If passed, the script will be installed
    into this directory within .todo.actions.d. This parameter is not valid
    for git retrievals.
    - only one addon script per line can be defined for git retrievals

    For example
    - wget example
    birdseye,birdseye.py=wget;https://raw.githubusercontent.com/todotxt/todo.txt-cli/addons/.todo.actions.d
    - wget example with optional target directory. The futureTasks script will
    be installed into .todo.actions.d/filters
    futureTasks=wget;https://raw.githubusercontent.com/FND/todo.txt-cli/extensions;filters
    - git example
    hiding=git;https://github.com/klausweiss/todo.txt-hiding.git

    Results:
    - wgets all the wget scripts, **overwriting** any existing files
    - git checkouts all the git retrievals, where the git repository doers not
    already exist
    - if the git repository already exists, git pulls to refresh the files
"""

import os,re,sys
from abc import ABC, abstractmethod
from colorama import Fore, init, Style
from subprocess import run, PIPE

def usage():
    print("USAGE:  %s [SOURCE] [extensions directory]" % (sys.argv[0], ))

def main(argv):
    # make sure we have all our args
    if len(argv) < 3:
        usage()
        sys.exit(2)

    init()
    reader = source_reader(argv[1], argv[2])
    if reader.fetch():
        exit(0)
    else:
        exit(1)

def printe_and_exit(msg):
    printe(msg)
    exit(1)

def printe(msg):
    print(Fore.RED + msg + Style.RESET_ALL, file=sys.stderr)

class SourceDefsError(TypeError): pass

class source_reader(object):
    def __init__(self, file, exts_dir):
        self._file = file
        self._exts_dir = exts_dir
        self._getters = []
        self._factory = getter_factory()
        self._fetch_errors = []

    def _read(self):
        try:
            f = open(self._file, "r")
            for line in f:
                getter = self._factory.create_getter(line.rstrip(),
                                                     self._exts_dir)
                self._getters.append(getter)
        except IOError as ioe:
            printe_and_exit(f"ERROR: {self._file} could not be read: {ioe}.")

    def fetch(self):
        self._read()
        success = True
        for getter in self._getters:
            if getter.check():
                self._fetch_errors += getter.fetch()
            else:
                success = False

        if self._fetch_errors:
            printe("The following commands failed:\n\n%s"% "\n".join(self._fetch_errors))

        return success

class getter_factory(object):

    def create_getter(self, line, exts_dir):
        if wget_getter._regex.match(line):
            return wget_getter(line, exts_dir)
        elif git_getter._regex.match(line):
            return git_getter(line, exts_dir)
        else:
            return error_getter(line)

class getter(ABC):
    def __init__(self, line):
        self._line = line

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def match(line):
        pass

class cmd_getter(getter):
    _regex = re.compile("^[^.]$") # define a regex that doesn't match anything
                                  # This should be overriden by subclasses.

    def __init__(self, line, dest_dir, working_dir=None):
        self._errors = []
        self._cmds = {}
        self._working_dir = working_dir
        self._dest_dir = dest_dir
        super().__init__(line)

    def fetch(self):
        for script in self._cmds.keys():
            cmd_arr = self._cmds[script]
            print("Fetching script '%s'..."% script, end='')
            result = run(cmd_arr,
                         stdout=PIPE,
                         stderr=PIPE,
                         encoding='utf-8',
                         cwd = self._working_dir)

            # Check for returncode of 0
            if not result.returncode:
                print(Fore.GREEN + "DONE" + Style.RESET_ALL)
                self._make_executable(script)
            else:
                print(Fore.RED + "FAIL" + Style.RESET_ALL)
                cmd = " ".join(cmd_arr)
                self._errors.append("%s : %s"% (cmd, result.stderr))

        return self._errors

    def _make_executable(self, script):
        os.chmod(f"{self._dest_dir}/{script}", 0o775)

    def match(self, line):
        if _regex.match(line):
            return True
        else:
            return False

class wget_getter(cmd_getter):
    _regex = re.compile('^([^=]+)=wget;([^;]+)(?:;([^;]+))?$')

    def __init__(self, line, exts_dir):
        (scripts_csv, url, opt_dir) = self._regex.match(line).groups()
        dest_dir = f"{exts_dir}/{opt_dir}" if opt_dir else f"{exts_dir}"
        self._mkdir = opt_dir
        self._scripts = scripts_csv.split(",")
        self._url = url
        super().__init__(line, dest_dir)

    def check(self):
        ok_to_proceed = True
        if self._mkdir:
            try:
                os.makedirs(self._dest_dir, mode=0o775, exist_ok=True)
            except OSError as ose:
                printe(f"Could not create {exts_dir}/{opt_dir}: {ose}")
                ok_to_proceed = False

        if ok_to_proceed:
            for script in self._scripts:
                cmd = f"wget {self._url}/{script} -O {self._dest_dir}/{script}"
                self._cmds[script] = cmd.split()

        return ok_to_proceed

class git_getter(cmd_getter):
    _regex = re.compile('^([^=,]+)=git;([^;]+)$')

    def __init__(self, line, exts_dir):
        (self._script, self._url) = self._regex.match(line).groups()
        self._repo = f"{exts_dir}/{self._script}"
        super().__init__(line, self._repo)

    def check(self):
        if self._repo_exists():
            cmd = f"git pull {self._repo}"
            self._working_dir = self._repo
        else:
            cmd = f"git clone {self._url} {self._repo}"

        self._cmds[self._script] = cmd.split()
        return True

    def _repo_exists(self):
        return os.path.exists(f"{self._repo}/.git/config")

class error_getter(getter):
    def check(self):
        printe(f"BAD LINE: {self._line}")
        return False

    def fetch(self):
        pass

    def match(self):
        pass

if __name__ == "__main__":
    main(sys.argv)
