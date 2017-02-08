__author__ = 'Alexandre S. Cezar - acezar@juniper.net - PyEZ, Database and parsers'
# __author__ = 'Rosemary Chan - Parsers, GUI and log function'

import datetime
import os
import sqlite3
import sys
import vpn_log
# ------------------------------------------------------------------------------------
from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP
from jnpr.junos.exception import *
# ------------------------------------------------------------------------------------

# Variables Definition
global g_msg

vdate = datetime.datetime.now()
vtxt_file = r"kmd.txt"
g_msg = list()

# ------------------------------------------------------------------------------------
# Connecting to the selected SRX (variables received by user input from the main_gui app)
#print "Establishing connection to:", g_input_IP
g_msg.append("Establishing connection to SRX")

dev = Device(host=g_input_IP, user=g_input_username, password=g_input_password)

try:
    dev.open()
except ConnectError as e:
#    print "Could not connect to the SRX, please check your connectivity"
    g_msg.append("Could not connect to the SRX, please check your connectivity")
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# print "Connected"
g_msg.append("Connected")


# Retrieving the KMD log file and creating the local directory (if needed)
# print "Retrieving the VPN Log File"
g_msg.append("Retrieving the VPN Log File")

try:
    # Default progress messages
    with SCP(dev, progress=True) as kmd_file:
        kmd_file.get("/var/log/kmd-logs", local_path="./")
except ConnectError as e:
#    print "Could not retrieve the VPN log file, exiting"
    g_msg.append("Could not retrieve the VPN log file, exiting")
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# print "VPN Log file successfully retrieved"
g_msg.append("VPN Log file successfully retrieved")

# Closing Connection to the SRX device
# print "Closing Connection to:", g_input_IP
g_msg.append("Closing Connection to SRX")

try:
    dev.close()
except ConnectError as e:
#    print "Error on disconnecting from the SRX "
    g_msg.append("Error on disconnecting from the SRX")
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# print "Connection Closed"
g_msg.append("Connection Closed")


# Adding a .txt extension to the KMD file
# print "Converting log file to .txt file"
g_msg.append("Converting log file to a .txt file")

try:
    os.rename("kmd-logs", "kmd.txt")
except OSError as e:
#    print "Error converting log file to .txt file"
    g_msg.append("Error converting log file to a .txt file")
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# print "KDM.txt file is now available"
g_msg.append("KDM.txt file is now available")

# ------------------------------------------------------------------------------------

# Initializing the database
# print "Initializing the database"
g_msg.append("Initializing the database")

try:
    conn = sqlite3.connect('kmd.db')
    curs = conn.cursor()
    curs.executescript("""
        DROP TABLE IF EXISTS KMD;
        CREATE TABLE KMD (DATE, LOCAL, REMOTE, TUNNEL, MESSAGE);
        """)  # checks if table exists and makes a fresh one, if nothing is found.
    print "Database Initialized successfully"
    g_msg.append("Database Initialized successfully")
except sqlite3.Error as e:
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# Create indexes for the database
# print "Creating database's index"
g_msg.append("Creating database's index")

try:
    conn = sqlite3.connect('kmd.db')
    curs = conn.cursor()
    curs.executescript("""
        CREATE INDEX KMD_DATE ON KMD (DATE);
        CREATE INDEX KMD_LOCAL ON KMD (LOCAL);
        CREATE INDEX KMD_REMOTE ON KMD (REMOTE);
        CREATE INDEX KMD_MESSAGE ON KMD (MESSAGE);
        """)
#    print "Database's index successfully created"
    g_msg.append("Database's index successfully created")
except sqlite3.Error as e:
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# Parsing the txt file (to remove special characters)
# print "Parsing the kmd.txt file"
g_msg.append("Parsing the kmd.txt file")

try:

    with open(vtxt_file, 'r') as f:
        data = f.readlines()

        vMsg_to_find = [
            'IKE negotiation successfully completed',   # 0
            'KMD_PM_SA_ESTABLISHED',                    # 1
            'KMD_VPN_UP_ALARM_USER',                    # 2
            'KMD_VPN_DOWN_ALARM_USER',                  # 3
            'IKE negotiation failed with error',        # 4
            'KMD_DPD_PEER_DOWN',                        # 5
            'KMD_VPN_TS_MISMATCH',                      # 6
            'Phase-1 [responder] done',                 # 7
            'IKE Phase-2: Failed to match',             # 8
            'KMD_VPN_PV_PHASE2',                        # 9
            'IKE Phase-2 Failure',                      # 10
            'IKE Phase-2: Negotiations failed'          # 11
        ]

        for line in data:

            vLogDate = ""
            vVPN_Tunnel = "-"
            vLocal_Peer = "-"
            vRemote_Peer = "-"
            vMsg = ""

            # taking off the line feed character
            line = line.rstrip(chr(10))

            for vMsgID in range(0, 12):
                vpos_msg1 = line.find(vMsg_to_find[vMsgID])

                if vpos_msg1 != -1:

                    vpos_date = 0
                    vqtd_char_date = 16

                    vLogDate = line[vpos_date: (vpos_date + vqtd_char_date)]
                    vLogDate = vLogDate.rstrip(' ')

                    break

            if vpos_msg1 != -1:

                # -----------------------------------------------------------------------------------
                # Check if the line contains the messages:
                # 'IKE negotiation successfully completed' or 'IKE negotiation failed with error'
                # vMsgID = 0 or vMsgID = 4
                # -----------------------------------------------------------------------------------
                if vMsgID == 0 or vMsgID == 4:

                    vpos_tunnel = line.find(' VPN: ')
                    vpos_other2 = line.find(' Gateway:')
                    vpos_local = line.find('Local:')
                    vpos_remote = line.find('Remote:')
                    vpos_other3 = line.find('Local IKE-ID:')

                    vqtd_char_msg1 = vpos_tunnel - vpos_msg1
                    vqtd_char_tunnel = vpos_other2 - vpos_tunnel
                    vqtd_char_local = vpos_remote - vpos_local
                    vqtd_char_remote = vpos_other3 - vpos_remote

                    vMsg = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1 - 1)]
                    vVPN_Tunnel = line[(vpos_tunnel + len(' VPN: ')):
                                ((vpos_tunnel + len(' VPN: ')) + vqtd_char_tunnel - len(' VPN: '))]
                    vLocal_Peer = line[(vpos_local + len('Local: ')):
                                ((vpos_local + len('Local: ')) + vqtd_char_local - len('Local: ') - 2)]
                    vRemote_Peer = line[(vpos_remote + len('Remote: ')):
                                ((vpos_remote + len('Remote: ')) + vqtd_char_remote - len('Remote: ') - 2)]

                # -------------------------------------------------------
                # Check if the line contains 'KMD_PM_SA_ESTABLISHED'
                # vMsgID = 1
                # -------------------------------------------------------
                elif vMsgID == 1:

                    vpos_local = line.find('Local gateway:')
                    vpos_remote = line.find('Remote gateway:')
                    vpos_other1 = line.find('Local ID:')
                    vpos_msg2 = line.find('Traffic-selector: ')

                    vqtd_char_msg1 = vpos_local - vpos_msg1
                    vqtd_char_local = vpos_remote - vpos_local
                    vqtd_char_remote = vpos_other1 - vpos_remote
                    vqtd_char_msg2 = len(line) - vpos_msg2

                    vMsg1 = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1 - 2)]
                    vLocal_Peer = line[(vpos_local + len('Local gateway: ')):
                        ((vpos_local + len('Local gateway: ')) + vqtd_char_local - len('Local gateway: ') - 2)]
                    vRemote_Peer = line[(vpos_remote + len('Remote gateway: ')):
                        ((vpos_remote + len('Remote gateway: ')) + vqtd_char_remote - len('Remote gateway: ') - 2)]
                    vMsg2 = line[vpos_msg2:(vpos_msg2 + len(line))]

                    vMsg = vMsg1 + ". " + vMsg2

                    vVPN_Tunnel = "-"

                # -------------------------------------------------------------------------------------
                # Check if the line contains 'KMD_VPN_UP_ALARM_USER' or 'KMD_VPN_DOWN_ALARM_USER'
                # vMsgID = 2 or vMsgID = 3
                # -------------------------------------------------------------------------------------
                elif vMsgID == 2 or vMsgID == 3:

                    vpos_remote = line.find('from ')

                    if vMsgID == 2:
                        vpos_other1 = line.find(' is up. ')
                    else:
                        vpos_other1 = line.find(' is down. ')

                    vpos_local = line.find('Local-ip:')
                    vpos_other2 = line.find('gateway name:')
                    vpos_tunnel = line.find('vpn name: ')
                    vpos_other3 = line.find('tunnel-id:')
                    vpos_msg2 = line.find('Traffic-selector:')
                    vpos_other4 = line.find('Traffic-selector local ID:')

                    vqtd_char_msg1 = len("KMD_VPN_UP_ALARM_USER")
                    vqtd_char_remote = vpos_other1 - vpos_remote
                    vqtd_char_local = vpos_other2 - vpos_local
                    vqtd_char_tunnel = vpos_other3 - vpos_tunnel
                    vqtd_char_msg2 = vpos_other4 - vpos_msg2

                    vMsg1 = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1)]

                    vLocal_Peer = line[(vpos_local + len('Local-ip: ')):
                        ((vpos_local + len('Local-ip:')) + vqtd_char_local - len('Local-ip: ') - 1)]

                    vRemote_Peer = line[(vpos_remote + len('from ')):
                        ((vpos_remote + len('from ')) + vqtd_char_remote - len('from '))]

                    vVPN_Tunnel = line[(vpos_tunnel + len('vpn name: ')):
                        ((vpos_tunnel + len('vpn name: ')) + vqtd_char_tunnel - len('vpn name: ') - 2)]

                    vMsg2 = line[vpos_msg2: (vpos_msg2 + vqtd_char_msg2 - 2)]

                    vMsg = vMsg1 + ", " + vMsg2

                    # for ID without message
                    if vpos_local == -1:
                        vVPN_Tunnel = "-"
                        vLocal_Peer = "-"
                        vRemote_Peer = "-"
                        vMsg1 = ""
                        vMsg2 = ""
                        vMsg = ""

                # -------------------------------------------------------------------------------------
                # Check if the line contains 'KMD_DPD_PEER_DOWN'
                # vMsgID = 5
                # -------------------------------------------------------------------------------------
                elif vMsgID == 5:

                    vpos_remote = line.find('DPD detected peer') + len("DPD detected peer ")
                    vpos_other1 = line.find(' is dead')
                    vpos_other2 = vpos_other1 + len(' is dead')

                    vqtd_char_msg1 = vpos_other2 - vpos_msg1
                    vqtd_char_remote = vpos_other1 - vpos_remote

                    vMsg = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1)]
                    vRemote_Peer = line[vpos_remote: (vpos_remote + vqtd_char_remote)]

                # -------------------------------------------------------------------------------------
                # Check if the line contains 'KMD_VPN_TS_MISMATCH'
                # vMsgID = 6
                # -------------------------------------------------------------------------------------
                elif vMsgID == 6:

                    vpos_tunnel = line.find('vpn name:')
                    vpos_other1 = line.find('Peer Proposed traffic-selector local-ip')

                    vqtd_char_msg1 = vpos_tunnel - vpos_msg1
                    vqtd_char_tunnel = vpos_other1 - vpos_tunnel

                    vMsg = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1) - 2]

                    vVPN_Tunnel = line[(vpos_tunnel + len('vpn name: ')):
                                ((vpos_tunnel + len('vpn name: ')) + vqtd_char_tunnel - len('vpn name: ') - 2)]

                # -------------------------------------------------------------------------------------
                # Check if the line contains 'Phase-1 [responder] done'
                # vMsgID == 7
                # -------------------------------------------------------------------------------------
                elif vMsgID == 7:

                    vpos_local = line.find('for local=')
                    vpos_remote = line.find('remote=')
                    vpos_msg2 = line.find('Phase-2 [responder] done')
                    vpos_other1 = line.find('for p1_local=')

                    vqtd_char_msg1 = vpos_local - vpos_msg1
                    vqtd_char_local = vpos_remote - vpos_local
                    vqtd_char_remote = vpos_msg2 - vpos_remote
                    vqtd_char_msg2 = vpos_other1 - vpos_msg2

                    vMsg1 = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1 - 1)]

                    vLocal_Peer1 = line[(vpos_local + len('for local=')):
                        ((vpos_local + len('for local=')) + vqtd_char_local - len('for local='))]

                    vRemote_Peer1 = line[(vpos_remote + len('remote=')):
                        ((vpos_remote + len('remote=')) + vqtd_char_remote - len('remote='))]

                    vMsg2 = line[vpos_msg2: (vpos_msg2 + vqtd_char_msg2 - 1)]

                    vMsg = vMsg1 + ", " + vMsg2

                    vVPN_Tunnel = "-"

                    # Review the result in order to select only the Peers
                    vpos_other2 = vLocal_Peer1.find('=')
                    vqtd_char_local = len(vLocal_Peer1) - vpos_other2

                    vpos_other3 = vRemote_Peer1.find('=')
                    vqtd_char_remote = len(vRemote_Peer1) - vpos_other3

                    vLocal_Peer = vLocal_Peer1[(vpos_other2 + 1): ((vpos_other2 + 1) + vqtd_char_local - 2)]

                    vLocal_Peer = vLocal_Peer.rstrip(' ')
                    vLocal_Peer = vLocal_Peer.rstrip(')')

                    vRemote_Peer = vRemote_Peer1[(vpos_other3 + 1):
                        ((vpos_other3 + 1) + vqtd_char_remote - 2)]

                    vRemote_Peer = vRemote_Peer.rstrip(' ')
                    vRemote_Peer = vRemote_Peer.rstrip(')')

                # -------------------------------------------------------
                # Check if the line contains 'IKE Phase-2: Failed to match'
                # vMsgID = 8
                # -------------------------------------------------------
                elif vMsgID == 8:

                    vpos_other1 = line.find('[p2_remote_proxy_id=')
                    vpos_local = line.find('local ip:')
                    vpos_remote = line.find('remote peer ip:')

                    vqtd_char_msg1 = vpos_other1 - vpos_msg1
                    vqtd_char_local = vpos_remote - vpos_local
                    vqtd_char_remote = len(line) - vpos_remote

                    vMsg = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1)]
                    vLocal_Peer = line[(vpos_local + len('local ip: ')): (
                       (vpos_local + len('local ip: ')) + vqtd_char_local - len('local ip: ') - 2)]
                    vRemote_Peer = line[(vpos_remote + len('remote peer ip:')):
                       ((vpos_remote + len('remote peer ip:')) + len(line))]

                    vVPN_Tunnel = "-"

                # -------------------------------------------------------
                # Check if the line contains 'IKE Phase-2 Failure' or 'KMD_VPN_PV_PHASE2'
                # vMsgID = 9 or vMsgID = 10
                # -------------------------------------------------------
                elif vMsgID == 9 or vMsgID == 10:

                    vpos_msg2 = line.find('[spi=')
                    vpos_local = line.find('src_ip=')
                    vpos_remote = line.find('dst_ip=')

                    vqtd_char_msg1 = vpos_msg2 - vpos_msg1
                    vqtd_char_msg2 = vpos_local - vpos_msg2
                    vqtd_char_local = vpos_remote - vpos_local
                    vqtd_char_remote = len(line) - vpos_remote

                    vMsg = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1)]
                    vMsg2 = line[vpos_msg2: (vpos_msg2 + vqtd_char_msg2)]
                    vLocal_Peer = line[(vpos_local + len('src_ip=')): (
                        (vpos_local + len('src_ip=')) + vqtd_char_local - len('src_ip=') - 2)]

                    vRemote_Peer = line[(vpos_remote + len('dst_ip=')): (
                                (vpos_remote + len('dst_ip=')) + vqtd_char_remote - len('dst_ip=') - 1)]

                    vVPN_Tunnel = "-"

                # -------------------------------------------------------
                # Check if the line contains 'IKE Phase-2: Negotiations failed'
                # vMsgID = 11
                # -------------------------------------------------------
                elif vMsgID == 11:

                    vpos_local = line.find('Local gateway:')
                    vpos_remote = line.find('Remote gateway:')

                    vqtd_char_msg1 = vpos_local - vpos_msg1
                    vqtd_char_local = vpos_remote - vpos_local
                    vqtd_char_remote = len(line) - vpos_remote

                    vMsg = line[vpos_msg1: (vpos_msg1 + vqtd_char_msg1)]
                    vLocal_Peer = line[(vpos_local + len('Local gateway: ')): ((vpos_local + len('Local gateway: ')) +
                                vqtd_char_local - len('Local gateway: ') - 2)]
                    vRemote_Peer = line[(vpos_remote + len('Remote gateway: ')): (
                                (vpos_remote + len('Remote gateway: ')) + vqtd_char_remote - len('Remote gateway: '))]

                    vVPN_Tunnel = "-"

                # ---------------------------------------------------------------------

            if vpos_msg1 != -1:

                # Loading the data
                # print "Inserting data into table"
                g_msg.append("Inserting data into table")

                try:

                    to_db = [vLogDate, vLocal_Peer, vRemote_Peer, vVPN_Tunnel, vMsg]
                    curs.execute("INSERT INTO KMD (DATE, LOCAL, REMOTE, TUNNEL, MESSAGE) VALUES(?, ?, ?, ?, ?);",
                                 to_db)
                    conn.commit()

                except sqlite3.Error as e:
                    g_msg.append(e)
                    print (e)
                    exit()

    conn.commit()
    conn.close()

#    print "Data uploaded successfully"
    g_msg.append("Data uploaded successfully")

    f.close()
except OSError as e:
    g_msg.append(e)
    print (e)
    exit()
finally:
    vpn_log.f_log(g_msg)

# print "All Done. Tks for your preference."
