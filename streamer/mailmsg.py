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

def read_keys(dir_path):
    emails = []
    for line in open(dir_path+'mail.ini'):
        if line[:1] =='#' or line.strip()=='':
                continue
        else:
            if 'email_id' in line:
                email_id = line.split(':')[1].strip()
                emails.append(email_id)
            if 'subject' in line:
                subject = line.split(':')[1].strip()
            if 'error_msg' in line:
                error_msg = line.split(':')[1].strip()
            if 'service' in line:
                service = line.split(':')[1].strip()
    return emails, subject, error_msg, service

def send_email(toaddr,fromaddr,subject,message,service):

    email = "From: " + fromaddr + "\n"
    email += "To: " + toaddr + "\n"
    email += "Subject: " + subject + "\n"
    email += "\n"
    email += message

    try:
        server = smtplib.SMTP(service)
        server.sendmail(fromaddr,toaddr,email)
        server.quit()
        return True
    except smtplib.SMTPException as e:
        return False

def main(dir_path):
    uname = getpass.getuser()
    hostname = platform.node()
    emails, subject, error_msg, service = read_keys(dir_path)
    for email_id in emails:
        rc = send_email(email_id, '{0}@{1}'.format(uname, hostname), subject, error_msg, service)