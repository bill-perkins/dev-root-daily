#!/usr/bin/python
#
# simple script to take incoming system status emails and convert them into
# something easy to read in the mornings.
#
# takes files from ~/incoming/new and strips them down to properly
# named files in ~/incoming/work
# the original incoming files are moved to ~/incoming/cur


# some standard python stuff
import sys
import os
from dateutil.parser import *

iam = sys.argv[0]

# usage check:
# (do whatever is needed here)
#if len(sys.argv) < 2:
#    print("usage: " + iam + " <input file>")
#    exit(1)

# ----------------------------------------------------------------------------
# getContent(inpname): bring the contents of the given input file into a list
# and return the list.
# ----------------------------------------------------------------------------
def getContent(inpname):
    content = []

    # open up the new file, bring it in as a list:
    try:
        with open(inpname, "r") as inpfile:
            content = inpfile.readlines()

    except IOError as err:
        print("getContent(): Couldn't open file " + inpname + ": " + str(err))

    return content

# ----------------------------------------------------------------------------
# putContent(content, outname): send the content list to the given output file
# ----------------------------------------------------------------------------
def putContent(content, outname):
    if len(content) == 0:
        print("putContent(): empty content")
        return 1

    if len(outname) == 0:
        print("putContent(): empty output name")
        return 1

    # since content gets consumed, make and use a local copy:
    lclcontent = list(content)

    try:
        with open(outname, "w") as outfile:
            while len(lclcontent) > 0:
                outfile.write(lclcontent.pop(0))

            outfile.write('\n') # one final nl

    except IOError as err:
        print("putContent(): Couldn't open output file " + outname + ": " + str(err))
        return 1

    return 0

# ----------------------------------------------------------------------------
# makeReport(content): produce a 'digested' report from content
# ----------------------------------------------------------------------------
def makeReport(content):
    outlist = []        # init

    if len(content) == 0:
        print("makeReport(): content is empty.")
        return

    # --- generate a report on the new output:
    newheader = content.pop(0)
    newheader = newheader[:-1] # strip the '\n'

    # snag the next line, it's got uptime, user count, load average
    uptime = content.pop(0)
    uptimeparts = uptime.split(',')
    utp_len = len(uptimeparts)

    # put how long we've been up into the header:
    soh = uptimeparts[0].split(' ', 2)
    hdr = '; ' + soh[2]
    if 'days' in uptimeparts[0]:
        hdr += ',' + uptimeparts[1]

    outlist.append(newheader + hdr + '\n\n')

    # get the load average for later:
    loadavg1 = uptimeparts[utp_len - 3] + uptimeparts[utp_len - 2] + uptimeparts[utp_len - 1]
    loadavg2 = loadavg1.split(':')
    loadavg  = loadavg2[0].strip() + "     " + loadavg2[1] # send this out later

    # say how many users and list them, if any:
    content.pop(0) # skip header line for 'w' command
    usercount = 0;
    userlist = []
    tmpline = content.pop(0)
    while len(tmpline) > 1:
        userlist.append("  " + tmpline)
        usercount += 1;
        tmpline = content.pop(0)

    if (usercount == 0):
        outlist.append('no users\n')
    else:
        if usercount == 1:
            outlist.append("1 user:\n")
        else:
            outlist.append(str(usercount) + " users:\n")

        for line in userlist:
            outlist.append(line)

    outlist.append('\n')

    # show load average:
    outlist.append(loadavg)

    # skip blank lines:
    tmpline = '\n'
    while len(tmpline) == 1:
        tmpline = content.pop(0)

    # get amount of free memory:
    if 'total' in tmpline:
        tmpline = content.pop(0)    # get memory stats
        parts = tmpline.split()     # split up the stats
        total = float(parts[1])
        avail = float(parts[6])
        outlist.append("used memory:     " + "{:>4.1f}".format((1 - (avail / total)) * 100) + '%\n')

    # get amount of swap space:
    tmpline = content.pop(0)
    parts = tmpline.split()
    total = float(parts[1])
    used  = float(parts[2])
    free  = float(parts[3])
    outlist.append("used swap space: " + "{:>4.1f}".format((1 - (free / total))  * 100) + '%\n\n')

    # get filesystem usage:
    outlist.append("filesystem usage:\n")
    tmpline = content.pop(0)         # skip blank line
    tmpline = content.pop(0)         # skip header for df -h
    tmpline = content.pop(0)         # get 1st line

    while len(tmpline) > 1:          # go until next blank line
        parts = tmpline.split()      # split it up
        outlist.append("  " + str.ljust(parts[5], 15) + str.rjust(parts[4], 5) + '\n')
        tmpline = content.pop(0)     # get next line

    outlist.append('\n')

    # --- check network for errors:
    tmpline = content.pop(0)         # get a line
    if 'ens192' in tmpline or 'eno16780032' in tmpline:
        outlist.append("network check:\n")
        while len(tmpline) > 1:      # go until next blank line
            if 'errors' in tmpline:
                errlist = tmpline.split()
                if errlist[2] != '0' or errlist[4] != '0' or errlist[6] != '0' or errlist[8] != '0':
                    for i in range(0,8):
                        outlist.append("  " + errlist[i] + ' ')
                    outlist.append('\n')

            tmpline = content.pop(0) # get next line

        outlist.append('\n')

    while len(content) > 0:
        tmpline = content.pop(0)
        if 'services check' in tmpline:
            outlist.append(tmpline)
            while len(tmpline) > 1:
                if len(content) > 0:
                    tmpline = content.pop(0)
                    outlist.append(tmpline)
                else:
                    tmpline = ''

        if 'auditcli check' in tmpline:
            outlist.append(tmpline)
            while len(tmpline) > 1:
                if len(content) > 0:
                    tmpline = content.pop(0)
                    outlist.append(tmpline)
                else:
                    tmpline = ''

        if 'ping test' in tmpline:
            outlist.append(tmpline)
            while len(tmpline) > 1:
                if len(content) > 0:
                    tmpline = content.pop(0)
                    outlist.append(tmpline)
                else:
                    tmpline = ''

    return outlist

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
os.chdir(os.environ['HOME'] + '/incoming/')
inpdir = 'new/'
outdir = 'work/'
tmpdir = 'tmp/'
curdir = 'cur/'

lclhostname = ''
timestamp = ''

inpfileslist = os.listdir(inpdir)

for thefile in inpfileslist:
    inpath = inpdir + thefile
    contents = getContent(inpath)
    os.rename(inpdir + thefile, curdir + thefile)

    if len(contents) == 0:
        continue;   # skip empty files

    while len(contents) > 0:
        inpline = contents.pop(0)
        if len(inpline) == 1:
            break;  # break outta here when we hit the first blank line

        # search for the subject line, get the short hostname:
        if "Subject: daily report from" in inpline:
            parts = inpline.split(' ')
            tmphost = parts[4][:-1] # trim trailing \n
            lclhostname = tmphost.split('.')[0]
            continue

        # search for the date line, get YYYYMMDD-HHMMSS:
        if 'Date: ' in inpline:
            msgdate = parse(inpline[6:])
            timestamp = str(msgdate.year) + \
                "{:02d}".format(msgdate.month) + \
                "{:02d}".format(msgdate.day) + \
                '-' + \
                "{:02d}".format(msgdate.hour) + \
                "{:02d}".format(msgdate.minute) + \
                "{:02d}".format(msgdate.second)
            continue

    # --- now send the data to a report file:
    outname = lclhostname + '.' + timestamp
    outpath = outdir + outname + ".report"
    reportContent = makeReport(contents)
    putContent(reportContent, outpath)

# ----------------------------------------------------------------------------
# 
# ----------------------------------------------------------------------------

# EOF:
