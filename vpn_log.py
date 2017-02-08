__author__ = 'Alexandre S. Cezar - acezar@juniper.net - PyEZ, Database and parsers'
# __author__ = 'Rosemary Chan - Parsers, GUI and log function'

import os
import subprocess
import platform


def f_log(vlist):

    vfile = "vpn_log.txt"

    with open(vfile, 'w') as pTxtFile:

        for str_line in vlist:
            print str_line
            pTxtFile.write(str_line + chr(10))


        # for row in result:
        #     vlinha = row[0] + ", " + row[1] + ", " + row[2] + ", " + row[3] + ", " + row[4] + chr(10)

    pTxtFile.close()

    # -------------------------------------------------------------
    # Open Log File
    # -------------------------------------------------------------
#    if platform.system() == "Windows":
#        os.system('vpn_log.txt')
#    else:
#        subprocess.call(['open', '-a', 'TextEdit', 'vpn_log.txt'])

