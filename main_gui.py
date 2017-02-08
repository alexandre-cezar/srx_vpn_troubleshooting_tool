from Tkinter import *
import Tkinter
import tkFont
import ttk
import sqlite3
import os
import subprocess
import platform
import vpn_log

# Global Variables definition
global g_input_IP
global g_input_username
global g_input_password
global container
global vsearch
global vsql_geral
global tree_columns


# -------------------------------------------------------------------------------------------
# f_enter_key
# Start an action when the enter key is pressed
# -------------------------------------------------------------------------------------------
def f_enter_key(event=None):

    if root.focus_get().winfo_name() == "btn_connect":
        f_connect()
    elif root.focus_get().winfo_name() == "btn_exit1":
        f_exit_1()
    elif root.focus_get().winfo_name() == "btn_filter":
        f_filter_type()
    elif root.focus_get().winfo_name() == "fld_Search":
        f_filter_type()
    elif root.focus_get().winfo_name() == "btn_open":
        f_openfile()
    elif root.focus_get().winfo_name() == "btn_save":
        f_savequery()
    elif root.focus_get().winfo_name() == "btn_exit2":
        f_exit_2()

# -------------------------------------------------------------------------------------------
# f_center_window
# Center the current window
# -------------------------------------------------------------------------------------------
def f_center_window(width=300, height=200):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

# -------------------------------------------------------------------------------------------
# f_connect
# Check if connection information was filled, connect and retrieve log information
# -------------------------------------------------------------------------------------------
def f_connect():

    g_input_IP = vSRXIP.get()
    g_input_username = vUsername.get()
    g_input_password = vPassword.get()

    if g_input_IP == "" or g_input_username == "" or g_input_password == "":

        ttk.Label(mainframe, text="Please fill all the fields above.", fg="red").grid(column=2, row=9, columnspan=4, sticky=W)

    else:

        execfile("vpn_troubleshooting.py")
        f_list_vpn()
        root.title("SRX VPN Troubleshooting Tool - SRX MGMT IP : " + g_input_IP)

# -------------------------------------------------------------------------------------------
# f_list_vpn - Assemble the result screen
# -------------------------------------------------------------------------------------------
def f_list_vpn():

    g_msg = list()

    f_multicolumnlistbox()

# -------------------------------------------------------------------------------------------
# f_exit_1 - Exit from first screen
# -------------------------------------------------------------------------------------------
def f_exit_1 ():
    exit()

# -------------------------------------------------------------------------------------------
# f_exit_2 - Exit from second screen, deleting files and DBs created
# -------------------------------------------------------------------------------------------
def f_exit_2():
    try:
        conn = sqlite3.connect('kmd.db')
        curs = conn.cursor()
        curs.executescript("""
            DROP TABLE IF EXISTS KMD
            """)  # drop existing table
        # g_msg.append("Database dropped successfully")
    except sqlite3.Error as e:
        # g_msg.append(e)
        # print (e)
        exit()

    try:
        os.remove("kmd.txt")
    except OSError as e:
        # g_msg.append("Text file deleted")
        # g_msg.append(e)
        # print (e)
        exit()

    try:
        os.remove("kmd.db")
    except OSError as e:
        # g_msg.append("DB file deleted")
        # g_msg.append(e)
        # print (e)
        exit()

    exit()

# -------------------------------------------------------------------------------------------
# sortby - Sort tree contents when a column is clicked on
# -------------------------------------------------------------------------------------------
def sortby(tree, col, descending):

    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)
    # switch the heading so that it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))

# -------------------------------------------------------------------------------------------
# f_filter_type - Checkbox Action - call the filter function
# -------------------------------------------------------------------------------------------
def f_filter_type():

    sqlcode("2")

# -------------------------------------------------------------------------------------------
# f_multicolumnlistbox - main function to recreate the window to show the log information
# -------------------------------------------------------------------------------------------
def f_multicolumnlistbox():

    _setup_widgets()
    _build_tree()
    sqlcode("1")

    root.update()
    f_center_window(root.winfo_reqwidth(), root.winfo_reqheight())

# -------------------------------------------------------------------------------------------
# _setup_widgets - Recreate the window structure
# -------------------------------------------------------------------------------------------
def _setup_widgets():
    global tree

    container.grid(column=0, row=0, sticky=(N, W, E, S))
    container.columnconfigure(0, weight=1)
    container.rowconfigure(0, weight=1)

    # Row=0, Col=0
    ttk.Label(container, text="").grid(row=0, column=0)

    # Row=3, Col=0
    ttk.Label(container, text="").grid(row=3,  column=0)

    # Row=3, Col=1
    ckb_error = ttk.Checkbutton(container, text="Error messages", variable=vCheckError, command=f_filter_type)
    ckb_error.grid(row=3, column=1, sticky=W)

    # Row=3, Col=3
    ckb_success = ttk.Checkbutton(container, text="Success messages", variable=vCheckSuccess, command=f_filter_type)
    ckb_success.grid(row=3, column=3, sticky=W)

    # Row=3, Col=17
    ttk.Label(container, text="Search : ").grid(row=3, column=17, sticky=E)
    vsearch_entry = ttk.Entry(container, width=60, textvariable=vsearch, name="fld_Search")
    # Row=3, Col=18-20
    vsearch_entry.grid(row=3, column=18, columnspan=3, sticky=W)

    # Row=3, Col=21
    ttk.Button(container, text="Filter", name="btn_filter", command=f_filter_type).grid(row=3, column=21, sticky=W)

    # Row=4, Col=18
    Radiobutton(container, text="Local Peer", variable=vopt_search, value=1).grid(row=4, column=18, sticky=W)
    # Row=4, Col=19
    Radiobutton(container, text="Remote Peer", variable=vopt_search, value=2).grid(row=4, column=19, sticky=W)
    # Row=4, Col=20
    Radiobutton(container, text="Message", variable=vopt_search, value=3).grid(row=4, column=20, sticky=W)

    vopt_search.set(3)

    # v.set(3)

    # Row=6, Col=0
    ttk.Label(container, text="       ").grid(row=6,  column=0)

    # Row=6, Col=1
    tree = ttk.Treeview(columns=tree_columns, show="headings", height=20)
    tree.grid(row=6, column=1, columnspan=30, sticky='NSEW', in_=container)

    # Row=6, Col=31
    vsb = ttk.Scrollbar(orient="vertical", command=tree.yview)
    vsb.grid(row=6, column=31, sticky='NS', in_=container)

    # Row=7, Col=1
    hsb = ttk.Scrollbar(orient="horizontal", command=tree.xview)
    hsb.grid(row=7, column=1, columnspan=30, sticky='NSEW', in_=container)

    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Row=6, Col=32
    ttk.Label(container, text="       ").grid(row=6,  column=32)

    # Row=11, Col=0
    ttk.Label(container, text="").grid(row=11,  column=0)

    # Row=12, Col=1
    ttk.Button(container, text="Open full Log file", name="btn_open",
               command=f_openfile).grid(row=12, column=1, sticky=W)
    # Row=12, Col=2
    ttk.Button(container, text="Save query results", name="btn_save",
               command=f_savequery).grid(row=12, column=2, sticky=W)
    # Row=12, Col=30
    ttk.Button(container, text="Exit", name="btn_exit2",
               command=f_exit_2).grid(row=12, column=30, sticky=E)

    # Row=13, Col=0
    ttk.Label(container, text="").grid(row=13, column=0)

    tree.column("Date",        minwidth=0, width=100, stretch=0)
    tree.column("Local Peer",  minwidth=0, width=200, stretch=0)
    tree.column("Remote Peer", minwidth=0, width=200, stretch=0)
    tree.column("VPN Tunnel",  minwidth=0, width=100, stretch=0)
    tree.column("Message",     minwidth=0, width=600, stretch=0)

    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)

# -------------------------------------------------------------------------------------------
# _build_tree - create the treeview structure
# -------------------------------------------------------------------------------------------
def _build_tree():

    for col in tree_columns:
        tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
        # adjust the column's width to the header string
        tree.column(col, width=tkFont.Font().measure(col.title())+10, anchor="c")

# -------------------------------------------------------------------------------------------
# sqlcode - Retrieve log lines according the filter
# Parameters:
#   1 - Retrieve all lines (when mounting the screen at the first time)
#   2 - Retrieve Success and/or Error messages (according to user selection)
#       Retrieve lines with search keyword information (as typed by the user)
# -------------------------------------------------------------------------------------------
def sqlcode(vtipo):

    db = sqlite3.connect('kmd.db')
    cursor = db.cursor()
    sql1 = "Select * FROM KMD"

    if vtipo == "2":

        if vCheckError.get() == 1 and vCheckSuccess.get() == 1 and vsearch.get() == "":
            pass

        else:
            if vCheckError.get() == 1 or vCheckSuccess.get() == 1 or vsearch.get() != "":
                sql1 += " WHERE"

                if not (vCheckError.get() == 1 and vCheckSuccess.get() == 1):

                    if vCheckError.get() == 1:

                        sql1 += "  ( MESSAGE LIKE '%KMD_DPD_PEER_DOWN%' "
                        sql1 += " OR MESSAGE LIKE '%KMD_VPN_TS_MISMATCH%' "
                        sql1 += " OR MESSAGE LIKE '%KMD_VPN_DOWN_ALARM_USER%' "
                        sql1 += " OR MESSAGE LIKE '%IKE negotiation failed with error%' "
                        sql1 += " OR MESSAGE LIKE '%IKE Phase-2: Failed%' "
                        sql1 += " OR MESSAGE LIKE '%IKE Phase-2 Failure%' "
                        sql1 += " OR MESSAGE LIKE '%IKE Phase-2: Negotiations failed%' ) "

                    elif vCheckSuccess.get() == 1:

                        sql1 += "  ( MESSAGE LIKE '%IKE negotiation successfully completed%' "
                        sql1 += " OR MESSAGE LIKE '%KMD_PM_SA_ESTABLISHED%' "
                        sql1 += " OR MESSAGE LIKE '%KMD_VPN_UP_ALARM_USER%' "
                        sql1 += " OR MESSAGE LIKE '%Phase-1 [responder] done%' ) "

                if vsearch.get() != "":

                    if vCheckError.get() == 1 or vCheckSuccess.get() == 1:
                        if not (vCheckError.get() == 1 and vCheckSuccess.get() == 1):
                            sql1 += " AND "

                    if vopt_search.get() == 0:
                        vopt_search.set(3)

                    if vopt_search.get() == 1:
                        sql1 += " LOCAL LIKE '%" + vsearch.get() + "%' "

                    elif vopt_search.get() == 2:
                        sql1 += " REMOTE LIKE '%" + vsearch.get() + "%' "

                    elif vopt_search.get() == 3:
                        sql1 += " MESSAGE LIKE '%" + vsearch.get() + "%' "

    sql1 += " order by DATE DESC"

    cursor.execute(sql1)
    result = cursor.fetchall()

    for i in tree.get_children():
        tree.delete(i)

    for item in result:

        tree.insert('', 'end', values=item)
        # adjust column's width if necessary to fit each value
        for ix, val in enumerate(item):
            # ix = 0 -> DATE
            # ix = 1 -> LOCAL PEER
            # ix = 2 -> REMOTE PEER
            # ix = 3 -> VPN TUNNEL
            # ix = 4 -> MESSAGE

            if ix < 4:
                col_w = tkFont.Font().measure(val) + 5
                tree.column(tree_columns[ix], anchor="c")
            else:
                col_w = tkFont.Font().measure(val)
                tree.column(tree_columns[ix], anchor="w")

            if col_w > 450:
                col_w = 450
                tree.column(tree_columns[ix], width=col_w)

            if tree.column(tree_columns[ix], width=None) < col_w:
                tree.column(tree_columns[ix], width=col_w)

    cursor.close()

    vsql_geral.set(sql1)

# -------------------------------------------------------------------------------------------
# f_openfile - Open the full log file
# -------------------------------------------------------------------------------------------
def f_openfile():
    if platform.system() == "Windows":
        os.system('kmd.txt')
    else:
        subprocess.call(['open', '-a', 'TextEdit', 'kmd.txt'])

# -------------------------------------------------------------------------------------------
# f_savequery - Save the current log lines in a txt file and open it
# -------------------------------------------------------------------------------------------
def f_savequery():

    vtxt_queryfile = "kmd_filtered.txt"

    db = sqlite3.connect('kmd.db')
    cursor = db.cursor()

    cursor.execute(vsql_geral.get())
    result = cursor.fetchall()

    with open(vtxt_queryfile, 'w') as pTxtFile:

        for row in result:
            vlinha = row[0] + ", " + row[1] + ", " + row[2] + ", " + row[3] + ", " + row[4] + chr(10)
            pTxtFile.write(vlinha)

    pTxtFile.close()

    cursor.close()

    if platform.system() == "Windows":
        os.system('kmd_filtered.txt')
    else:
        subprocess.call(['open', '-a', 'TextEdit', 'kmd_filtered.txt'])

# ---------------------------------------------------------------------------
# MAIN CODE
# ---------------------------------------------------------------------------

root = Tk()
root.title("SRX VPN Tool")

mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

container = ttk.Frame(root)


vCheckError = IntVar()
vCheckSuccess = IntVar()
vopt_search = IntVar()

vsearch = StringVar()
vsql_geral = StringVar()

vSRXIP = StringVar()
vUsername = StringVar()
vPassword = StringVar()
vFilename = StringVar()

tree_columns = ("Date", "Local Peer", "Remote Peer", "VPN Tunnel", "Message")

vSRXIP_entry = ttk.Entry(mainframe, width=12, textvariable=vSRXIP)
vSRXIP_entry.grid(column=3, row=2, sticky=(W, E))

vUser_entry = ttk.Entry(mainframe, width=12, textvariable=vUsername)
vUser_entry.grid(column=3, row=3, sticky=(W, E))

vPass_entry = ttk.Entry(mainframe, width=12, show="*", textvariable=vPassword)
vPass_entry.grid(column=3, row=4, sticky=(W, E))

ttk.Button(mainframe, text="Connect", name="btn_connect", command=f_connect).grid(column=3, row=8, sticky=E)
ttk.Button(mainframe, text="Exit",    name="btn_exit1",   command=f_exit_1).grid(column=2, row=8, sticky=W)

ttk.Label(mainframe, text="SRX MGMT IP : ").grid(column=2, row=2, sticky=E)
ttk.Label(mainframe, text="Username : ").grid(column=2, row=3, sticky=E)
ttk.Label(mainframe, text="Password : ").grid(column=2, row=4, sticky=E)

ttk.Label(mainframe, text="").grid(column=1, row=5, sticky=W)
ttk.Label(mainframe, text="").grid(column=1, row=1, sticky=W)
ttk.Label(mainframe, text="").grid(column=1, row=8, sticky=W)
ttk.Label(mainframe, text="").grid(column=1, row=9, sticky=W)
ttk.Label(mainframe, text="").grid(column=4, row=9, sticky=W)

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=3, pady=3, ipadx=5)

root.update()
f_center_window(root.winfo_width(), root.winfo_height())

root.bind('<Return>', f_enter_key)

vSRXIP_entry.focus()

root.mainloop()
