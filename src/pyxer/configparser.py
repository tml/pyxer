# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 103 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:08:54 +0100 (Mi, 31 Okt 2007) $"

import string
import fnmatch
import sys
import re
import os.path

re_args = re.compile("--([^-]*)-([^=]*)=(.*)")

def cBOOL(v):
    if type(v)==type(""):
        return v.lower().strip() in ("yes", "true", "on", "1")
    return not not v

def cSTRING(v):
    return unicode(v, "utf8")

def cINT(v, min=None, max=None):
    v = long(v)
    if min!=None:
        if v<min:
            raise Exception, "'%d' is smaller than '%d'" % (v, min)
    if max!=None:
        if v>max:
            raise Exception, "'%d' is bigger than '%d'" % (v, max)
    return v

def cPATH(v):
    if not v:
        return ""
    p = os.path.abspath(str(v))
##    if not os.path.exists(p):
##        raise Exception, "path '%s' does not exist" % p
##    if not os.path.isdir(p):
##        raise Exception, "'%s' is not a directory" % p
    return p

def cFILE(v):
    if not v:
        return ""
    p = os.path.abspath(str(v))
##    if not os.path.exists(p):
##        raise Exception, "file '%s' does not exist" % p
##    if not os.path.isfile(p):
##        raise Exception, "'%s' is not a file" % p
    return p

def cSELECT(v, l=[""]):
    if not v:
        return None
    if v.lower() in l:
        return l
    raise Exception, "'%s' not in %s" % (v, str(l))

class Config:

    def __init__(self, cfgdesc={}):
        self.set_description(cfgdesc)

    __code = "CONFIGURATION FILE"

    def empty(self):
        self.cfg = {}
        self.get = self.cfg.get

    def remove(self, name):
        if not name in self.cfgdesc.keys():
            if self.cfg.has_key(name):
                del self.cfg[name]
            if self.cfgorg.has_key(name):
                del self.cfgorg[name]

    def remove_section(self, name):
        for k in self.options(name).keys():
            self.remove(name + "." + k)

    def set(self, name, value):
        desc = None

        if self.cfgdesc.has_key(name):
            desc = self.cfgdesc[name]

        # search for patterns
        else:
            for mp in self.cfgdesc.keys():
                if fnmatch.fnmatch(name, mp):
                    desc = self.cfgdesc[mp]

        # adjust
        if desc:
            if len(desc)>2:

                # workaround python 152
                value = eval("%s(%s,%s)" % (desc[0].__name__, repr(value), string.join(map(repr, desc[2:]),",")))
                # und apply?

                # value = desc[0](value, *desc[2:])
            else:
                value = desc[0](value)

        self.cfgorg[name] = value
        self.cfg[name] = value

    #def get(self, name):
    #    return self.cfg.get(name, None)

    def set_description(self, cfgdesc):
        self.cfgdesc = cfgdesc
        self.cfgorg = {}
        self.empty()

        # sections with patterns
        self.patsecs = filter(lambda x: "*" in x, self.__sections(self.cfgdesc))

        # set default hash
        for k, v in self.cfgdesc.items():
            if not ("*" in k):
                self.cfg[k] = v[0](v[1])

    def get_description(self):
        return self.cfgdesc

    def read(self, file, password=""):

        """
        reads a config file. the first parameter may be a filehandle
        or a filename. the second parameter is a hash with entry names
        as keys and the values are a 2-tuple with first the function name
        of the converter and second the default value. returns a hash
        with section and option name separated by a point and the value.
        """

        # self.empty()

        # defaults
        sec = ""
        ln  = 0

        # open file if needed
        nf = 0
        if type(file)==type(""):
            nf = 1
            try:
                f = open(file, "r")
            except:
                return 0
        else:
            f = file

        while 1:

            l = f.readline()
            ln = ln + 1

            if not l: break

            try:

                l = string.lstrip(l)
                if l:

                    # section
                    if l[0] == "[":
                        p = string.find(l, "]")
                        if p>0:
                            sec = string.lower(string.strip(l[1:p]))

                            # pattern
                            for mp in self.patsecs:
                                if fnmatch.fnmatch(sec, mp):
                                    for k, v in self.__options(self.cfgdesc, mp).items():
                                        self.cfg[sec+"."+k] = v[0](v[1])


                    # option
                    elif l[0] in "abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        p = string.find(l, "=")
                        if p>0:
                            name = sec + "." + string.lower(string.strip(l[:p]))
                            value = string.lstrip(l[p+1:])
                            if value and (value[0] in ('"',"'")):
                                value = string.rstrip(value[1:])
                                if value[-1] in ("'", '"'):
                                    value = value[:-1]
                            else:
                                value = string.rstrip(value)

                            self.set(name, value)

            finally: pass
#            except Exception, e:
#                raise Exception, "Error in line %d (%s): %s" % (ln, name, str(e))

        if nf:
            f.close()

        return self.cfg

    #def __encrypt(self, s, password):
    #    return self.__code + "\r\n" + base64.encodestring(rotor.newrotor(password).encrypt(zlib.compress(s)))

    #def __decrypt(self, password):
    #    pass

    def write(self, file, orig=None, password=""):
        import cStringIO
        f = cStringIO.StringIO()

        if orig==None:
            keys = self.cfgorg.keys()
            keys.sort()
            sec = ""
            for k in keys:
                nsec, opt = string.split(k, ".")
                if sec!=nsec:
                    if sec:
                        f.write("\r\n")
                    f.write("[%s]\r\n" % nsec)
                    sec = nsec
                v = str(self.cfgorg[k])
                if not v: v = ""
                delim = ""
                #if " " in  v:
                #    delim = '"'
                f.write('%-16s = %s%s%s\r\n' % (opt, delim, v, delim))

        # open file if needed
        s = f.getvalue()

        #if password:
        #    s = self.__encrypt(s, password)

        if type(file)==type(""):
            open(file, "w").write(s)
        else:
            file.write(s)

    def __sections(self, cfg, pat=None):
        """
        list all sections. may be reduced by a fnmathc pattern.
        """
        import fnmatch
        l = []
        for k in cfg.keys():
            s = string.split(k,".")[0]
            if not (s in l):
                if pat:
                    if fnmatch.fnmatch(s, pat):
                        l.append(s)
                    continue
                l.append(s)
        return l

    def __options(self, cfg, sec):
        h = {}
        for k,v in cfg.items():
            s, o = string.split(k,".")[0:2]
            if s==sec:
                h[o] = v
        return h

    def sections(self, pattern=None):
        return self.__sections(self.cfg, pattern)

    def options(self, section):
        return self.__options(self.cfg, section)

    def allkeys(self):
        """
        alle sections und options
        """
        aux = self.cfgdesc.keys()
        aux.sort()
        return aux

    def parse_args(self, args=sys.argv):
        """
        kommandozeilen argumente auslesen und in die konfiguration
        einbinden. aus "x.y" müsste dann in der kommandozeile
        "--x-y=" werden.
        XXX Werte in Anführungszeichen werden noch nicht richtig interpretiert.
        XXX lower und strip fehlen
        """
        for a in args[1:]:
            #print a
            m = re_args.match(a)
            #print m
            if m:
                name  = m.group(1)+"."+m.group(2)
                value = m.group(3)
                #print name, value
                self.set(name, value)

    def dump(self):
        self.write(sys.stdout)

##########################################

if __name__=="__main__":

    testdata = """

[ HTtpd]

a       =
bBD     =  fsd
c       = "jhk"
num     = 33

port = 234
port2 = 123

    [exe]


# demo

[site1]

start=0

[site2]

    """

    _ConfigDefault = {
        "database.dbms":            (cSTRING, "mysql"),
        "database.name":            (cSTRING, ""),
        "database.user":            (cSTRING, "root"),
        "database.password":        (cSTRING, ""),
        "database.host":            (cSTRING, "127.0.0.1"),
        "database.port":            (cINT,3306, 0, 65536),
        "database.socket":          (cSTRING, ""),

        "server.document_path":     (cPATH, None),
        "server.gzip":              (cBOOL, 0),

        "mysql.start":              (cBOOL, 0),
        "mysql.stop":               (cBOOL, 1),
        "mysql.exe":                (cFILE, ""),
        "mysql.args":               (cSTRING, "--basedir=mysql --datadir=mysql\data --language=mysql\share\english --standalone --skip-innodb"),

        "httpd.host":               (cSTRING, "127.0.0.1"),
        "httpd.port":               (cINT, 80, 1, 65536),

        "kiosk.start":              (cBOOL, 0),
        "kiosk.exe":                (cFILE, ""),
        "kiosk.width":              (cINT, 800),
        "kiosk.height":             (cINT, 600),
        "kiosk.color":              (cSTRING, "000000"),
        "kiosk.url":                (cSTRING, "/index.html"),

        "site*.name":               (cSTRING, ""),
        "site*.start":              (cBOOL, 1)
        }

    import StringIO
    import pprint
    import sys

    c = Config(_ConfigDefault)
    c.read(StringIO.StringIO(testdata))
    c.parse_args()
    pprint.pprint(c.cfg)
    c.write(sys.stdout)
    print c.sections()
    print c.options("kiosk")
    print c.options("httpd")

    for s in c.sections("site*"):
        print c.options(s)

#    WriteConfigFile("c:\\tmp\\test.ini", c)
##    c = ReadConfigFile("c:\\tmp\\test.ini", _ConfigDefault)
##    pprint.pprint(c)
