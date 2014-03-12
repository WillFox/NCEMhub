import Tkinter
########TEST################
#Tkinter._test()

#frmMain = Tkinter.Tk()
#label = Tkinter.Label(frmMain, text="Welcome to NCEMhub")
#label.pack()
#frmMain.mainloop()
########TEST###############
"""
PURPOSE:  Match recorded data from microscopist and send it to NCEMhub
Items needed:
---Preferences 
	-holds where data is 
	-automatic transfer/ permission transfer
	-password or ssh key for transfer?
---User Login
	-connects to django database
	-verifies credentials
---Interface that allows addition of meta data right away
	-creation date 
	-characteristics
	-tags
"""
class Application(Tkinter.Frame):
    def say_hi(self):
        print "hi there, everyone!"

    def createWidgets(self):
        self.QUIT = Tkinter.Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = Tkinter.Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})

    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tkinter.Tk()
app = Application(master=root)
app.mainloop()
root.destroy()