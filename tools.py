import tkinter as tk
from tkinter import ttk


class SortTasksFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, width=52, height=168, bg="#324A5F")

        self.controller = controller

        self.buttonNameList = ["手動", "カテゴリ", "優先度", "コスト"]

        self.buttons = []

        self.drawButtons()


    def drawButtons(self):
        for i, buttonName in enumerate(self.buttonNameList):
                button =  tk.Button(self,
                    text=buttonName, 
                    command=lambda i=i: self.clickButtonFunction(i+1),
                    fg="#FFF", activeforeground = "#FFF",
                    background="#4A5F70",
                    activebackground="#566E82",  # クリック時背景色
                    font=("Noto Sans JP", 10),
                    borderwidth=0, highlightthickness=0,
                    cursor="hand2",
                )
                if i+1 == self.controller.selectedSortID:
                    button.config(
                        background="#245D8E",
                        activebackground="#245D8E"
                    )
                self.buttons.append(button)
                button.place(x=3, y=2+42*i, width=48, height=40)


    def clickButtonFunction(self, id):
        self.controller.selectedSortID = id
        for i, button in enumerate(self.buttons):
            if i+1 == id:
                button.config(
                        background="#245D8E",
                        activebackground="#245D8E"
                    )
            else:
                button.config(
                    background="#4A5F70",
                    activebackground="#566E82"
                )

        self.controller.view.taskDispFrame.displayAllTasks(id)
        


        

class FileterTaskStatusFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, width=52, height=142, bg="#324A5F")

        self.controller = controller

        self.buttons = []
        self.nameLabels = []

        self.statusColors = ["#73FF09", "#FFCC00", "#0088FF", "#C112F0", "#00FFBB"]

        self.drawButtons()


    def drawButtons(self):
        for i, buttonName in enumerate(self.controller.filterStatusNameList):
                button = tk.Frame(self,
                    background="#4A5F70",
                    borderwidth=0, highlightthickness=0,
                    cursor="hand2"
                )
                button.bind("<Button-1>", lambda e, i=i: self.clickButtonFunction(i))

                self.buttons.append(button)

                nameLabel = tk.Label(button,
                    bg="#4A5F70", fg="#FFF",
                    text=buttonName,
                    font=("Noto Sans JP", 9),
                    anchor="w"
                )
                nameLabel.bind("<Button-1>", lambda e, i=i: self.clickButtonFunction(i))
                nameLabel.place(x=4, y=3, width=42, height=14)

                self.nameLabels.append(nameLabel)

                if self.controller.selectedFilterStatusList[i]:
                    button.config(
                        background="#245D8E",
                    )
                    nameLabel.config(bg="#245D8E")
                    
                button.place(x=3, y=2+28*i, width=48, height=25)
                tk.Frame(button,
                    bg=self.statusColors[i]
                ).place(x=0, y=6, width=4, height=12)

    def on_enter(self, event):
        event.widget.config(bg="#566E82")       
    def on_leave(self, event):
        event.widget.config(bg="#4A5F70")       
    def on_enter_unselected(self, event):
        event.widget.config(bg="#2E6BA1")       
    def on_leave_unselected(self, event):
        event.widget.config(bg="#245D8E")       


    def clickButtonFunction(self, num):
        print(num)
        self.controller.selectedFilterStatusList[num] = not self.controller.selectedFilterStatusList[num]

        if self.controller.selectedFilterStatusList[num]:
            self.buttons[num].config(
                    background="#245D8E",
                )
            self.nameLabels[num].config(
                    background="#245D8E",
                )
        else:
            self.buttons[num].config(
                    background="#4A5F70",
                )
            self.nameLabels[num].config(
                background="#4A5F70",
            )

        self.controller.view.taskDispFrame.displayAllTasks(self.controller.selectedSortID)
      