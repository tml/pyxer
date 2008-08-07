# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

import pyxer.utils.jsonhelper
import os
import os.path
import sys
import types
import logging
log = logging.getLogger(__file__)

try:
    import subprocess
except:
    subprocess = None

iswin = (sys.platform=="win32")

class Dict(dict):

    def __getattr__(self, name):
        try:
            return dict.__getattr__(self, name)
        except:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value

def html_escape(value):
    return (value
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace('<', "&lt;")
        .replace('>', "&gt;"))

def html_unescape(value):
    return (value
        .replace("&quot;", '"')
        .replace("&lt;", '<')
        .replace("&gt;", '>')
        .replace("&amp;", '&'))

def system(cmd):
    cmd = cmd.strip()
    print "Command:", cmd
    return os.system(cmd)

def find_root(*path):
    cwd = os.getcwd()
    if path:
        cwd = os.path.join(cwd, *path)
    while cwd:
        if os.path.isfile(os.path.join(cwd, "app.yaml")):
            log.debug("Projects root directory is %r", cwd)
            return cwd
        cwd, last = os.path.split(cwd)
        if not last:
            break
    log.warn("Projects root directory could not be found")
    return None

def find_name(root=None):
    if not root:
        root = find_root()
    for name in os.listdir(os.path.join(root, "src")):
        if not name.startswith("."):
            return name
    return None

def call_subprocess(
    command,
    show_stdout=True,
    filter_stdout=None,
    cwd=None,
    raise_on_returncode=True,
    extra_env=None):

    if type(command) not  in (types.ListType, types.TupleType):
        raise Exception("List or tuple expected")

    cmd = []
    for part in command:
        if ' ' in part or '\n' in part or '"' in part or "'" in part:
            part = '"%s"' % part.replace('"', '\\"')
        if part:
            cmd.append(part)
    cmd_desc = ' '.join(command)
    if show_stdout:
        stdout = None
    else:
        stdout = subprocess.PIPE
    print ("Running command %s" % cmd_desc)
    if extra_env:
        env = os.environ.copy()
        env.update(extra_env)
    else:
        env = None
    try:
        proc = subprocess.Popen(
            cmd,
            stderr=subprocess.STDOUT,
            stdin=None,
            stdout=stdout,
            # shell = True,
            cwd=cwd,
            env=env)
    except Exception, e:
        print (
            "Error %s while executing command %s" % (e, cmd_desc))
        raise
    all_output = []
    if stdout is not None:
        stdout = proc.stdout
        while 1:
            line = stdout.readline()
            if not line:
                break
            line = line.rstrip()
            all_output.append(line)
            if filter_stdout:
                level = filter_stdout(line)
                if isinstance(level, tuple):
                    level, line = level
                print (level, line)
            else:
                print (line)
    else:
        proc.communicate()
    proc.wait()
    if proc.returncode:
        if raise_on_returncode:
            if all_output:
                print ('Complete output from command %s:' % cmd_desc)
                print ('\n'.join(all_output) + '\n----------------------------------------')
            raise OSError(
                "Command %s failed with error code %s"
                % (cmd_desc, proc.returncode))
        else:
            print (
                "Command %s had error code %s"
                % (cmd_desc, proc.returncode))
    #for k, v in env.items():
    #    print k,v
    if env:
        os.environ = env

def call_virtual(cmd, root=None, cwd=None):
    if not root:
        root = find_root()
    print "Init virtualenv", root
    if iswin:
        call_subprocess(cmd, extra_env={
            "VIRTUAL_ENV": root,
            "PATH": os.path.join(root, "Scripts") + ";" + os.environ.get("PATH"),
            }, cwd=cwd)
    else:
        call_subprocess(cmd, extra_env={
            "VIRTUAL_ENV": root,
            "PATH": os.path.join(root, "bin") + ";" + os.environ.get("PATH"),
            }, cwd=cwd)

def call_script(cmd, root=None, cwd=None):
    if not root:
        root = find_root()
    if iswin:
        cmd[0] = os.path.join(root, "Scripts", cmd[0] + ".exe")
    else:
        cmd[0] = os.path.join(root, "bin", cmd[0])

    #if cwd is not None:
    #    _cwd = os.getcwd()
    #    os.chdir(cwd)
    #try:

    call_virtual(cmd, root, cwd=cwd)

    #finally:
        #if cwd is not None:
        #    os.chdir(_cwd)

call_bin = call_script

