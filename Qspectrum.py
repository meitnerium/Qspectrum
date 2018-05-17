import sqlite3
from tkinter.filedialog import askopenfilename, askopenfile, asksaveasfilename
from tkinter import *
from tkinter import messagebox
import os
import io
from matplotlib.ticker import MultipleLocator

from jcamp import JCAMP_reader
import matplotlib.pyplot as plt
import numpy as np

# TODO : search
"""
pyinstaller --onefile --windowed Qspectrum.py
"""

ver = '1.0'
dbfile = 'spectra.db'

pertable=(['H','He','Li','Be','B','C','N','O','F','Ne'])

class MainWin(object):
    def __init__(self,window):
        self.window = window
        self.window.wm_title("STAV")
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Create a database", command=createdb)
        filemenu.add_command(label="Open a database", command=opendb)
        filemenu.add_command(label="Exit", command=window.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        window.config(menu=menubar)
        lmolname = Label(window,text="Molecule name")
        lmolname.grid(row=0, column=0)
        molname_text=StringVar()
        emolname = Entry(window,textvariable=molname_text)
        emolname.grid(row=0, column=1)


        lcas = Label(window,text="CAS")
        lcas.grid(row=0, column=2)
        cas_text=StringVar()
        ecas=Entry(window,textvariable=cas_text)
        ecas.grid(row=0, column=3)

        s1 = Button(text = 'Search')
        s1.grid(row=1, column=3)

        add_button = Button(text = 'Add a molecule',command=add_mol)
        add_button.grid(row=1, column=0)

        view_button = Button(text = 'View',command=view)
        view_button.grid(row=1, column=2)


        delete_button = Button(text = 'Delete',command=delete)
        delete_button.grid(row=1, column=1)

        list1=Listbox(window, height=20, width=80)
        list1.bind('<Double-1>', lambda x: view())
        list1.grid(row=2, column=0, rowspan=20, columnspan=4)
        sb1=Scrollbar(window)
        sb1.grid(row=2, column=5, rowspan=20, sticky="ns")


        # TODO : Create input from mol view
        # def createinput():
        #    print("Create input")

        # create a popup menu
        list1rbmenu = Menu(window, tearoff=0)
        list1rbmenu.add_command(label="View", command=view)
        list1rbmenu.add_command(label="Delete", command=delete)
        # list1rbmenu.add_command(label="Create Input", command=createinput)

        list1.bind("<Button-3>", self.popup)

        def popup(self,event):
            list1rbmenu.post(event.x_root, event.y_root)
class Molecule:
    def __init__(self, geom, id, name, cas, charge=0, multiplicity=1):
        self.charge = charge
        self.multiplicity = multiplicity
        self.geom = geom
        self.id = id
        self.name = name
        self.cas = cas


class Spectra:
    def __init__(self, id, molid, x, y, title):
        self.id = id
        self.molid = molid
        self.x = x
        self.y = y
        self.title = title


class Calcul:
    def __init__(self,molid, title, funct, basis, freq, irintens, anharmfreq=[], anharmintens=[]):
        self.molid = molid
        self.funct = funct
        self.basis = basis
        self.freq = freq
        self.irintens = irintens
        self.anharmfreq = anharmfreq
        self.anharmintens = anharmintens
        self.title = title

class Figure:
    def __init__(self):
        self.win = Toplevel(window)
# class Figure:
#    def __init__(self,id,numspectra=3):
#        self.numspectra = numspectra
#        self.id = id
#        self.win = Toplevel(window)
#        print('new figure')
#        self.buttonlist = []
#        for i in range(numspectra):
#            buttonchoose = Menubutton(self.win, text='Spectra')
#            buttonchoose.grid(row=i, column=0)
#            buttonchoose.menu = Menu(buttonchoose)
#            buttonchoose["menu"] = buttonchoose.menu
#            buttonchoose.menu.add_command(label = "Spectra", underline = 0, command = lambda: self.choosespectra(self.buttonlist[i]))
#            buttonchoose.menu.add_command(label = "Calcul", underline = 0, command = lambda: self.choosecalc(i))
#
#            buttonchoose2 = Menubutton(self.win, text='')
#            buttonchoose2.grid(row=i, column=1)
#            buttonadd = Button(self.win, text='Add figure')
#            buttonadd.grid(row=i,column=2)
#            self.buttonlist.append(buttonadd)
#
#    def choosecalc(self,i):
#            print("btnchoosecalc "+str(i))
#
#    def choosespectra(self,i):
#        print("choosespectra "+str(i))
#
#    def show(self):
#        plt.show()


class Database:
    def __init__(self):
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)
        conn = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS molecule (id INTEGER PRIMARY KEY, name text, cas text, geom text, echarge INTEGER, emult INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS calcul (id INTEGER PRIMARY KEY, molid INTEGER, log text,vib array, intensir array, anharmfreq array, anharmintens array,funct TEXT, basis TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS spectra (id INTEGER PRIMARY KEY, molid INTEGER, x arr, y arr, title text)")
        conn.commit()
        conn.close()

    def addmol(self):
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("INSERT INTO molecule VALUES (NULL,?,?)", (emolname.get(),ecas.get()))
        conn.commit()
        conn.close()

    def insert(self,molid,x,y,title): #,x,y,cas='111-11-11'
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)
        #try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("INSERT INTO spectra VALUES (NULL,?,?,?,?)", (molid,x,y,title))
        conn.commit()
        print(conn.Error)
        conn.close()

    def insertcalc(self,molid,data,freqanharm,intensanharm,basis,funct,log): #,x,y,cas='111-11-11'
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)
        #try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        # TODO add scan for func and basis
        cur.execute("INSERT INTO calcul VALUES (NULL,?,?,?,?,?,?,?,?)", (molid,log,data.vibfreqs,data.vibirs,freqanharm,intensanharm,funct,basis))
        conn.commit()
        print(conn.Error)
        # except:
        #    print("Error IN SPECTRA INPUT ")
        #    sys.exit(1)
        # finally:
        #    if conn:
        conn.close()
        # self.view()

    def molview(self):
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("SELECT * FROM molecule")
        rows = cur.fetchall()
        conn.close()
        return rows

    def calcview(self,molid):
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("SELECT * FROM calcul where molid= '"+str(molid)+"'")
        rows = cur.fetchall()
        conn.close()
        return rows

    def getmol(self,id):
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("SELECT * FROM molecule WHERE id="+str(id))
        rows = cur.fetchall()
        conn.close()
        return rows

    def delmol(self,id):
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        print("testttttttt : " +str(id))
        cur.execute("DELETE FROM molecule WHERE id = '"+str(id)+"'")
        conn.commit()
        rows = cur.fetchall()
        conn.close()

    def view(self,molid):
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)
        conn=sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("SELECT * FROM spectra where molid = '"+str(molid)+"'")
        rows = cur.fetchall()
        conn.close()
        return rows


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def savemol():
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    print("TTTTTEEEEEEESSSSSSSTTT3 : "+emolname.get())
    cur.execute("SELECT * FROM molecule WHERE name = '"+emolname.get()+"'")
    rows = cur.fetchall()
    print(cur.rowcount)


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


def popup_spectra(event):
    global listspectrabmenu
    listspectrabmenu.post(event.x_root, event.y_root)


def addfig(list_spectra,num,menu_button,type):
    if num == 1:
        color = "red"
    elif num == 2:
        color = "blue"
    elif num == 3:
        color = "black"
    if menu_button['text'] == 'Spectra':
        # global figure
        # figure = Toplevel(window)
        print("add to fig 1")
        # plt.figure(num=None, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
        ax = plt.subplot(3, 1, num)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        minorlocator = MultipleLocator(100)
        ax.xaxis.set_minor_locator(minorlocator)
        plt.yticks([0,1])
        # plt.xticks([])
        plt.axis([400,4000,0,1.1])
        freqrange = np.arange(400,4000,1)
        text=list_spectra.curselection()
        print('show spectra '+str(text[0]))
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("SELECT * FROM spectra WHERE id ='"+str(list_spectra_id[text[0]])+"'")
        rows = cur.fetchall()
        print("test numrow "+str(cur.rowcount))
        conn.close()
        for row in rows:
            test_x=np.array(convert_array(row[2]))
            test_y=np.array(convert_array(row[3]))
            test_y=normalize(test_y)
            plt.plot(test_x,test_y,color)
            minorLocator = MultipleLocator(100)
            ax.xaxis.set_minor_locator(minorLocator)
            plt.yticks([0, 1])
    elif menu_button['text'] == 'Calcul':
        print('Calcul')
        text=list_spectra.curselection()
        print("show calcul "+str(text[0]))
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)
        conn=sqlite3.connect(dbfile)
        cur=conn.cursor()
        cur.execute("SELECT * FROM calcul WHERE id ='"+str(list_calcul_id[text[0]])+"'")
        rows = cur.fetchall()
        print("test numrow "+str(cur.rowcount))
        for row in rows:
            print("enconre un test")
            ax = plt.subplot(3,1,num)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            # ax.spines['bottom'].set_visible(False)
            ax.yaxis.set_ticks_position('left')
            ax.xaxis.set_ticks_position('bottom')
            freqrange=np.arange(400,4000,1)
            if type == "harm":
                GAUSSIANspectra = mkspectra(freqrange, convert_array(row[3]),convert_array(row[4]), 10)
            elif type == "anharm":
                GAUSSIANspectra = mkspectra(freqrange, convert_array(row[5]),convert_array(row[6]), 10)
            NGAUSS=normalize(GAUSSIANspectra)
            plt.plot(freqrange,NGAUSS,color)
            minorLocator = MultipleLocator(100)
            ax.xaxis.set_minor_locator(minorLocator)
            #plt.ylabel("Normalized absorbance (a.u.)")
            plt.yticks([0, 1])
    if num == 3:
        plt.xlabel("Wavenumber $(cm^{-1})$")
        TXT=plt.figtext(0.07,0.70,"Normalized absorbance (arb. u.)")
        TXT.set_rotation('90')
    plt.show()

def updatelistspectra(list_spectra,molid):
    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute("SELECT * FROM spectra WHERE molid ='"+str(molid)+"'")
    rows = cur.fetchall()
    print("test numrow in view " + str(cur.rowcount))
    conn.close()
    global list_spectra_id
    list_spectra_id = []
    for row in rows:
        list_spectra_id.append(str(row[0]))
        list_spectra.insert(END,str(row[0])+" "+str(row[1])+" "+str(row[4]))


def getlog(list_spectra,menu_button):
    text=list_spectra.curselection()
    print("Get Log "+str(list_calcul_id[text[0]]))
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute("SELECT log FROM calcul WHERE id ='"+str(list_calcul_id[text[0]])+"'")
    rows = cur.fetchall()
    for row in rows:
        fname = asksaveasfilename()
        print('fname = '+fname)
        f = open(fname, 'w')
        f.write(row[0])
        f.close()


def view():
    global listspectrabmenu
    global listcalculmenu
    text = list1.curselection()
    print(text[0])
    for row in db.getmol(text[0]+1):
        emolname.delete(0,END)
        emolname.insert(0,row[1])
        ecas.delete(0,END)
        ecas.insert(0,row[2])
    add_button.grid_forget()#config(text='Save')
    delete_button.grid_forget()
    save_button = Button(text = 'Save', command=savemol)
    save_button.grid(row=1, column=0)
    s1.grid_forget()#config(text='back')
    view_button.grid_forget()
    list1.grid_forget()
    listspectrabmenu = Menu(window, tearoff=0)
    listspectrabmenu.add_command(label="Add to fig 1", command=lambda: addfig(list_spectra,1,menu_button,""))
    listspectrabmenu.add_command(label="Add to fig 2", command=lambda: addfig(list_spectra,2,menu_button,""))
    listspectrabmenu.add_command(label="Add to fig 3", command=lambda: addfig(list_spectra,3,menu_button,""))

    listcalculmenu = Menu(window, tearoff=0)
    listcalculmenu.add_command(label="Get Log", command=lambda: getlog(list_spectra,menu_button))
    #listcalculmenu.add_command(label="Make Input", command=lambda: makeinput(list_spectra,menu_button))
    listcalculmenu.add_command(label="Add Harm to fig 1", command=lambda: addfig(list_spectra,1,menu_button,"harm"))
    listcalculmenu.add_command(label="Add Harm to fig 2", command=lambda: addfig(list_spectra,2,menu_button,"harm"))
    listcalculmenu.add_command(label="Add Harm to fig 3", command=lambda: addfig(list_spectra,3,menu_button,"harm"))
    listcalculmenu.add_command(label="Add AnHarm to fig 1", command=lambda: addfig(list_spectra,1,menu_button,"anharm"))
    listcalculmenu.add_command(label="Add AnHarm to fig 2", command=lambda: addfig(list_spectra,2,menu_button,"anharm"))
    listcalculmenu.add_command(label="Add AnHarm to fig 3", command=lambda: addfig(list_spectra,3,menu_button,"anharm"))



    list_spectra = Listbox(window, height=20, width=80)
    list_spectra.bind('<Double-1>', lambda x: show_spectra(list_spectra))
    list_spectra.bind('<Button-3>', popup_spectra)
    list_spectra.grid(row=2, column = 0, rowspan = 20, columnspan = 4)
    menu_button = Menubutton(window, text='Spectra')
    menu_button.grid(row = 1, column = 2)
    menu_button.menu = Menu(menu_button)
    menu_button["menu"] = menu_button.menu
    spectravar = IntVar()
    calculvar = IntVar()
    menu_button.menu.add_command(label = "Spectra", underline = 0, command = lambda: spectracmd(menu_button,list_spectra,addspectra_button,text[0]+1))
    menu_button.menu.add_command(label = "Calcul", underline = 0, command= lambda: calculcmd(menu_button,list_spectra,addspectra_button,text[0]+1))
    #menu_button.after(1, lambda x: print("this is a test"))
    sb_spectra=Scrollbar(window)
    sb_spectra.grid(row = 2, column = 5, rowspan = 20, sticky = "ns")
    # list1.delete(0,END)
    updatelistspectra(list_spectra,text[0]+1)
    sb1.grid_forget()
    addspectra_button = Button(text='Add spectra', command=lambda: add_spectra(text[0]+1, list_spectra))
    addspectra_button.grid(row=1, column=1)
    backbutton = Button(text='back', command=lambda: back(backbutton,save_button,addspectra_button,list_spectra,sb_spectra,menu_button))
    backbutton.grid(row=1, column=4)
    deletebutton = Button(text='delete', command= lambda: deletespectra(list_spectra))
    deletebutton.grid(row=1, column=3)


def spectracmd(menu_button,list_spectra,addspectra_button,molid):
    print("spectracmd")
    list_spectra.delete(0,END)
    list_spectra.bind('<Double-1>', lambda x: show_spectra(list_spectra))
    list_spectra.bind('<Button-3>', popup_spectra)
    menu_button.config(text = 'Spectra')
    updatelistspectra(list_spectra,molid)


def calculcmd(menu_button,list_spectra,addspectra_button,molid):
    print("calculcmd")
    menu_button.config(text = 'Calcul')
    list_spectra.delete(0,END)
    list_spectra.bind('<Double-1>', lambda x: show_calcul(list_spectra))
    list_spectra.bind('<Button-3>', popup_calcul)
    global list_calcul_id
    list_calcul_id = []
    for row in db.calcview(molid):
        print("test2")
        print(row)
        list_calcul_id.append(row[0])
        list_spectra.insert(row[0],str(row[0])+" "+row[8]+" "+row[7])

    addspectra_button.config(text = 'Add Calcul', command= lambda: add_calcul(molid))


def popup_calcul(event):
    global listcalculmenu
    listcalculmenu.post(event.x_root, event.y_root)


def show_calcul(list_spectra):

    text=list_spectra.curselection()
    print("show calcul "+str(text[0]))
    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)
    conn=sqlite3.connect(dbfile)
    cur=conn.cursor()
    cur.execute("SELECT * FROM calcul WHERE id ='"+str(text[0]+1)+"'")
    rows = cur.fetchall()
    print("test numrow "+str(cur.rowcount))
    for row in rows:
        print("enconre un test")
        ax = plt.subplot(1,1,1)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        freqrange=np.arange(400,4000,1)
        GAUSSIANspectra = mkspectra(freqrange, convert_array(row[2]),convert_array(row[3]), 10)
        NGAUSS=normalize(GAUSSIANspectra)
        plt.plot(freqrange,NGAUSS)
        minorLocator = MultipleLocator(100)
        ax.xaxis.set_minor_locator(minorLocator)
        plt.xlabel("Wavenumber $(cm^{-1})$")
        plt.ylabel("Normalized absorbance (a.u.)")
        plt.yticks([0, 1])
        plt.show()


def mkspectra(freqx,vibfreqs,iract,r):
    """
    mkspectra create a IR spectra with lorentz function correlated to vibrationnal frequency value with iract amplitude
    :param freqx: frequence vector used to create the spectra
    :param vibfreqs: theoritical vibrationnal frequency
    :param amp: Ir activities of each vibrationnal frequency
    :return: Absorbance for each freqx value
    """
    print(freqx)
    spectra=np.zeros(len(freqx))
    for i in range(len(freqx)):
        print(i,freqx[i])
        spectra[i]=0

        for j in range(len(vibfreqs)):
            #TODO calculate correctly the amplitude (amp[i])
            spectra[i]=spectra[i]+lorentz(r,freqx[i],vibfreqs[j])*iract[j]
            #print(r,freqx[i],vibfreqs[j],iract[j])
    return spectra


def lorentz(r, x, x0):
    """
    :param r: mid-height witdh of the lorentz function
    :param x: x-value for the evaluation
    :param x0: abscice of the maximum of the lorentz function
    :return: Amplitude of the Lorentz at the x value
    """
    under=(r/2)**2+(x-x0)**2
    l=r/(2*np.pi)*1/under
    return(l)


def normalize(vec):
    output=vec/np.max(vec)
    return output


def show_spectra(list_spectra):
    text=list_spectra.curselection()
    print('show spectra '+str(text[0]))
    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)
    conn=sqlite3.connect(dbfile)
    cur=conn.cursor()
    cur.execute("SELECT * FROM spectra WHERE id ='"+str(text[0]+1)+"'")
    rows = cur.fetchall()
    print("test numrow "+str(cur.rowcount))
    conn.close()
    for row in rows:
        print("enconre un test")
        ax = plt.subplot(1,1,1)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        test_x=np.array(convert_array(row[2]))
        test_y=np.array(convert_array(row[3]))
        test_y=normalize(test_y)
        plt.plot(test_x,test_y)
        minorLocator = MultipleLocator(100)
        ax.xaxis.set_minor_locator(minorLocator)
        plt.xlabel("Wavenumber $(cm^{-1})$")
        plt.ylabel("Normalized absorbance (a.u.)")
        plt.yticks([0, 1])
        plt.show()


def back(backbutton,save_button,addspectra_button,list_spectra,sb_spectra,menu_button):
    backbutton.grid_forget()
    save_button.grid_forget()
    addspectra_button.grid_forget()
    list_spectra.grid_forget()
    sb_spectra.grid_forget()
    menu_button.grid_forget()
    delete_button.grid(row = 1, column = 1)
    view_button.grid(row = 1, column = 2)
    add_button.grid(row = 1, column = 0)
    s1.grid(row = 1, column = 3)
    list1.grid(row = 2, column = 0, rowspan = 20, columnspan = 4)
    sb1.grid(row = 2, column = 5, rowspan = 20, sticky="ns")
    updatelist()


def delete():
    print("delete")
    text=list1.curselection()
    db.delmol(text[0]+1)
    updatelist()


def deletespectra(list_spectra):
    text=list_spectra.curselection()
    print('delete spectra '+str(text[0]))


def add_mol():
    t = Toplevel(window)
    t.wm_title("Add Molecule")
    lname = Label(t, text="Name")
    lname.grid(row=0, column=0)
    name = StringVar()
    ename = Entry(t, textvariable=name)
    ename.grid(row=0, column=1)
    lcas = Label(t, text="CAS")
    lcas.grid(row=1, column=0)
    cas = StringVar()
    ecas = Entry(t, textvariable=cas)
    ecas.grid(row=1, column=1)
    lcharge = Label(t, text="Charge")
    lcharge.grid(row=2, column=0)
    charge = StringVar()
    echarge = Entry(t, textvariable=charge)
    echarge.grid(row=2, column=1)
    mult = StringVar()
    lmult = Label(t, text="Multiplicity")
    lmult.grid(row=3, column=0)
    emult = Entry(t, textvariable=mult)
    emult.grid(row=3, column=1)
    lgeom = Label(t, text="geom")
    lgeom.grid(row=4, column=0)
    egeom = Text(t)
    egeom.grid(row=4, column=1)
    addgeombtn = Button(t, text='Get geom from file', command=lambda: add_geomtotxt(egeom,geomfile))
    addgeombtn.grid(row=5, column=0)
    geomfile = StringVar()
    efile = Entry(t, textvariable=geomfile)
    efile.grid(row=5, column=1)
    addbtn = Button(t, text='Add', command=lambda: add_mol2list(t,ename,ecas,egeom,echarge,emult))
    addbtn.grid(row=6, column=0)
    cancelbtn = Button(t, text='Cancel', command=t.destroy)
    cancelbtn.grid(row=6, column=1)

    #if emolname.get() == '':
    #    result = messagebox.showerror("No molecule name set", "Please set a molecule name before choosing a spectrum file.", icon='warning')
    #db.addmol()
    #updatelist()

def add_geomtotxt(egeom,geomfile):
    #print(geomfile.get())
    #f=open(geomfile.get())
    #print(f.read())
    from cclib.parser import ccopen
    if geomfile.get() == '':
        print("No log file!")
        filetypes=(("Gaussian Output","*.log"),("all files","*.*"))
        logfile = askopenfilename(filetypes = filetypes)
    else:
        logfile = ccopen(geomfile.get())
    data = logfile.parse()
    for i in range(len(data.atomnos)):

        egeom.insert(END,pertable[data.atomnos[i]]+" "+str(data.atomcoords[-1,i,0])+" "+str(data.atomcoords[-1,i,1])+" "+str(data.atomcoords[-1,i,2])+"\n")
    egeom.setvar()
def add_mol2list(t,ename,ecas,egeom,echarge,emult):
    print('adding '+ename.get()+" "+egeom.get("1.0",END))
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute("INSERT INTO molecule VALUES (NULL,?,?,?,?,?)", (ename.get(),ecas.get(),egeom.get("1.0",END),echarge.get(),emult.get()))
    conn.commit()
    conn.close()
    updatelist()
    t.destroy()

def add_calcul(molid):
    t = Toplevel(window)
    t.wm_title("Add Calcul")
    file = StringVar()
    lfile = Label(t, text='File')
    lfile.grid(row=0, column=0)
    efile = Entry(t, textvariable=file)
    efile.grid(row=0, column=1)
    browsebtn = Button(t, text = 'Browse',command=lambda: browse(file,efile,(("Gaussian log files","*.log"),("all files","*.*"))))
    browsebtn.grid(row=0, column=2)
    addbtn = Button(t, text='Add', command=lambda: add_calcul2list(efile.get(),molid,t))
    addbtn.grid(row=2, column=0)
    cancelbtn = Button(t, text='Cancel', command=t.destroy)
    cancelbtn.grid(row=2, column=1)

def scanbasis(file):
    f = open(file)
    for line in f:
        if line[1:13] == "Gaussian 09:":
            print("Gaussian version 09")

            while line[1:5] != "----":
                line = next(f)
            line = next(f)
            print("This is the line :")
            print(line)
            import re
            m = re.search('([-a-zA-Z0-9]*)/([-a-zA-Z0-9]*)', line)
            print("test")
            print(m.group(2))
            funct=m.group(1)
            basis=m.group(2)
    return basis,funct


def freqanharmscan(output,freqanharm,intensanharm,Nvibs):
    f=open(output)
    for line in f:
        #print(line)
        #print(' Cite this work as:')
        #wait = input("PRESS ENTER TO CONTINUE.")
        if line[0:19] == ' Cite this work as:':
            print("it's here")
            line = next(f)
            print(line)
            if line[0:28] == ' Gaussian 09, Revision C.01,':
                GAUSSMAIN = '09'
                GAUSSREV = 'c.01'
                print('Version = '+GAUSSMAIN+GAUSSREV)
            if line[0:28] == ' Gaussian 16, Revision A.03,':
                GAUSSMAIN = '16'
                GAUSSREV = 'a.03'
                print('Version = '+GAUSSMAIN+GAUSSREV)
            if line[0:28] == ' Gaussian 09, Revision E.01,':
                GAUSSMAIN = '09'
                GAUSSREV = 'e.01'
                print('Version = '+GAUSSMAIN+GAUSSREV)
            #wait = input("PRESS ENTER TO CONTINUE.")

        # For FREQ=Anharm, extract anharmonicity frequency
        #print(line)
        if line[14:46] == "Anharmonic Infrared Spectroscopy":
            #print("test")
            #Nvibs = len(vibfreqs)
            print('Nvibs = ' + str(Nvibs))
            line = next(f)
            line = next(f)
            line = next(f)
            line = next(f)
            line = next(f)
            line = next(f)
            line = next(f)
            line = next(f)

            #freqanharm=np.zeros(Nvibs,"d")
            for i in range(Nvibs):
                #print('i='+str(i))
                line = next(f)
                #print('freqanharm = '+line[33:44]+ "intensanharm = "+line[63:79])
                if GAUSSMAIN == '16':
                    freqanharm[i]=line[37:46]
                else:
                    freqanharm[i] = line[33:44]
                    #print('freqanharm')
                    #print(freqanharm[i])
                #print(line[62:76])
                if (line[62:76] == '************\n'):
                    intensanharm[i]=line[46:59]
                else:
                    intensanharm[i]=line[63:79]


def scanfreq(file):#,freqharm,intensharm,freqanharm,intensanharm):
    freqharm=[]
    intensharm=[]
    freqanharm=[]
    intensanharm=[]
    f=open(file)
    for line in f:
        if line[14:46] == "Anharmonic Infrared Spectroscopy":
        #if line[0:1] == " ":
            print("This is here")
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            line1=f.readline()
            #line1=line
            #next(f)
            line2=f.readline()
            #next(f)
            line3=f.readline()
            while (line2[1:10]!='Overtones'):
                #print(line1)
                #print(line2)
                #print(line3)
                #print("---------")
                freqharm.append(np.float(line1[23:31]))
                #print(freqharm[-1])
                freqanharm.append(np.float(line1[33:42]))
                #print(freqanharm[-1])
                intensharm.append(np.float(line1[45:58]))
                #print(intensharm[-1])
                intensanharm.append(np.float(line1[60:74]))
                #print(intensanharm[-1])
                line1=line2
                line2=line3
                #next(f)
                line3=f.readline()
            line1=f.readline()
            line1=f.readline()
            line2=f.readline()
            line3=f.readline()
            while (line2[1:18]!='Combination Bands'):
                #line1=f.readline()
                freqanharm.append(np.float(line1[23:31]))
                print(freqanharm[-1])
                intensanharm.append(np.float(line1[60:74]))
                print(intensanharm[-1])
                line1=line2
                line2=line3
                #next(f)
                line3=f.readline()
    return freqharm, intensharm, freqanharm, intensanharm







def add_calcul2list(file,molid,t):
    t.destroy()
    print('Opening file')
    log = open(file).read()
    # print("Test reading")
    # print(log)
    basis,funct = scanbasis(file)
    #scanfreq(file)
    from cclib.parser import ccopen
    logfile = ccopen(file)
    data = logfile.parse()
    freqanharm = np.zeros(len(data.vibfreqs))
    intensanharmtmp = np.zeros(len(data.vibfreqs))
    intensanharm = np.zeros(len(data.vibfreqs))
    freqanharmscan(file,freqanharm,intensanharmtmp,len(data.vibfreqs))
    print(freqanharm)
    sort = np.argsort(freqanharm)
    freqanharm=np.sort(freqanharm)
    for k in range(len(intensanharmtmp)):
        intensanharm[k]=intensanharmtmp[sort[k]]
    db.insertcalc(molid,data,freqanharm,intensanharm,"B3LYP",basis,log)


def browse(file,efile,filetypes=(("csv files","*.csv"),("jdx files","*.jdx"),("all files","*.*"))):
    file = askopenfilename(filetypes = filetypes)
    efile.insert(0,file)


def add_spectra2list(file,title,molid,list_spectra,t):
    print('add_spectra2list '+file+" "+title)
    filename, file_extension = os.path.splitext(file)
    print('this is a '+file_extension+' file')
    if file_extension == '.jdx':
        print('Importing jdx file')
        jcamp_dict = JCAMP_reader(file)
        x=np.array(jcamp_dict['x'])
        if jcamp_dict['yunits'] == 'TRANSMITTANCE':
            print('Unit is TRANSMITTANCE, changing to absorbance')
            y = np.array(-np.log(jcamp_dict['y']))
        else:
            print('Unit is '+jcamp_dict['yunits']+', keeping it')
            y = np.array(jcamp_dict['y'])
        db.insert(molid,x,y,title)
    elif file_extension == '.csv':
        import csv
        x=[]
        y=[]
        with open('G:\Francois\RDDC\LAST_RESULT\TNT_ANHARM\TNT.csv', 'rt') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i=0
            for row in spamreader:
                i=i+1
                if(i>5):
                    x.append(row[0])
                    y.append(float(row[1]))
        db.insert(molid,np.array(x),np.array(y),title)
    updatespectra(molid,list_spectra)
    t.destroy()


def about():
    t = Toplevel(window)
    t.wm_title("About Qspectrum")
    abouttxt = Message(t, text='Qspectrum '+ver+' is a Software developped by François Dion (meitnerium109@gmail.com)')
    abouttxt.grid(row=0, column=0)
    okbtn = Button(t, text='OK', command=t.destroy)
    okbtn.grid(row=1, column=0)


def add_spectra(molid, list_spectra):
    t = Toplevel(window)
    t.wm_title("Add Spectra")
    ltitle = Label(t, text="Title")
    ltitle.grid(row=0, column=0)
    spectra_text = StringVar()
    etitle = Entry(t, textvariable=spectra_text)
    etitle.grid(row=0, column=1)
    filelabel = Label(t, text="File")
    filelabel.grid(row=1, column=0)
    file=StringVar()
    efile = Entry(t, textvariable=file)
    efile.grid(row=1, column=1)
    browsebtn = Button(t, text = 'Browse',command=lambda: browse(file,efile))
    browsebtn.grid(row=1, column=2)
    addbtn = Button(t, text='Add', command=lambda: add_spectra2list(efile.get(),etitle.get(),molid,list_spectra,t))
    addbtn.grid(row=2, column=0)
    cancelbtn = Button(t, text='Cancel', command=t.destroy)
    cancelbtn.grid(row=2, column=1)


def updatespectra(molid,list_spectra):
    spectra=readspectra(molid)
    for spectrum in spectra:
        list_spectra.insert(spectrum.id,spectrum.title)


def opendb():
    global dbfile
    print('open a database')
    dbfile = askopenfilename(filetypes=(("Sqlite DB files","*.db"),("all files","*.*")))
    conn=sqlite3.connect(dbfile)
    cur=conn.cursor()
    conn.close()
    updatelist()


def createdb():
    global dbfile, db
    dbfile = asksaveasfilename(filetypes=(("Sqlite DB files","*.db"),("all files","*.*")))
    db = Database()
    updatelist()



db = Database()
window = Tk()
window.wm_title("STAV ver "+ver)
menubar = Menu(window)
#win=windows()





filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Create a database", command=createdb)
filemenu.add_command(label="Open a database", command=opendb)
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)
# TODO create a menu to create fig and modify right clicking on list
# listfigure = []
# def createfig():
#    global listfigure
#    fig = Figure()
#    listfigure.append(fig)

# TODO figure menu
#figuremenu = Menu(menubar, tearoff=0)
#figuremenu.add_command(label="Create a figure", command=createfig)
#menubar.add_cascade(label="Figure", menu=figuremenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)
window.config(menu=menubar)

lmolname = Label(window,text="Molecule name")
lmolname.grid(row=0, column=0)
molname_text=StringVar()
emolname = Entry(window,textvariable=molname_text)
emolname.grid(row=0, column=1)


lcas = Label(window,text="CAS")
lcas.grid(row=0, column=2)
cas_text=StringVar()
ecas=Entry(window,textvariable=cas_text)
ecas.grid(row=0, column=3)

s1 = Button(text = 'Search')
s1.grid(row=1, column=3)

add_button = Button(text = 'Add a molecule',command=add_mol)
add_button.grid(row=1, column=0)

view_button = Button(text = 'View',command=view)
view_button.grid(row=1, column=2)


delete_button = Button(text = 'Delete',command=delete)
delete_button.grid(row=1, column=1)

list1=Listbox(window, height=20, width=80)
list1.bind('<Double-1>', lambda x: view())
list1.grid(row=2, column=0, rowspan=20, columnspan=4)
sb1=Scrollbar(window)
sb1.grid(row=2, column=5, rowspan=20, sticky="ns")

def hello():
    print("hello!")

# TODO : Create input from mol view
# def createinput():
#    print("Create input")

# create a popup menu
list1rbmenu = Menu(window, tearoff=0)
list1rbmenu.add_command(label="View", command=view)
list1rbmenu.add_command(label="Delete", command=delete)
# list1rbmenu.add_command(label="Create Input", command=createinput)
def popup(event):
    list1rbmenu.post(event.x_root, event.y_root)
list1.bind("<Button-3>", popup)

def updatelist():
    global mol
    mol = readmol()
    list1.delete(0,END)
    #list1.insert(END,("methanol"))
    for molecule in mol:
        list1.insert(molecule.id,str(molecule.id)+" "+molecule.name+" ("+molecule.cas+") ")

def menage():
    global dbfile
    for row in db.molview():
        print(row)
        if os.path.isfile(dbfile)and os.access(dbfile, os.R_OK):
            print("File exists and is readable")
        else:
            dbfile=askopenfilename(filetypes = (("Sqlite DB files","*.db"),("all files","*.*")))
        conn=sqlite3.connect(dbfile)
        cur=conn.cursor()
        print("testttttttt2222 : " +str(row[0]))
        cur.execute("DELETE FROM molecule WHERE id = '"+str(row[0])+"'")
        conn.commit()
        #rows=cur.fetchall()
        conn.close()

def getrows(select, table, end):
    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)
    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)
    conn = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("SELECT "+select+" FROM "+table+" "+end)
    rows=cur.fetchall()
    conn.close()
    return rows

def readspectra(molid):
    if molid == '':
        rows=getrows('id,molid,x,y,title','spectra','')
    else:
        rows=getrows('id,molid,x,y,title','spectra',"WHERE molid = '"+str(molid)+"'")
    spectra=[]
    for row in rows:
        spectra.append(Spectra(row[0],row[1],row[2],row[3],row[4]))
    return spectra


def readmol():
    rows=getrows('id,name,cas','molecule','')
    mol=[]
    for row in rows:
        mol.append(Molecule('',row[0],row[1],row[2]))
    return mol


mol=readmol()
print('--- Molecule ---')
for molecule in mol:
    print(molecule.name)
    spectra=readspectra(molecule.id)
    for spectrum in spectra:
        print(str(spectrum.id)+" "+spectrum.title)
#menage()
updatelist()
window.mainloop()
window=Tk()
MainWin(window)
#window.mainloop()
