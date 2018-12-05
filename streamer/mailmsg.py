#! /usr/bin/env python3

"""
Center for Research on Media, Technology, and Health
University of Pittsburgh

Author:  welling
Version: 2018-12-05
Python version: 2.7 (tested) & 3.5+ (preferred)

Required Python packages:
  smtplib
  getpass
  platform

"""


import smtplib
import getpass
import platform

def send_email(toaddr,fromaddr,subject,message):

    email = "From: " + fromaddr + "\n"
    email += "To: " + toaddr + "\n"
    email += "Subject: " + subject + "\n"
    email += "\n"
    email += message

    try:
        server = smtplib.SMTP('mailer.psc.edu')
        server.sendmail(fromaddr,toaddr,email)
        server.quit()
        return True
    except smtplib.SMTPException as e:
        # print('exception: {0}'.format(e))
        return False

def main():
    uname = getpass.getuser()
    hostname = platform.node()
    rc = send_email('welling@psc.edu', '{0}@{1}'.format(uname, hostname), 'This is a test', 'Hello World!')
    print('send_email returned {0}'.format(rc))

if __name__ == '__main__':
    main()
