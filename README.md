TPX Brute - The z/OS TPX logon panel brute forcer
-----------------------------------------------------
* By: Quentin HARDY (quentin.hardy@bt.com or quentin.hardy@protonmail.com)
* Based on: https://github.com/mainframed/TSO-Brute
* Thanks to "Soldier of FORTRAN".

TPX (Terminal Productivity Executive) is a multiple session manager for IBM mainframes. The TPX logon panel tells you if you have a valid user account. 
Consequently, you can enumerate users allowed to authenticate on the z/OS system.
With valid users, you can do a dictionnary attack on passwords.


Features
---------

Thanks to TPX_brute tool, you can (from a TPX logon panel):

* __enumerate valid users__ :
	
  You have to give a file of usernames to the tool. It will try to use each username to log in.
  For information, TSO only allows characters A-z, 0-9, @, # and $ in its username. 
  Additionally a username cannot start with a number and it must be seven characters or less. 
	This script will skip items that would be invalid TSO username.
	As TSO_brute tool, this mode is envoked by passing -e or --enumeration.
	
* __brute force passwords__: 
	
  The brute forcer does the same as the enumerator except it requires a file of passwords to use. 
	As TSO_Brute tool, the same rules for passwords apply except it can start with a number and has a max length of eight instead of seven. 
	This is the default mode for TPX_Brute. 

As TSO_Brute tool, TPX_Brute makes use of x3270 and s3270 to perform much of the heavy lifting, using __py3270 which has been modified for TPX interface__ (included with this tool). 


The tool comes 2 modes:

* Movie Mode: 
  In this mode you can watch script typing commands in a 3270 emulator in real time. 
	It can be enabled with the --moviemode or -m option. 

* Quiet mode: 
  In this mode only valid Usernames/passwords are printed to the screen. 
	It can be enabled with the -q or --quiet option

SETTINGS FOR YOUR TARGET
------------------------

The ADPAPT section in the TPX_Brute.py script is used to get to the TPX logon panel with an invalid/valid credentials. 
__You will have to change this section of the script before being able to use it.__

Screens are saved to an HTML file (tso_screen.html file). See the following line in source code:
```
em.exec_command('PrintText(html,tso_screen.html)')).
```

Examples
------------------------

* To just enumerate users:

```
python TPX_Brute.py -t target:23 -u users.txt -e
```

* To enumerate users and then brute force the password for the found user ID, using movie mode and sleep 2 seconds between actions:

```
python TPX_Brute.py -t target:23 -u users.txt -p passwords.txt -m -s 2
```


Installation
---------------------------

Install 3270/x3270 to /usr/bin. 

```
sudo apt-get install s3270 x3270
```

Install missing python packages with pip.

Known Issues:
-------------
* TSO accounts can be locked during brute force attacks.
