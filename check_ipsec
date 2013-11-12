#!/bin/bash
#
# Plugin Name: check_ipsec
# Version: 2.2
# Date: 11/12/2013
#
# Usage: check_ipsec --tunnels <n>
#
# gateways.txt file must be located in same directory
# and has to look like:
# nameofconn1	192.168.0.1
# nameofconn2	192.168.1.1
#
# ------------Defining Variables------------
PROGNAME=`basename $0`
REVISION=`echo '$Revision: 2.2 $' | sed -e 's/[^0-9.]//g'`
DOWN=""
# ---------- Change to your needs ----------
# PLUGINPATH="/usr/lib/nagios/plugins"
GATEWAYLIST="gateways.txt"
IPSECBIN="/usr/sbin/ipsec"
# ------------------------------------------

# Testing availability of $IPSECBIN and $GATEWAYLIST

test -e $IPSECBIN
if [ $? -ne 0 ];
then
	echo CRITICAL - $IPSECBIN not exist
	exit $STATE_CRITICAL
else
	STRONG=`$IPSECBIN --version |grep strongSwan | wc -l`
fi

test -e $GATEWAYLIST
if [ $? -ne 0 ];
then
   echo CRITICAL - $GATEWAYLIST not exist
   exit $STATE_CRITICAL
fi

print_usage() {
        echo "Usage:"
        echo " $PROGNAME --help"
        echo " $PROGNAME --version"
        echo " Created by Henry, questions or problems, report on Github"
		echo ""
}

print_help() {
        print_revision $PROGNAME $REVISION
        echo ""
        print_usage
        echo " Checks vpn connection status of an openswan or strongswan installation."
		echo ""
        echo " provides the tunnel status of the openswan or strongswan installation"
		echo ""
        echo " --help"
		echo " -h"
        echo " prints this help screen"
		echo ""
        echo " --version"
		echo " -V"
        echo " Print version and license information"
        echo ""
}

check_tunnel() {

	if [[ "$STRONG" -eq "1" ]]
	then
	    GATEWAYS=`$IPSECBIN status`
	else
	    GATEWAYS=`$IPSECBIN whack --status`
	fi

	i=1

	while read line; do
		CONN=`echo $line`
		tunneltest=`echo "$GATEWAYS" | grep -e $CONN | wc -l`

		if [[ "$tunneltest" -ge "3" ]]
    		then
			echo "0 VPN_Tunnel_$CONN - VPN Tunnel $CONN is up and running."
    		else
			echo "2 VPN_Tunnel_$CONN - VPN Tunnel $CONN is down."
		fi

	i=$[$i+1]
	done < $GATEWAYLIST

}


case "$1" in
--help)
        print_help
        exit $STATE_OK
        ;;
-h)
        print_help
        exit $STATE_OK
        ;;
--version)
        print_revision $PLUGIN $REVISION
        exit $STATE_OK
        ;;
-V)
        print_revision $PLUGIN $REVISION
        exit $STATE_OK
        ;;
*)
	check_tunnel
        exit $STATE_OK

esac
