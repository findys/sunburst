# -*- coding: utf-8 -*-

from termcolor import colored
import time
#import MySQLdb
import pymongo
import socket
import ftplib
import optparse
from termcolor import colored

mg_unauthhosts = []
redis_unauthhost = []
Mysql_unauthhost = []
ftp_unauthhost = []
meMcached_unauthhost = []

def portFind(hosts, port, timeout=3):
    connSKt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connSKt.settimeout(timeout)
    try:
        connSKt.connect((hosts, port))
        connSKt.close()
        return True
    except:
        return False

def connMysql(hosts):
    for host in hosts:
        try:
            try:
                conn = MySQLdb.connect(host=host, user="root", passwd="")
                Mysql_unauthhost.append(host)
                conn.close()
            except:
                pass
        except:
            pass
    return Mysql_unauthhost

def connFtp(hosts):
    for host in hosts:
        try:
            ftp = ftplib.FTP(host)
            ftp.login('anonymous','guest@guest.com')
            ftp_unauthhost.append(host)
        except:
            pass


def connMongodb(hosts,port = 27017):
    for host in hosts:
        try:
            conn = pymongo.MongoClient(host,port,socketTimeoutMS=300)
            dbname = conn.database_names()
            mg_unauthhosts.append(host)
            conn.close()
        except:
            pass
    return mg_unauthhosts


def connRedis(hosts,port = 6379):
    payload = '\x2a\x31\x0d\x0a\x24\x34\x0d\x0a\x69\x6e\x66\x6f\x0d\x0a'
    s = socket.socket()
    socket.setdefaulttimeout(10)
    for host in hosts:
        try:
            s.connect((host, port))
            s.send(payload)
            recvdata = s.recv(1024)
            if recvdata and 'redis_version' in recvdata:
                redis_unauthhost.append(host)
        except:
            pass
    return redis_unauthhost

def meMcached(hosts,port = 11211):
    for host in hosts:
        payload = '\x73\x74\x61\x74\x73\x0a'
        s = socket.socket()
        socket.setdefaulttimeout(10)
        try:
            s.connect((host, port))
            s.send(payload)
            recvdata = s.recv(2048)
            s.close()
            if recvdata and 'STAT version' in recvdata:
                meMcached_unauthhost.append(host)
        except:
            pass
        return meMcached_unauthhost


def unauth(hosts):
    if portFind(hosts, 27017):
        connMongodb(hosts,27017)
    elif portFind(hosts, 6397):
        connRedis(hosts,6379)
    elif portFind(hosts,11211):
        meMcached(hosts,11211)
    elif portFind(hosts,22):
        connFtp(hosts)
    elif portFind(hosts,3306):
        connMysql(hosts)



def parseInputAndUnauth():
    parser = optparse.OptionParser("usage%prog " + "-H <target host> -f <ip_file>")
    parser.add_option('-f', action="store",dest='filename',help='import hosts from file')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target hosts')
    (options, args) = parser.parse_args()
    tgtHosts = str(options.tgtHost).split(',')
    filename = options.filename
    if filename!=None:
        f = open(filename)
        Hosts = f.readlines()
        unauth(Hosts)
    else:
        unauth(tgtHosts)

def printResults():
    print colored('[]', 'blue'), colored('results:', 'blue')
    while len(ftp_unauthhost) > 0:
        print ftp_unauthhost.pop() + ' : ' + 'FTP Anonymous Logon Succeeded'
    while len(mg_unauthhosts) > 0:
        print mg_unauthhosts.pop() + ' : ' + 'Mongodb Unauthorized Access Succeeded'
    while len(redis_unauthhost) > 0:
        print redis_unauthhost.pop() + ' : ' + 'Redis Unauthorized Access Succeeded'
    while len(meMcached_unauthhost) > 0:
        print meMcached_unauthhost.pop() + ' : ' + 'Memcached Unauthorized Access Succeeded'
    while len(Mysql_unauthhost) > 0:
        print Mysql_unauthhost.pop() + ' : ' + 'Mysql Unauthorized Access Succeeded'

#settings
VERSION = '1.0'
AUTHOR = 'DSRC'
MAIL = 'sec-oc@didichuxing.com'
BANNER = """\033[01;36m
 \033[37m use python sunburst.py -H ip1,ip2,... \033[01;33mor\033[37m python sunburst.py -f ip.txt \033[01;36m
          __
  / |  | |  | |    |  |  | /  /  |
 /  |  | |  | |    |  |  |/  /   |
 \  |  | |  | |_   |  |  |   \  ---
  \ |  | |  | |  \ |  |  |    \  |
  / |  | |  | |   ||  |  |    /  |
 /  |__| |  | |__/ |__|  |   /   |___/
 \n\033[37m # Version %s By %s mail:%s #
""" %(VERSION,AUTHOR,MAIL)


print BANNER
parseInputAndUnauth()
printResults()
