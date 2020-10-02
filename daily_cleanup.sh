#!/bin/sh
#
# daily_cleanup.sh - clean up /sastmp, /sastmp/saswork
# should be run as root on the micro servers

# use for /sastmp, /sastmp/saswork:
# /opt/sas/spre/home/SASFoundation/utilities/bin/cleanwork
#   [-n] -hostmatch <hostname> [-log <logfile>] -v <directory>

# ${CLEANWORK} is on the micro servers:
CLEANWORK='/opt/sas/spre/home/SASFoundation/utilities/bin/cleanwork'

LOGPATH='/var/log/cleanwork'

TODAY=`date +%Y%m%d`

for s in \
    sasdevcasrhelsr01 \
    sasdevcasrhelsr02 \
    sasdevmicrorhelsr01 \
    sasdevmicrorhelsr02 \
    sasdevcontrollerrhelsr01 \
    sasdevcontrollerrhelsr02; do

    echo "server $s:"
    echo    "    ${CLEANWORK} -v -log ${LOGPATH}/${TODAY}.sastmp.${s}.log -hostmatch $s /sastmp"
    echo -n "    "
    ${CLEANWORK} -v -log ${LOGPATH}/${TODAY}.sastmp.${s}.log -hostmatch $s /sastmp
#    ${CLEANWORK} -hostmatch $s -v /sastmp
    echo
    echo    "    ${CLEANWORK} -v -log ${LOGPATH}/${TODAY}.saswork.${s}.log -hostmatch $s /sastmp/saswork"
    echo -n "    "
    ${CLEANWORK} -v -log ${LOGPATH}/${TODAY}.saswork.${s}.log -hostmatch $s /sastmp/saswork
#    ${CLEANWORK} -hostmatch $s -v /sastmp/saswork
    echo

# The files in /opt/sas/viya/config/var/log don't take an appreciable amount of space.
# We should probably keep only 32 days worth of log files.
#
# Note that when piping the find command output through xarks with the 'ls -lhart' gives
# a proper ls listing:
#    ssh $s 'find /opt/sas/viya/config/var/log -name "*_*.log" -mtime +20 | xargs ls -lhart'
#    echo
done
echo



# EOF:
