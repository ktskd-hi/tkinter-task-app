import tkinter as tk
from tkinter import ttk, messagebox

from task import TaskList,Task,CategoryList,Category,GoalLineList,GoalLine
from pydantic import ValidationError

from PIL import Image, ImageTk

import json
import sys

from viewFunc import Styles,EditModal,AddTaskWindowEntry,DataFunctions,GoallineFunctions,TaskTitle,CategoryListFrame,DeleteDialogModal,DeleteButton,GraphView,ViewGoallineListFrame,TaskHeader
from tools import SortTasksFrame, FileterTaskStatusFrame



class TaskDispFrame(tk.Frame):
    def __init__(self, master, parent, controller):
        # 継承元クラス（tk.Frame）のコンストラクタを呼び出し
        super().__init__(master, width=532, height=536, bg="#2B455B")
        
        self.styles = Styles()
        self.task_list = controller.task_list
        self.parent = parent
        self.controller = controller
        self.goalLineUnitFrameList = {}
        self.taskDispAreaHeight = self.parent.toolFrame.winfo_height()-80

        self.edit_icon = tk.PhotoImage(file="./imgs/edit_icon.png")

        self.taskDispCanvas = tk.Canvas(self, bg="#2B455B", bd=0, highlightthickness=0, relief='flat')
        self.taskDispInnerFrame = tk.Frame(self.taskDispCanvas, width=532, height=536, bg="#2B455B", borderwidth=0, relief="flat")

        # タスクリストエリアと目安ラインエリアのフレームを配置
        self.taskListWrapFrame = tk.Frame(self.taskDispInnerFrame, width=378, height=536, bg="#2B455B", borderwidth=0, relief="flat")
        self.taskListWrapFrame.pack(side="left", expand=1, fill=tk.BOTH)
        self.goalLineWrapFrame = tk.Frame(self.taskDispInnerFrame, width=154, height=536, bg="#2B455B", borderwidth=0, relief="flat")
        self.goalLineWrapFrame.pack(side="right", fill=tk.Y)

        self.unchecked_photo_list = {}
        self.checked_photo_list = {}
        self.check_button_list = {}

        self.taskDispScrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.taskDispCanvas.yview,
            style="Vertical.TScrollbar"
        )
        self.taskDispCanvas.configure(yscrollcommand=self.taskDispScrollbar.set)

        self.noto_font = ("Noto Sans JP", 12)
        
        self.displayAllTasks(1)


        # 目標ラインの表示
        dispGoalLineHeight = self.taskDispAreaHeight

        sortedGoallines = sorted(self.controller.goalline_list.goallines, key=lambda goalline: goalline.cost)

        for goalLine in sortedGoallines:
            dispGoalLineHeight = self.parent.goalline_functions.dispGoalLine(goalLine, dispGoalLineHeight, self)

        # CanvasにFrameを埋め込む
        window_id = self.taskDispCanvas.create_window((0, 0), window=self.taskDispInnerFrame, anchor="nw")

        def on_frame_configure(event):
            bbox = self.taskDispCanvas.bbox("all")
            self.taskDispAreaHeight = self.parent.toolFrame.winfo_height()-80
            self.taskDispCanvas.configure(scrollregion=bbox)
            self.taskDispCanvas.itemconfig(window_id, width=self.taskDispCanvas.winfo_width())

            self.taskDispCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            if bbox[3] > self.taskDispAreaHeight:
                self.styles.bind_to_all_children(self, "<MouseWheel>", self.on_mousewheel_tasklist)
                self.taskDispScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                self.taskDispScrollbar.pack_forget()
                self.styles.unbind_from_all_children(self, "<MouseWheel>")
        
        self.taskDispInnerFrame.bind("<Configure>", on_frame_configure)
        self.bind("<Configure>", on_frame_configure)



    def on_mousewheel_tasklist(self, event):
        self.taskDispCanvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def addTaskList(self, dispOrder, task):
        self.list_frame = tk.Frame(self.taskListWrapFrame, width=378, height=40, bg="#2B455B")
        
        # 子要素を取得して、今回の追加番目の位置を指定して追加する
        # 追加番目より要素数が多い場合は最後に追加する
        slaves = self.taskListWrapFrame.pack_slaves()
        target = slaves[dispOrder-1] if dispOrder-1 < len(slaves) else None
        if target:
            self.list_frame.pack(side=tk.TOP, fill=tk.X, anchor=tk.NW, pady=2, before=target)
        else:
            self.list_frame.pack(side=tk.TOP, fill=tk.X, anchor=tk.NW, pady=2) # 最後に追加
        listBGColor = task.category.color
        ttk.Label(self.list_frame, 
            text=f"{dispOrder}",
            justify="center", anchor="center", font=self.noto_font,
            foreground="#FFF", background="#3C5A75",
            width=20
        ).place(x=2, y=0, width=20, height=40)

        if task.status == "未実施":
            statusColor = "#73FF09"
        elif task.status == "取組中":
            statusColor = "#FFCC00"
        elif task.status == "保留":
            statusColor = "#0088FF"
        elif task.status == "完了":
            statusColor = "#C112F0"
        else:
            statusColor = "#00FFBB"

        tk.Label(self.list_frame, 
            bg=statusColor
        ).place(x=24, y=0, width=4, height=40)
        

        self.unchecked_photo_list[task.id] = ImageTk.PhotoImage(Image.open("./imgs/unchecked.png"))
        self.checked_photo_list[task.id]  = ImageTk.PhotoImage(Image.open("./imgs/checked.png"))

        self.check_button_list[task.id] = checkboxButton = tk.Button(self.list_frame,
            image=self.checked_photo_list[task.id] if task.check else self.unchecked_photo_list[task.id],
            command=lambda: self.checkTask(task.id),
            background=listBGColor,
            activebackground=listBGColor,  # クリック時背景色
            borderwidth=0, highlightthickness=0,
            cursor="hand2"
        )
        self.check_button_list[task.id].place(x=30, y=0, width=32, height=40)

        
        priorityExclamation = "!" * task.priority

        ttk.Label(self.list_frame, 
            text=priorityExclamation,
            anchor="center", justify="center", font=("Noto Sans JP", 10),
            foreground="#FFF", background=listBGColor,
            width=20
        ).place(x=64, y=0, width=20, height=40)
        cost = task.estimatedCost
        cost = int(cost) if cost == int(cost) else cost
        ttk.Label(self.list_frame, 
            text=f"{cost}",
            anchor="center", justify="center", font=self.noto_font,
            foreground="#FFF", background=listBGColor,
            width=20
        ).place(x=86, y=0, width=32, height=40)
        ttk.Label(self.list_frame, 
            text=f"{task.title}",
            anchor="w", justify="left", font=self.noto_font,
            foreground="#FFF", background=listBGColor,
            width=245
        ).place(x=120, y=0, relwidth=1.0, width=-142, height=40)
        tk.Button(self.list_frame, 
            text="",
            image=self.edit_icon, compound="center",
            anchor="center", justify="left", font=self.noto_font,
            background= listBGColor,
            width=20,
            cursor="hand2", relief="flat", bd=0, highlightthickness=0,
            command=lambda: self.parent.openEditTaskWindow(task.id),
            activebackground=self.styles.adjust_brightness(listBGColor, 1.07)  # クリック時背景色
        ).place(x=-20, y=0, width=20, height=40, relx=1.0)



    def updateCheckButton(self, task_id):
        self.check_button_list[task_id].configure(image=self.checked_photo_list[task_id] if self.task_list.tasks[task_id-1].check else self.unchecked_photo_list[task_id])

    def displayAllTasks(self, sortID):
        for widget in self.taskListWrapFrame.winfo_children():
            widget.destroy()

        dispId=0

        if sortID == 2:
            sortedTasks = sorted(self.controller.task_list.tasks, key=lambda task: task.category.id)
        elif sortID == 3:
            sortedTasks = sorted(self.controller.task_list.tasks, key=lambda task: task.priority, reverse=True)
        elif sortID == 4:
            sortedTasks = sorted(self.controller.task_list.tasks, key=lambda task: task.estimatedCost, reverse=True)
        else:
            sortedTasks = sorted(self.task_list.tasks, key=lambda task: task.displayOrder)

        dispStatusList = []
        noDispStatusList = []
        dispOthers = False

        for i, boolean in enumerate(self.controller.selectedFilterStatusList):
            if boolean == True:
                addName = self.controller.filterStatusNameList[i]
                if addName == "その他":
                    dispOthers = True
                else:
                    dispStatusList.append(addName)
            else:
                addName = self.controller.filterStatusNameList[i]
                if addName != "その他":
                    noDispStatusList.append(addName)


        for task in sortedTasks:
            if task.displayOrder != 9999:
                if dispOthers:
                    if task.status not in noDispStatusList:
                        dispId+=1
                        self.addTaskList(dispId, task)                        
                else:
                    if task.status in dispStatusList:
                        dispId+=1
                        self.addTaskList(dispId, task)

        self.controller.calcCostSum()
        
        self.editGoalLinePlace(None)
        

    def editTaskList(self, id, task):
        # 該当番目を削除する
        self.displayAllTasks(1)

    def checkTask(self, task_id):
        self.controller.task_list.tasks[task_id-1].check = not self.controller.task_list.tasks[task_id-1].check
        self.updateCheckButton(task_id)
        self.controller.view.visualizeFrame.graphViewFrame.updateGraph()

        self.controller.calcCostSum()

        self.editGoalLinePlace(None)



    def editGoalLinePlace(self, goalline):

        for key, val in self.goalLineUnitFrameList.items():
            val["frame"].destroy()
        self.goalLineUnitFrameList.clear()

        dispGoalLineHeight = self.taskDispAreaHeight

        sortedGoallines = sorted(self.controller.goalline_list.goallines, key=lambda goalline: goalline.cost)

        def get_all_descendants(widget):
            descendants = []
            for child in widget.winfo_children():
                descendants.append(child)
                descendants.extend(get_all_descendants(child))  # 再帰的に追加
            return descendants

        for widget in get_all_descendants(self.goalLineWrapFrame):
            widget.destroy()

        for goalLine in sortedGoallines:
            dispGoalLineHeight = self.parent.goalline_functions.dispGoalLine(goalLine, dispGoalLineHeight, self)


    def editGoalline(self, goalline):
        goalline_functions = self.parent.goalline_functions
        cost = goalline.cost
        cost = int(cost) if cost == int(cost) else cost
        goalline_functions.goallineUnitSlaves[goalline.id]["line_button"].config(
            bg=goalline_functions.colors[goalline.color_id-1]["bg"], 
            fg=goalline_functions.colors[goalline.color_id-1]["fg"],
            text=cost
        )
        goalline_functions.goallineUnitSlaves[goalline.id]["name_button"].config(
            text=goalline.title
        )
        self.editGoalLinePlace(goalline)





class VisualizeFrame(tk.Frame):
    def __init__(self, parent, controller):
        # 継承元クラス（tk.Frame）のコンストラクタを呼び出し
        super().__init__(parent.frame, width=372, bg="#1B2D3D")

        self.parent = parent
        self.controller = controller
        self.styles = Styles()

        self.disp_icon = tk.PhotoImage(file="./imgs/disp_icon.png")
        self.undisp_icon = tk.PhotoImage(file="./imgs/undisp_icon.png")


        # ビジュアライズフレームにCanvasを配置してスクロールバーをつける====
        self.visualizeCanvas = tk.Canvas(self, bg="#2B455B", width=366, bd=0, highlightthickness=0, relief='flat')
        self.visualizeInnerFrame = tk.Frame(self.visualizeCanvas, width=372, bg="#1B2D3D", borderwidth=0, relief="flat")
        self.visualizeScrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.visualizeCanvas.yview,
            style="Custom2.Vertical.TScrollbar"
        )
        self.visualizeCanvas.configure(
            yscrollcommand=self.visualizeScrollbar.set
        )
        
        # ビジュアライズフレーム内のcanvasに3つのフレームを配置===
        self.visualizeGraphFrame = tk.Frame(self.visualizeInnerFrame, width=348, height=360, bg="#324A5F")
        self.visualizeGoallineFrame = tk.Frame(self.visualizeInnerFrame, width=348, height=240, bg="#324A5F")
        self.visualizeCategoryFrame = tk.Frame(self.visualizeInnerFrame, width=348, height=232, bg="#324A5F")

        self.visualizeGraphFrame.pack(side=tk.TOP, padx=8, pady=8) 
        self.visualizeGoallineFrame.pack(side=tk.TOP, padx=8) 
        self.visualizeCategoryFrame.pack(side=tk.TOP, padx=8, pady=8)

        self.visualizeGraphFrameTitleFrame = tk.Frame(self.visualizeGraphFrame, bg="#324A5F", width=348, height=40)
        self.visualizeGraphFrameTitle = tk.Label(self.visualizeGraphFrameTitleFrame, text="カテゴリごとの合計", bg="#324A5F", fg="#E3E6E8", font=("Noto Sans JP", 11, "bold"), anchor="w", justify="left", relief=None)
        self.visualizeGraphFrameTitle.place(x=12, y=16, width=320, height=16)
        self.diffDispSwitchFlag = True
        self.diffDispSwitchButton = tk.Button(self.visualizeGraphFrameTitleFrame,
            image=self.undisp_icon,
            bg="#4D6F8D", activebackground="#567A99",
            anchor="center", justify="center",
            cursor="hand2", relief="flat", bd=0, highlightthickness=0,
            command=self.diffDispSwitch
        )
        self.diffDispSwitchButton.place(x=308, y=14, width=28, height=24)

        self.visualizeGraphFrameTitleFrame.pack()
        self.graphViewFrame = GraphView(self.visualizeGraphFrame, self.controller, self)
        self.graphViewFrame.pack(pady=(0, 16))


        self.viewGoallineList()
        

        self.visualizeCategoryFrameTitleFrame = tk.Frame(self.visualizeCategoryFrame, bg="#324A5F", width=348, height=40)
        self.visualizeCategoryFrameTitle = tk.Label(self.visualizeCategoryFrameTitleFrame, text="カテゴリリスト", bg="#324A5F", fg="#E3E6E8", font=("Noto Sans JP", 11, "bold"), anchor="w", justify="left", relief=None)
        self.visualizeCategoryFrameTitle.place(x=12, y=16, width=320, height=16)
        self.visualizeCategoryFrameTitleFrame.place(x=0, y=0, width=320, height=40)
        categoryListWrapFrame = tk.Frame(self.visualizeCategoryFrame,
            background="#324A5F"
        )
        categoryListWrapFrame.place(x=16, y=44, width=320, height=160)


        for category in self.controller.category_list.categories:
            category_list_frame = CategoryListFrame(categoryListWrapFrame, category, self.controller)


        self.visualizeCanvas.create_window((0, 0), window=self.visualizeInnerFrame, anchor="nw")


        def on_visualizeFrame_configure(event):
            self.visualizeCanvas.update_idletasks()
            self.visualizeCanvas.configure(scrollregion=self.visualizeCanvas.bbox("all"))

        self.visualizeInnerFrame.bind("<Configure>", on_visualizeFrame_configure)

        # スクロールイベント
        self.styles.bind_to_all_children(self.visualizeCanvas, "<MouseWheel>", self.on_mousewheel_visualize)
        # キャンバスとスクロールバーをパック
        self.visualizeCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.visualizeScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_mousewheel_visualize(self, event):
        self.visualizeCanvas.yview_scroll(-1 * (event.delta // 120), "units")

    def diffDispSwitch(self):
        self.diffDispSwitchFlag = not self.diffDispSwitchFlag
        for diffDispFrame in self.graphViewFrame.diffDispFrameList:
            diffDispFrame.destroy()
        self.graphViewFrame.updateGraph()
        if self.diffDispSwitchFlag:
            self.diffDispSwitchButton.config(image=self.undisp_icon)
        else:
            self.diffDispSwitchButton.config(image=self.disp_icon)
        

    def viewGoallineList(self):
        self.visualizeGoallineFrameTitleFrame = tk.Frame(self.visualizeGoallineFrame, bg="#324A5F", width=348, height=40)
        self.visualizeGoallineFrameTitle = tk.Label(self.visualizeGoallineFrameTitleFrame, text="グラフに表示する目安ライン", bg="#324A5F", fg="#E3E6E8", font=("Noto Sans JP", 11, "bold"), anchor="w", justify="left", relief=None)
        self.visualizeGoallineFrameTitle.place(x=12, y=16, width=320, height=16)
        self.visualizeGoallineFrameTitleFrame.pack()
        self.viewGoallineListFrame = ViewGoallineListFrame(self.visualizeGoallineFrame, self.controller, self, 1)

        self.visualizeGoallineFrameTitleFrame2 = tk.Frame(self.visualizeGoallineFrame, bg="#324A5F", width=348, height=40)
        self.visualizeGoallineFrameTitle2 = tk.Label(self.visualizeGoallineFrameTitleFrame2, text="グラフに表示しない目安ライン", bg="#324A5F", fg="#E3E6E8", font=("Noto Sans JP", 11, "bold"), anchor="w", justify="left", relief=None)
        self.visualizeGoallineFrameTitle2.place(x=12, y=16, width=320, height=16)
        self.visualizeGoallineFrameTitleFrame2.pack()
        self.viewGoallineListFrame2 = ViewGoallineListFrame(self.visualizeGoallineFrame, self.controller, self, 2)

    def dispDiffDispSwitchButton(self):
        self.diffDispSwitchButton.place(x=308, y=14, width=28, height=24)

    def undispDiffDispSwitchButton(self):
        self.diffDispSwitchButton.place_forget()





class View(tk.Frame):
    def __init__(self, parent, controller):
        # 継承元クラス（tk.Frame）のコンストラクタを呼び出し
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller
        self.tasks = controller.task_list.tasks
        self.goalline_list = controller.goalline_list
        self.category_list = controller.category_list

        self.data_functions = DataFunctions()
        self.goalline_functions = GoallineFunctions(root, controller, self.goalline_list)

        self.beforeDispOrder = 1 # 変更前の表示順

        # メインフレームを定義
        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH)


        # メインフレームを3つに分割================================
        self.toolFrame = tk.Frame(self.frame, width=56, height=640, bg="#283B4B")
        self.taskFrame = tk.Frame(self.frame, width=532, height=640, bg="#263C4E")
        self.visualizeFrame = VisualizeFrame(self, self.controller)

    
        # メインの3つのフレームを配置
        self.toolFrame.pack(side=tk.LEFT,fill=tk.Y, anchor=tk.W)
        self.taskFrame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.visualizeFrame.pack(side=tk.LEFT,fill=tk.BOTH)

        self.sortTasksFrame = SortTasksFrame(self.toolFrame, self.controller)
        self.sortTasksFrame.pack(side="bottom", pady=(2,4))

        self.fileterTaskStatusFrame = FileterTaskStatusFrame(self.toolFrame, self.controller)
        self.fileterTaskStatusFrame.pack(side="bottom", pady=0)



        # タスクフレームを3つに分割=====
        # １つ目===
        self.taskHeaderFrame = tk.Frame(self.taskFrame, width=532, height=32, bg="#112F48")
        self.taskTitle = TaskTitle(self.taskHeaderFrame, self.controller.project_title, self.controller)

        #　2つ目===
        self.title_header = TaskHeader(self.taskFrame)

        self.taskDispFrame = TaskDispFrame(self.taskFrame, self, controller)
        #　3つ目===
        self.taskToolFrame = tk.Frame(self.taskFrame, width=532, height=56, bg="#253644")
        #　1~3つ目をパック
        self.taskHeaderFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.N) 
        self.title_header.pack(side=tk.TOP, fill=tk.X, anchor=tk.N, padx=0, pady=0)
        self.taskDispFrame.pack(side=tk.TOP, expand=True, fill=tk.BOTH) 
        self.taskToolFrame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.S)

        self.addTaskButtonStyle = ttk.Style()
        self.addTaskButtonStyle.configure("AddTask.TButton", 
            font=("Noto Sans", 18),
            background="#E8E8E8",foreground="#2B455B",
            relief = "flat"
        )
        self.addTaskButtonStyle.map("AddTask.TButton",
          background=[("active", "#F6F6F6")],
          foreground=[("active", "#2B455B")])
        self.taskAddButton = ttk.Button(self.taskToolFrame, 
            style="AddTask.TButton",
            text="＋", 
            command=self.openAddTaskWindow,
            cursor="hand2",
            takefocus=0 
        )
        self.taskAddButton.place(x=24, y=8, relwidth=1.0, width=-189, height=40)


        self.addGoalLineButtonStyle = ttk.Style()
        self.addGoalLineButtonStyle.configure("AddGoalLine.TButton", 
            font=("Noto Sans", 18),
            background="#DC567C",foreground="#FFF",
            relief = "flat"
        )
        self.addGoalLineButtonStyle.map("AddGoalLine.TButton",
          background=[("active", "#E65F85")],
          foreground=[("active", "#FFF")])
        self.goalLineAddButton = ttk.Button(self.taskToolFrame, 
            style="AddGoalLine.TButton",
            text="＋", 
            command=lambda: self.goalline_functions.openAddGoallineWindow(),
            cursor="hand2",
            takefocus=0
        )
        self.goalLineAddButton.place(x=-153, y=8, width=120, height=40, relx=1.0)


    def openWriteTaskWindow(self, command, id, dispPattern):
        self.addTaskWindow = EditModal(root, "タスクを追加", 816, 548, "#324A5F", command, id)

        # ラベルや他のUI
        font = ("Noto Sans JP", 12)
        font2 = ("Noto Sans JP", 14)

        # 各プロパティ入力
        addProperties = tk.Frame(self.addTaskWindow, background="#324A5F")
        self.addTaskWindow.after(20, lambda: addProperties.place(x=34, y=42, width=488, height=408))
        

        ttk.Label(addProperties, text="項目名", foreground="#FFF", font=font, background="#324A5F").place(x=8, y=-1, width=48, height=40)
        self.titleEntry = AddTaskWindowEntry(addProperties, "left")
        self.titleEntry.place(x=64, y=0, width=424, height=40)
        self.titleEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.titleEntry, ""))
        self.titleEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.titleEntry, ""))
        self.addTaskWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.titleEntry, dataType=""))

        ttk.Label(addProperties, text="優先度", foreground="#FFF", font=font, background="#324A5F").place(x=8, y=55, width=48, height=40)
        self.priorityEntry = AddTaskWindowEntry(addProperties, "center")
        self.priorityEntry.place(x=64, y=56, width=48, height=40)
        self.priorityEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.priorityEntry, int))
        self.priorityEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.priorityEntry, int))
        self.addTaskWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.priorityEntry, dataType=int))

        ttk.Label(addProperties, text="想定コスト", foreground="#FFF", font=font, background="#324A5F").place(x=134, y=55, width=80, height=40)
        self.estimatedCostEntry = AddTaskWindowEntry(addProperties, "center")
        self.estimatedCostEntry.place(x=222, y=56, width=48, height=40)
        self.estimatedCostEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.estimatedCostEntry, float))
        self.estimatedCostEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.estimatedCostEntry, float))
        self.addTaskWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.estimatedCostEntry, dataType=float))

        ttk.Label(addProperties, text="ステータス", foreground="#FFF", font=font, background="#324A5F").place(x=294, y=55, width=80, height=40)
        self.statusEntry = AddTaskWindowEntry(addProperties, "center")
        self.statusEntry.place(x=382, y=56, width=80, height=40)
        self.statusEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.statusEntry, ""))
        self.statusEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.statusEntry, ""))
        self.addTaskWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.statusEntry, dataType=""))

        ttk.Label(addProperties, text="表示順", foreground="#FFF", font=font, background="#324A5F").place(x=8, y=112, width=48, height=40)
        self.dispOrderEntry = AddTaskWindowEntry(addProperties, "center")
        if dispPattern == 1:
            count = sum(1 for task in self.tasks if task.displayOrder != 9999)
            self.dispOrderEntry.insert(0, count+1)
        else:
            self.dispOrderEntry.insert(0, self.tasks[id-1].displayOrder)
        self.dispOrderEntry.place(x=64, y=112, width=48, height=40)
        self.dispOrderEntry.bind("<Configure>", lambda event: self.data_functions.validate_entry(event, self.dispOrderEntry, int))
        self.dispOrderEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.dispOrderEntry, int))
        self.dispOrderEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.dispOrderEntry, int))
        self.addTaskWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.dispOrderEntry, dataType=int))

        ttk.Label(addProperties, text="概要", foreground="#FFF", font=font2, background="#324A5F").place(x=8, y=168, width=40, height=40)
        self.aboutTextFrame = tk.Frame(addProperties, background="#324A5F")
        self.aboutTextFrame.place(x=8, y=206, width=480, height=126)
        self.abouText = tk.Text(self.aboutTextFrame, bg="#253645", fg="#FFF", relief="flat", bd=0, insertbackground="#FFF", font=("Noto Sans JP", 12), wrap="word")
        self.abouText.pack(side="left", fill="both")
        self.abouText.bind("<Control-z>", lambda e: self.abouText.edit_undo())

        if dispPattern == 2:
            DeleteButton(addProperties, self.deleteTask, id, 356)


        # カテゴリの選択
        addCategory = tk.Frame(self.addTaskWindow, background="#324A5F")
        addCategory.place(x=556, y=122, width=208, height=180)

        self.selectCategoryVar = tk.StringVar(value="1")
        for i, category in enumerate(self.category_list.categories):
            selectCategoryFrame = tk.Frame(addCategory, width=208, height=32, background="#324A5F")
            selectCategoryFrame.pack(side="top", pady=4)
            tk.Radiobutton(selectCategoryFrame, text="", variable=self.selectCategoryVar, value=i+1, fg="#142C30", bg="#324A5F", activebackground="#324A5F", selectcolor="white", cursor="hand2", relief="flat", bd=0).place(x=0,y=0,width=24,height=24)
            tk.Frame(selectCategoryFrame, bg=category.color).place(x=28, y=4, width=32, height=16)
            tk.Label(selectCategoryFrame, text=category.title, fg="#FFF", bg="#324A5F", font=font).place(x=68, y=-4)
    
    def openAddTaskWindow(self):
        self.openWriteTaskWindow(self.addTask, len(self.tasks)+1, 1)
        
        # モーダルのイベントループを開始
        root.wait_window(self.addTaskWindow)  # ウインドウが閉じられるまで待機

    def openEditTaskWindow(self, id):
        self.openWriteTaskWindow(self.editTask, id, 2)
        
        self.beforeDispOrder = self.tasks[id-1].displayOrder
        # print (self.task_list)
        self.titleEntry.insert(0, next((task.title for task in self.tasks if task.id == id), None))
        self.data_functions.validate_entry(event=None, widget=self.titleEntry, dataType="")
        self.priorityEntry.insert(0, next((task.priority for task in self.tasks if task.id == id), None))
        self.data_functions.validate_entry(event=None, widget=self.priorityEntry, dataType=int)
        cost = next((task.estimatedCost for task in self.tasks if task.id == id), None)
        cost = int(cost) if cost == int(cost) else cost
        self.estimatedCostEntry.insert(0, cost)
        self.data_functions.validate_entry(event=None, widget=self.estimatedCostEntry, dataType=float)
        self.statusEntry.insert(0, next((task.status for task in self.tasks if task.id == id), None))
        self.data_functions.validate_entry(event=None, widget=self.statusEntry, dataType="")
        self.abouText.insert("1.0", next((task.about for task in self.tasks if task.id == id), None))
        self.selectCategoryVar.set(next((task.category.id for task in self.tasks if task.id == id), 1))

        root.wait_window(self.addTaskWindow)  # ウインドウが閉じられるまで待機

    def setNewTask(self, id, dispOrder):
        title = self.titleEntry.get()
        priority = self.priorityEntry.get()
        estimatedCost = self.estimatedCostEntry.get()
        status = self.statusEntry.get()
        about = self.abouText.get("1.0", "end-1c")
        category = self.category_list.categories[int(self.selectCategoryVar.get())-1]
        if next((task.check for task in self.tasks if task.id == id), False):
            self.new_task = {"id": id, "title": str(title), "priority": int(priority), "estimatedCost": float(estimatedCost), "status": str(status), "check": True, "category": Category.model_validate(category), "displayOrder": dispOrder, "about": str(about)}
        else:
            self.new_task = {"id": id, "title": str(title), "priority": int(priority), "estimatedCost": float(estimatedCost), "status": str(status), "check": False, "category": Category.model_validate(category), "displayOrder": dispOrder, "about": str(about)}
        
    def addTask(self, *_):
        dispOrder = int(self.dispOrderEntry.get())
        count = sum(1 for task in self.tasks if task.displayOrder != 9999)
        if dispOrder > count+1:
            dispOrder = count+1
        self.setNewTask(len(self.tasks)+1, dispOrder)
        self.controller.addTask(self.new_task)
        print("store")

    def editTask(self, id, *_):
        task = self.tasks[id-1]
        dispOrder = int(self.dispOrderEntry.get())
        self.setNewTask(task.id, dispOrder)
        self.controller.editTask(self.new_task, task.id, self.beforeDispOrder)
    
    def deleteTask(self, id, *_):
        def deleteTaskExecution():
            task = self.tasks[id-1]
            self.addTaskWindow.destroy()
            slaves = self.taskDispFrame.taskListWrapFrame.pack_slaves()
            slaves[task.displayOrder-1].destroy()
            self.controller.deleteTask(id)
        
        # ダイアログウィンドウ作成
        dialog = DeleteDialogModal(root, "削除確認", "この項目を削除しますか?", deleteTaskExecution)






class Controller():
    def __init__(self, root):
        # ファイルの読み込み

        # self.task_listは下記のようにタスクデータを保有するインスタンス
        # TaskList(tasks=[Task(id=1, title='SNS開設', priority=3, estimatedCost=3.0, status='未着手', category=Category(id=4, title='発信・まとめ', color='#E7B21D'), displayOrder=1, about=''), Task(id=2, title='サンプルサイト開発', priority=2, estimatedCost=10.0, status='取組中', category=Category(id=1, title='実践', color='#C2F25B'), displayOrder=2, about='')])
        # self.category_listは同様にカテゴリデータを保有するインスタンス

        self.costSumList = []
        self.app_status = ""

        self.selectedSortID = 1
        self.selectedFilterStatusList = [True, True, True, True, True]
        self.filterStatusNameList = ["未実施", "取組中", "保留", "完了", "その他"]

        with open("./data.json", mode='r', encoding="utf-8") as json_data:
            data = json.load(json_data)

            try:
                tasks=[]
                for task in data["tasks"]:
                    tasks.append(Task.model_validate(task))
                self.task_list = TaskList(tasks=tasks)

                self.calcCostSum()

                categories=[]
                for category in data["categories"]:
                    categories.append(Category.model_validate(category))
                self.category_list = CategoryList(categories=categories)

                goallines=[]
                for goalline in data["goallines"]:
                    goallines.append(GoalLine.model_validate(goalline))
                self.goalline_list = GoalLineList(goallines=goallines)

                self.project_title = data["projecttitle"]

                self.view = View(root, self)
                self.view.pack(expand=True, fill=tk.BOTH)


            except ValidationError as e:
                print("open-data-error!!")
                print(e)


    def save_tasks_on_exit(self):
        updated_data = {
            "tasks": [task.model_dump() for task in self.task_list.tasks],
            "categories": [category.model_dump() for category in self.category_list.categories],
            "goallines": [goalline.model_dump() for goalline in self.goalline_list.goallines],
            "projecttitle": self.project_title
        }
        # 保存先ディレクトリがなければ作成
        with open("./data.json", mode='w', encoding="utf-8") as json_file:
            json.dump(updated_data, json_file, indent=4, ensure_ascii=False)


    def addTask(self, new_task):
        try:
            new_task = Task.model_validate(new_task)
            self.task_list.tasks.append(new_task)
            self.view.taskDispFrame.addTaskList(new_task.displayOrder, new_task)
            print("success-add")
            self.calcCostSum()
            self.view.visualizeFrame.graphViewFrame.updateGraph()
        except ValidationError as e:
            print("error!!")
            print(e)

    def editTask(self, new_task, id, beforeDispOrder):
        try:
            new_task = Task.model_validate(new_task)
            next((task.category.id for task in self.task_list.tasks if task.id == id), 0)
            for i, task in enumerate(self.task_list.tasks):
                if task.id==id:
                    del self.task_list.tasks[i]
                    self.task_list.tasks.insert(i, new_task)
    

            afterDispOrder = int(new_task.displayOrder)

            if beforeDispOrder < afterDispOrder:
                for task in self.task_list.tasks:
                    if task.displayOrder <= afterDispOrder and task.displayOrder > beforeDispOrder and task.id != id:
                        task.displayOrder -= 1
            elif beforeDispOrder > afterDispOrder:
                for task in self.task_list.tasks:
                    if task.displayOrder >= afterDispOrder and task.displayOrder < beforeDispOrder and task.id != id:
                        task.displayOrder += 1
            
            self.view.taskDispFrame.editTaskList(id, new_task)
            self.calcCostSum()

            self.view.visualizeFrame.graphViewFrame.updateGraph()
            print("success-edit")
        except ValidationError as e:
            print("error!!")
            print(e)

    def deleteTask(self, id):
        task = self.task_list.tasks[id-1]
        targetDispOrder = task.displayOrder
        task.displayOrder = 9999

        for i, task in enumerate(self.task_list.tasks):
            if task.displayOrder > targetDispOrder and task.displayOrder!=9999:
                self.task_list.tasks[i].displayOrder = task.displayOrder-1
        self.view.taskDispFrame.displayAllTasks(1)
            

    def calcCostSum(self):
        self.costSumList = self.task_list.calcCostSum(
            self.selectedSortID,
            self.selectedFilterStatusList,
            self.filterStatusNameList
        )
        

    def addGoalline(self, new_goalline):
        try:
            new_goalline = GoalLine.model_validate(new_goalline)
            self.goalline_list.add(new_goalline)
            
            self.withAddEditGoalline()

            print("success-add")
                
        except ValidationError as e:
            print("error!!")
            print(e)


    def editGoalline(self, new_goalline, id):
        try:
            new_goalline = GoalLine.model_validate(new_goalline)

            # データを書き換えて、位置を変えるメソッドを実行
            self.goalline_list.replace_at_same_position(new_goalline)

            self.withAddEditGoalline()

            print("success-edit")
        except ValidationError as e:
            print("error!!")
            print(e)

    def deleteGoalline(self, id):
        del self.goalline_list.goallines[id-1]

        for goalline in self.goalline_list.goallines:
            if goalline.id > id:
                goalline.id = goalline.id + 1
        
        self.withUpdateGoalline()


    def withAddEditGoalline(self):
        for key, val in list(self.view.taskDispFrame.goalLineUnitFrameList.items()):
            val["frame"].destroy()
        self.view.taskDispFrame.goalLineUnitFrameList.clear()

        dispGoalLineHeight = self.view.taskDispFrame.taskDispAreaHeight
        sortedGoallines = sorted(self.goalline_list.goallines, key=lambda goalline: goalline.cost)

        for goalLine in sortedGoallines:
            dispGoalLineHeight = self.view.goalline_functions.dispGoalLine(goalLine, dispGoalLineHeight, self.view.taskDispFrame)

        self.withUpdateGoalline()


    def withUpdateGoalline(self):

        visualizeFrame = self.view.visualizeFrame
        visualizeFrame.graphViewFrame.updateGraph()
        visualizeFrame.styles.bind_to_all_children(visualizeFrame.visualizeCanvas, "<MouseWheel>", visualizeFrame.on_mousewheel_visualize)
        visualizeFrame.viewGoallineListFrame.updateFrame()
        visualizeFrame.viewGoallineListFrame2.updateFrame()


    def editCategory(self, id, new_title):
        self.category_list.categories[id-1].title = new_title





if __name__ == "__main__":
    root = tk.Tk()
    root.title("タスク管理アプリ")
    root.geometry("978x640")

    controller = Controller(root)

    
    def on_close():
        controller.save_tasks_on_exit()
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
