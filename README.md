# srx_vpn_troubleshooting_tool

The SRX VPN Troubleshoot tool helps SRX admins to troubleshoot VPN issues without the need to use CLI or management apps.

---REQUIREMENTS---
Python 2.7.12 (it may work with other 2.7 releases, I just tried with .12)
Juniper PyEZ library

---HOW IT WORKS---
The application connects to a given SRX, extracts the vpn log file, parser all the messages and upload all of them
to a temporary database for visualization.
When the user is finishes using the application, the database and the original vpn log are deleted

---INITIAL SET UP---
You need to configure the SRX yoy want to troubleshoot to generate syslog message for the VPN daemon (KMD)
In config. mode, just type:

set system syslog file kmd-logs daemon info
set system syslog file kmd-logs match KMD
commit

The application looks specifically for the kmd-logs file, so you need to set up the log file with this exactly name

To launch the application, just download the main_gui, vpn_troubleshooting and vpn_log files to a folder in your computer
and run the main_gui.py file
If you are running from shell, just type python main_gui.py, if your OS already mapped python files with the interpreter, just
open the app from the graphical user interface.

---TROUBLESHOOTING THE TROUBLESHOOTER---
If you run into any issue, take a look in the log file. Once started, the application will save all the main tasks results into
the vpn_log file (log is saved in the same folder where the application is running). It make easier to find where things went 
south and fix them (error in the network connection, lake of permission, credential errors, etc).
