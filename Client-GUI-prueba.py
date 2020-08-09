import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("Client")
username = " "

topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="OLD MAID JUEGO \n Intrucciones: \n Primero te repartiremos 5 cartas \n En el deck existe solamente una Reina, la cual no quieres tener al final del juego \n Tambien debes quedarte sin cartas \n para desaserte de ellas puedes bajar parejas \n Cuando sea tu turno puede escoger UNA carta del contricante anterior \n Bajas las parejas (si tienes) y el siguente toma una carta de las tuyas").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)

bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)

def connect():
    print("Connect to server")

def getChatMessage(msg):
    print("Get message from message area")

def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        # display message from server on the chat window

        # enable the display area and insert the text and then disable.
        # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n"+ from_server)

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)

        # print("Server says: " +from_server)

    sck.close()
    window.destroy()

window.mainloop()
