#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import argparse, sys
import os
import base64
import mimetypes
import hashlib

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
        #print "[DEBUG-SEND-MSG]"+msg
        self.sSMTP.sendall(msg)


def makeFileAttach(file):
    if os.path.isfile(file):
        mimetypes.init()
        tFileMime   = mimetypes.types_map['.'+file.split('.')[1]]
        tFile       = open(file,'rb')
        tFileBin    = tFile.read()
        tFileSize   = str(os.stat(file).st_size)
        tFileB64    = base64.b64encode(tFileBin)
        tFileHash   = hashlib.md5(tFileBin).hexdigest().upper()                                                                    # Сделать хеш!!!!
        HEADERFILE  = ''
        HEADERFILE  = HEADERFILE + "--_005_098F6BCD4621D373CADE4E832627B4F6srvExchLocalMail_\r\n"
        HEADERFILE  = HEADERFILE + "Content-Type: "+tFileMime+"; name=\""+file+"\"\r\n"
        HEADERFILE  = HEADERFILE + "Content-Description: "+file+"\r\n"
        HEADERFILE  = HEADERFILE + "Content-Disposition: attachment; filename=\""+file+"\"; size="+str(tFileSize)+";\r\n"
        HEADERFILE  = HEADERFILE + "	creation-date=\"Wed, 11 Apr 2017 10:13:33 GMT\";\r\n"
        HEADERFILE  = HEADERFILE + "	modification-date=\"Wed, 18 Apr 2017 10:13:33 GMT\"\r\n"
        HEADERFILE  = HEADERFILE + "Content-ID: <"+file+"@01D3D727.D17CCDB0>\r\n"
        HEADERFILE  = HEADERFILE + "Content-Transfer-Encoding: base64\r\n\r\n"
        a = 0
        BODY = tFileB64+'\r\n'
        return HEADERFILE + BODY + "\r\n"


def createParser ():
    parser = argparse.ArgumentParser(
            prog = sys.argv[0]
            )
    parser.add_argument ('-t',    metavar='TO',                 help="mail recipien")
    parser.add_argument ('-nt',   metavar='NAME-TO',            help="Name TO (TEXT)")
    parser.add_argument ('-nf',   metavar='NAME-FROM',          help="Name FROM (TEXT)")
    parser.add_argument ('-f',    metavar='FROM',               help="mail from")
    parser.add_argument ('-s',    metavar='SERVER',             help="mail server ip/hostname")
    parser.add_argument ('-d',    metavar='DOMAIN',             help="mail server domain")
    parser.add_argument ('-sb',   metavar='Subject',            help="Subject of this message")
    parser.add_argument ('-txt',  metavar='TEXT',               help="Text for message")
    parser.add_argument ('-tf',   metavar='TEXT',               help="File containing the message text")
    parser.add_argument ('-fd',   metavar='DIR TO FILE/FILES',  help="Attach file or files")
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
    ATTACH    = namespace.fd

    if ATTACH != None:
        if os.path.isdir(ATTACH) == True:
            pass
        else:
            ATTACH = makeFileAttach(ATTACH)

    # exit()

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
        sSMTP.send('Accept-Language: ru-RU, en-US\r\n')
        sSMTP.send('Content-Language: ru-RU\r\n')
        sSMTP.send('X-MS-Has-Attach: yes\r\n')
        sSMTP.send('X-MS-TNEF-Correlator:\r\n')
        sSMTP.send('x-ms-exchange-transport-fromentityheader: Hosted\r\n')
        sSMTP.send('x-originating-ip: [172.16.20.129]\r\n')
        if type(ATTACH) != type(None):
            sSMTP.send('Content-Type: multipart/mixed;\r\n')
            sSMTP.send('	boundary="_005_098F6BCD4621D373CADE4E832627B4F6srvExchLocalMail_";\r\n\r\n')
            sSMTP.send('MIME-Version: 1.0\r\n')
            sSMTP.send('--_005_098F6BCD4621D373CADE4E832627B4F6srvExchLocalMail_\r\n')
            sSMTP.send('Content-Type: multipart/alternative; boundary="_000_098F6BCD4621D373CADE4E832627B4F6srvExchLocalMail_"\r\n')
            sSMTP.send('--_000_098F6BCD4621D373CADE4E832627B4F6srvExchLocalMail__\r\n')
            sSMTP.send('Content-Type: text/plain; charset="UTF-8"\r\n')
            sSMTP.send('Content-Transfer-Encoding: quoted-printable\r\n\r\n')
        sSMTP.send(mTEXT+'\r\n\r\n')
        if type(ATTACH) != type(None):
            sSMTP.send(ATTACH+'\r\n')
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
