import os.path, string, posix, pyvms
#
#

IDIR = ['swig_root:[source.swig]', 'swig_root:[source.doh.include]',
        'swig_root:[source.include]', 'swig_root:[source.preprocessor]'] 

def new_file(fg, dirname):
    global IDIR
    fn = 'swig_root:[vms.scripts]compil_' + os.path.basename(dirname) + '.com'
    print >> fg, '$ @' + fn
    f = open(fn, 'w')
    print >> f, '$!'
    print >> f, '$! Generated by genbuild.py'
    print >> f, '$!'
    print >> f, '$ libname = "swig_root:[vms.o_alpha]swig.olb"'
    print >> f, '$'
    print >> f, '$ set default', pyvms.crtl_to_vms(dirname)[0][0]
    print >> f, '$'
    print >> f, "$ idir := ", IDIR[0]
    for i in range(1, len(IDIR)):
        print >> f, '$ idir = idir + ",' + IDIR[i] + '"'
    print >> f, '$'
    print >> f, "$ iflags = \"/include=(''idir', sys$disk:[])\""
    print >> f, '$ oflags = \"/object=swig_root:[vms.o_alpha]'
    print >> f, "$ cflags = \"''oflags'''iflags'''dflags'\""
    print >> f, "$ cxxflags = \"''oflags'''iflags'''dflags'\""
    print >> f, '$'
    return f


def end_file(f):
    print >>f,"""$ exit
$!
$!
$MAKE: SUBROUTINE   !SUBROUTINE TO CHECK DEPENDENCIES
$ V = 'F$Verify(0)
$! P1 = What we are trying to make
$! P2 = Command to make it
$! P3 = Source file
$! P4 - P8  What it depends on
$
$ modname = f$parse(p3,,,"name")
$ set noon
$ set message/nofacility/noident/noseverity/notext
$ libr/lis=swig_root:[vms]swiglib.tmp/full/width=132/only='modname' 'libname'
$ set message/facility/ident/severity/text
$ on error then exit
$ open/read swigtmp swig_root:[vms]swiglib.tmp
$! skip header
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$ read swigtmp r
$!
$
$ read/end=module_not_found swigtmp r
$ modfound = 1
$ Time = f$cvtime(f$extract(49, 20, r))
$ goto end_search_module
$ module_not_found:
$ modfound = 0
$
$ end_search_module:
$ close swigtmp
$ delete swig_root:[vms]swiglib.tmp;*
$
$ if modfound .eq. 0 then $ goto Makeit
$
$! Time = F$CvTime(F$File(P1,"RDT"))
$arg=3
$Loop:
$       Argument = P'arg
$       If Argument .Eqs. "" Then Goto Exit
$       El=0
$Loop2:
$       File = F$Element(El," ",Argument)
$       If File .Eqs. " " Then Goto Endl
$       AFile = ""
$Loop3:
$       OFile = AFile
$       AFile = F$Search(File)
$       If AFile .Eqs. "" .Or. AFile .Eqs. OFile Then Goto NextEl
$       If F$CvTime(F$File(AFile,"RDT")) .Ges. Time Then Goto Makeit
$       Goto Loop3
$NextEL:
$       El = El + 1
$       Goto Loop2
$EndL:
$ arg=arg+1
$ If arg .Le. 8 Then Goto Loop
$ Goto Exit
$
$Makeit:
$ VV=F$VERIFY(1)
$ 'P2' 'P3'
$ VV='F$Verify(VV)
$Exit:
$ If V Then Set Verify
$ENDSUBROUTINE"""


def listRep(args, dirname, filenames):
    fg = args[0]
    first = 1
    for fn in filenames:
        if fn[-2:] == '.c':
            if first:
                first = 0
                fc = new_file(fg, dirname)

            cstr = "\"cc ''cflags'\" "
            line = "$ call make swig_root:[vms.o_alpha]"
            line += fn[:-1] + 'obj -'
            print >> fc, line
            line = "\t" + cstr + fn
            print >> fc, line
        elif fn[-4:] == '.cxx':
            if first:
                first = 0
                fc = new_file(fg, dirname)

            cstr = "\"cxx ''cxxflags'\" "
            line = "$ call make swig_root:[vms.o_alpha]"
            line += fn[:-3] + 'obj -'
            print >> fc, line
            line = "\t" + cstr + fn
            print >> fc, line
    if first == 0:
        end_file(fc)
        fc.close()
#
def genbuild(f, dir):
    os.path.walk(dir, listRep, (f,))
    cmd = 'set default swig_root:[vms]'
#
f = open('swig_root:[vms.scripts]build_all.com','w')
print >> f, '$!'
print >> f, '$! Generated by genbuild.py'
print >> f, '$!'
print >> f, '$ set default swig_root:[vms]'
print >> f, '$'
print >> f, '$ @swig_root:[vms]build_init'
#
genbuild(f, '/swig_root/source')
print >> f, '$'
print >> f, '$ set default swig_root:[vms]'
print >> f, '$'
print >> f, '$ @swig_root:[vms]build_end'
f.close
