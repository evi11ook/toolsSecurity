#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import argparse, sys

class sockSMTP():

    sSMTP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self,mHOST,mPORT):
        if mHOST == None:
            print "specify server address"
            exit()
        try:
            self.sSMTP.connect((mHOST,mPORT))
            print "[+] Connect server "+mHOST
        except Exception as e:
            print "NOT CONNECT TO "+str(mHOST)
            print e
            self.close()
            exit()
        try:
            header = self.recv()
            print "[+] response from "+mHOST
        except Exception as e:
            print e
            self.close()
            exit()
        if header.split(' ')[0] != '220':
            print '[!] ERROR: '+header
            self.close()
            exit()

    def colse(self):
        self.sSMTP.close()

    def recv(self):
        data = self.sSMTP.recv(1024).replace('\n','').replace('\r','')
        # print "[DEBUG-RECV-MSG]"+data
        return data

    def send(self,msg):
        # print "[DEBUG-SEND-MSG]"+msg
        self.sSMTP.sendall(msg)


def createParser ():
    parser = argparse.ArgumentParser(
            prog = sys.argv[0]
            )
    parser.add_argument ('-t',    metavar='TO',           help="mail recipien")
    parser.add_argument ('-nt',   metavar='NAME-TO',      help="Name TO (TEXT)")
    parser.add_argument ('-nf',   metavar='NAME-FROM',    help="Name FROM (TEXT)")
    parser.add_argument ('-f',    metavar='FROM',         help="mail from")
    parser.add_argument ('-s',    metavar='SERVER',       help="mail server ip/hostname")
    parser.add_argument ('-d',    metavar='DOMAIN',       help="mail server domain")
    parser.add_argument ('-sb',   metavar='Subject',      help="Subject of this message")
    parser.add_argument ('-txt',  metavar='TEXT',         help="Text for message")
    parser.add_argument ('-tf',   metavar='TEXT',         help="File containing the message text")
    return parser



if __name__ == "__main__" :

    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])

    mHOST     = namespace.s
    mPORT     = 25
    mDOMAIN   = namespace.d
    mFROM     = namespace.f
    mTO       = namespace.t
    nFROM     = namespace.nf
    nTO       = namespace.nt
    mSUBJ     = namespace.sb
    mTEXT     = namespace.txt

    if mDOMAIN == None:
        mDOMAIN = mHOST

    try:
        sSMTP = sockSMTP(mHOST,mPORT)
    except Exception as e:
        print e
        exit()

    try:
        sSMTP.send('HELO '+mDOMAIN+'\r\n')
        recv = sSMTP.recv()
        if recv.split(' ')[0] != '250':
            print "[!] BAD ANSWER:"
            print recv
            exit()
    except Exception as e:
        print e
        exit()

    try:
        sSMTP.send('MAIL FROM: '+mFROM+'\r\n')
        recv = sSMTP.recv()
        if recv.split(' ')[0] != '250':
            print "[!] BAD ANSWER:"
            print recv
            exit()
    except Exception as e:
        print e
        exit()

    try:
        sSMTP.send('RCPT TO: '+mTO+'\r\n')
        recv = sSMTP.recv()
        if recv.split(' ')[0] != '250':
            print "[!] BAD ANSWER:"
            print recv
            exit()
    except Exception as e:
      print e
      exit()

    try:
        sSMTP.send('DATA\r\n')
        recv = sSMTP.recv()
    except Exception as e:
      print e
      exit()

    try:
        if nTO != None:
            sSMTP.send('To: '+nTO+' <'+mTO+'>\r\n')
        if nFROM != None:
            sSMTP.send('From: '+nFROM+' <'+mFROM+'>\r\n')
        if mSUBJ != None:
            sSMTP.send('SUBJECT: '+mSUBJ+'\r\n')
        sSMTP.send(mTEXT+'\r\n')
        sSMTP.send('\r\n.\r\n')
        recv = sSMTP.recv()
        if recv.split(' ')[0] != '250':
            print "[!] BAD ANSWER:"
            print recv
            exit()
        print "[+] SEND MESSAGE: OK"
    except Exception as e:
        print "[!] ERROR: "
        print e
        exit()

    sSMTP.send('QUIT')
    exit()
