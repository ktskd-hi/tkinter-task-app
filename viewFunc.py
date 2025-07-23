import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from task import GoalLineList,GoalLine
from pydantic import ValidationError


from PIL import Image, ImageTk



class Modal(tk.Toplevel):
    def __init__(self, master, title, width, height, bg):
        # 継承元クラス（tk.Toplevel）のコンストラクタを呼び出し
        super().__init__(master, bg=bg)

        self.withdraw()  # 最初は非表示
        self.after(100, self.deiconify)   # 少し待ってから表示（チラつき防止）

        self.title(title)
        self.geometry(str(width)+"x"+str(height))

        # 親ウインドウを操作できないようにする
        self.transient(master)        # 親ウインドウの前面に表示
        self.grab_set()        # モーダル化

        # 閉じるボタン（✕）でウインドウを閉じたときの処理
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # 親ウインドウの位置とサイズを取得
        master.update_idletasks()  # 最新のサイズ・位置を取得するために必要
        x = master.winfo_rootx()
        y = master.winfo_rooty()
        root_width = master.winfo_width()
        root_height = master.winfo_height()

        # 中央の位置を計算
        pos_x = x + (root_width - width) // 2
        pos_y = y + (root_height - height) // 2

        # 位置とサイズを設定
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y-16}")

        self.blankPanel = tk.Frame(self, bg=bg)
        self.blankPanel.place(x=0,y=0,width=width,height=height)

        self.after(500, self.blankPanel.place_forget)




class EditModal(Modal):
    def __init__(self, master, title, width, height, bg, command, id):
        # 継承元クラス（tk.Toplevel）のコンストラクタを呼び出し
        super().__init__(master, title, width, height, bg)

        self.command = command
        self.id = id

        StoreButton(self, x=288, y=464, text="保存", command=lambda: self.commandFunc(), id=id)

    def commandFunc(self):
        self.command(self.id)
        self.destroy()

class DeleteDialogModal(tk.Toplevel):
    def __init__(self, master, title, text, command):
        # 継承元クラス（tk.Toplevel）のコンストラクタを呼び出し
        super().__init__(master, bg="#324A5F")

        self.title(title)
        self.configure(bg="#324A5F")  # 背景色
        self.geometry("248x112")  # 幅300px × 高さ150px
        self.resizable(False, False)

        # ウィンドウ中央に配置
        self.geometry("+%d+%d" % (
            master.winfo_rootx() + master.winfo_width() // 2 - 100,
            master.winfo_rooty() + master.winfo_height() // 2 - 50
        ))

        # ラベル
        label = tk.Label(self, text=text, fg="#FFF", bg="#324A5F", font=("Noto sans jp", 12))
        label.pack(padx=20, pady=16)

        # ボタンフレーム
        btn_frame = tk.Frame(self, bg="#324A5F")
        btn_frame.pack(pady=4)

        # はいボタン
        yesButtonStyle = ttk.Style()
        yesButtonStyle.configure("deleteYes.TButton", 
            font=("Noto Sans jp", 10),
            background="#C03939",foreground="#FFF",
            relief="flat",
            width=6, padding=(10, 2)
        )
        yesButtonStyle.map("deleteYes.TButton",
          background=[("active", "#D14242")]
        )
        yes_btn = ttk.Button(btn_frame,
            style = "deleteYes.TButton",
            text="はい",
            command=lambda: [command(), self.destroy()], 
            takefocus=0, cursor="hand2"
        )
        yes_btn.pack(side="left", padx=10)

        # いいえボタン
        noButtonStyle = ttk.Style()
        noButtonStyle.configure("deleteNo.TButton", 
            font=("Noto Sans", 10),
            background="#56718A",foreground="#FFF",
            relief="flat",
            width=6, padding=(10, 4.6)
        )
        noButtonStyle.map("deleteNo.TButton",
          background=[("active", "#5E7B96")]
        )
        no_btn = ttk.Button(btn_frame, 
            style = "deleteNo.TButton",
            text="いいえ",
            command=self.destroy, 
            takefocus=0, cursor="hand2"
        )
        no_btn.pack(side="left", padx=10)

        # モーダルにする（親が操作できないように）
        self.transient(master)
        self.grab_set()
        master.wait_window(self)




class StoreButton(ttk.Button):
    def __init__(self, master, x, y, text, command, id):
        # 継承元クラス（tk.Toplevel）のコンストラクタを呼び出し

        super().__init__(
            master, 
            text=text, 
            command= command,
            style="Store.TButton",
            cursor="hand2",
            takefocus=0
        )
        
        # 保存ボタン
        self.addButtonStyle = ttk.Style()
        self.addButtonStyle.theme_use("default")
        self.addButtonStyle.configure("Store.TButton",
            font=("Noto Sans JP", 12),
            background="#063661",
            foreground="#FFF",
            relief="flat",
        )
        self.addButtonStyle.map("Store.TButton",
            background=[("active", "#093F6E")],  # ホバー時の背景
            foreground=[("active", "#FFF")]     # ホバー時の文字色（変更しないなら省略可）
        )

        self.place(x=x, y=y, width=240, height=44)


class DeleteButton():
    def __init__(self, master, command, id, y_pos):
        self.taskDeleteButton = ttk.Style()
        self.taskDeleteButton.configure("delete.TButton", 
            font=("Noto Sans JP", 12),
            background="#322323",foreground="#FF4040",
            relief = "flat", borderwidth=0
        )
        self.taskDeleteButton.map("delete.TButton",
            background=[("active", "#3D2B2B")],
            foreground=[("active", "#FF4848")]
        )
        self.deleteButton = ttk.Button(master,
            style="delete.TButton",
            text="この項目を削除",
            cursor="hand2", takefocus=0,
            command=lambda: command(id),
        )
        self.deleteButton.place(x=8, y=y_pos, width=144, height=32)

    def reposition(self, y_pos):
        self.deleteButton.place(x=8, y=y_pos, width=144, height=32)


class AddTaskWindowEntry(tk.Entry):
    def __init__(self, master, justify):
        # 継承元クラス（tk.Toplevel）のコンストラクタを呼び出し

        super().__init__(master,
            bg="#253645",
            fg="#FFF",
            insertbackground="#FFF",  # キャレット色
            relief="flat",           # フラット
            bd=0,                    # 枠なし
            highlightthickness=1,    # 任意の枠線
            highlightbackground="#253645",  # 非アクティブ時の枠線色
            highlightcolor="#253645",       # アクティブ時の枠線色
            font=("Noto Sans JP", 12),
            justify=justify
        )

class Styles():
    def __init__(self):
         # スクロールバー用のスタイルを定義
        self.taskDispScrollbarStyle = ttk.Style()
        self.taskDispScrollbarStyle.theme_use('default')  # カスタマイズが反映されやすいテーマを使用
        # self.taskDispScrollbarStyle = Style()
        
        # スクロールバー用のスクロールバーのスタイル設定
        self.taskDispScrollbarStyle.configure(
            "Vertical.TScrollbar",
            background="#506F8B",      # スライダーの
            troughcolor="#273949",     # トラックの色（灰色）
            bordercolor="#273949",
            lightcolor="#273949",
            darkcolor="#273949",
            arrowcolor="#314B61",
            width=6,                  # スクロールバーの幅
            borderwidth=0,
            relief="flat"
        )
        # ホバー状態で色が変わらないようにmapを無効化
        self.taskDispScrollbarStyle.map("Vertical.TScrollbar",
                background=[("active", "#507392")],  # hover
                arrowcolor=[("active", "#506F8B")])
        
        
    def get_all_descendants(self, widget):
        descendants = []
        for child in widget.winfo_children():
            descendants.append(child)
            descendants.extend(self.get_all_descendants(child))  # 再帰的に追加
        return descendants

    def bind_to_all_children(self, frame, sequence, func):
        frame.bind(sequence, func)
        for widget in self.get_all_descendants(frame):
            widget.bind(sequence, func)

    @staticmethod
    def adjust_brightness(hex_color: str, brightness: float) -> str:
        """
        16進カラーにbrightnessを適用して返す。
        - hex_color: '#RRGGBB'形式
        - brightness: 明るさ係数（例: 0.5=暗く, 1.0=そのまま, 1.5=明るく）
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("hex_color must be in the format '#RRGGBB'")
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # 明るさ係数を掛けて255でクリップ
        r = min(int(r * brightness), 255)
        g = min(int(g * brightness), 255)
        b = min(int(b * brightness), 255)

        # 再び16進数に変換
        return "#{:02X}{:02X}{:02X}".format(r, g, b)
    
    def unbind_from_all_children(self, widget, sequence):
        widget.unbind(sequence)
        for child in widget.winfo_children():
            self.unbind_from_all_children(child, sequence)


class DataFunctions():
    def __init__(self):
        pass
    
    def validate_entry(self, event, widget, dataType):
        if isinstance(widget, tk.Text):
            val = widget.get("1.0", "end-1c")
        else:
            val = widget.get()
        try:
            if val.strip() == "":
                raise ValueError("空")
            if dataType:
                dataType(val)  # 整数でなければ例外
            # int(val)  # 整数でなければ例外
            widget.config(highlightthickness=2, highlightbackground="#3B5871", highlightcolor="#3B5871")  # 正常：枠色リセット
        except ValueError:
            widget.config(highlightthickness=2, highlightbackground="#DF3838", highlightcolor="#D34444")   # 異常：赤枠にする


class WidgetFundtions():
    def __init__(self):
        pass
    
    @staticmethod
    def get_all_descendants(widget):
        descendants = []
        for child in widget.winfo_children():
            descendants.append(child)
            descendants.extend(WidgetFundtions.get_all_descendants(child))  # 再帰的に追加
        return descendants



class GoallineFunctions():
    def __init__(self, root, controller, goalline_list):
        self.root = root
        self.controller = controller
        self.goalline_list = goalline_list
        self.data_functions = DataFunctions()
        self.colors = [
            dict(bg="#E3A8DD", fg="#1C242B"),
            dict(bg="#A48DFF", fg="#1C242B"),
            dict(bg="#F9BA9F", fg="#1C242B"),
            dict(bg="#E9F877", fg="#1C242B")
        ]
        self.new_goalline = {}
        self.goallineUnitSlaves = {}

        self.edit_icon = tk.PhotoImage(file="./imgs/edit_icon_3.png")

        self.styles = Styles()

        self.graphDispVarList = {}

    def calcGoalLine(self, goalLine):
        pos = -60
        cost = float(goalLine.cost)
        costSumList = self.controller.costSumList
        if costSumList != []:
            for i, costSum in enumerate(costSumList):
                if cost <= costSum:
                    seq = i-1 if i!=0 else 1
                    last_num = costSumList[seq] if i!=0 else 0
                    deno = (costSum - last_num)
                    deno = 1 if deno == 0 else deno
                    add_num = 44*(cost - last_num) / deno
                    if add_num > 44:
                        add_num = 44
                    pos = add_num + 44*(i) + 2
                    break
            if pos==-60:
                sortedTask = self.controller.task_list.getSortedTaskList(self.controller.selectedSortID)

                if costSumList != []:
                    # for costSum in reversed(costSumList):
                    for i in range(len(costSumList)-1, -1, -1):
                        if sortedTask[i].check and costSum!=0:
                            last_num = costSum
                            deno = (costSum - last_num)
                            deno = 1 if deno == 0 else deno
                            add_num = 44*(cost - last_num) / deno
                            if add_num > 44:
                                add_num = 44
                            pos = add_num + 44*(i) + 2
                            break
                    # deno = costSumList[-1] if costSumList[-1] !=0 else 1
                    # rate = (cost / deno)
                    # cost_list_size = 44*(len(costSumList))
                    # pos = cost_list_size * rate
        return pos


    def dispGoalLine(self, goalLine, dispGoalLineHeight, taskDispFrame):
        goalLineUnitFrame = tk.Frame(taskDispFrame.goalLineWrapFrame, 
            width=132, height=47, bg="#2B455B"
        )
        cost = goalLine.cost
        cost = int(cost) if cost == int(cost) else cost
        goalLineLineButton = tk.Label(goalLineUnitFrame, 
            bg=self.colors[goalLine.color_id-1]["bg"], 
            fg=self.colors[goalLine.color_id-1]["fg"],
            anchor="w", justify="left",
            text=cost, font=("Noto Sans JP", 11, "bold"),
        )

        bgColor = self.colors[goalLine.color_id-1]["bg"]

        canvas = tk.Canvas(goalLineUnitFrame, bg="#2B455B", highlightthickness=0)
        canvas.place(x=0, y=4, width=10, height=10)

        # 三角形の座標（左向き）
        triangle = canvas.create_polygon(
            10, 0,  # 右上
            10, 10,  # 右下
            0, 5, # 左頂点
            fill=bgColor, outline=""
        )

        edit_icon_button = tk.Button(goalLineUnitFrame,
            bg=bgColor, 
            image=self.edit_icon,
            anchor="center", justify="center",
            cursor="hand2", relief="flat", bd=0, highlightthickness=0,
            command=lambda: self.openEditGoallineWindow(goalLine.id),
            activebackground=bgColor  # クリック時背景色

        )
        edit_icon_button.place(x=106, y=0, width=24, height=20)

        goalLineNameButton = tk.Label(goalLineUnitFrame, 
            bg="#54718B", fg="#FFF", 
            anchor="w", justify="left",
            text=goalLine.title, font=("Noto Sans JP", 14, "normal")
        )

        self.goallineUnitSlaves[goalLine.id] = dict(line_button=goalLineLineButton, name_button=goalLineNameButton)
        
        y_pos = self.calcGoalLine(goalLine)
        goalLineUnitFrame.place(x=4, y=y_pos-11
        , width=130, height=47)
        goalLineLineButton.place(x=10, y=0, width=96, height=20)
        goalLineNameButton.place(x=10, y=22, width=120, height=26)
        taskDispFrame.goalLineUnitFrameList[goalLine.id] = {'frame': goalLineUnitFrame}

        if dispGoalLineHeight > y_pos+47:
            return dispGoalLineHeight
        else:
            return y_pos+47

    

    def openWriteGoallineWindow(self, command, id, dispPattern):
        self.addGoallineWindow = EditModal(self.root, "タスクを追加", 800, 548, "#324A5F", command, id)

        # ラベルや他のUI
        font = ("Noto Sans JP", 12)
        font2 = ("Noto Sans JP", 14)

        self.categorySizeEntry = {}

        # 各プロパティ入力
        self.addProperties = tk.Frame(self.addGoallineWindow, background="#324A5F")
        self.addProperties.place(x=32, y=42, width=528, height=400)

        self.writeGoallineCanvas = tk.Canvas(self.addProperties, bg="#324A5F", bd=0, highlightthickness=0, relief='flat')
        self.writeGoallineInnerFrame = tk.Frame(self.writeGoallineCanvas, width=528, height=616, bg="#324A5F", borderwidth=0, relief="flat")
        if dispPattern == 1:
            self.writeGoallineInnerFrame.config(height=548)

        ttk.Label(self.writeGoallineInnerFrame, text="項目名", foreground="#FFF", font=font, background="#324A5F").place(x=8, y=-1, width=48, height=40)
        self.titleEntry = AddTaskWindowEntry(self.writeGoallineInnerFrame, "left")
        self.titleEntry.place(x=64, y=0, width=424, height=40)
        self.titleEntry.bind("<Configure>", lambda event: self.data_functions.validate_entry(event, self.titleEntry, ""))
        self.titleEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.titleEntry, ""))
        self.titleEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.titleEntry, ""))
        self.addGoallineWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.titleEntry, dataType=""))

        ttk.Label(self.writeGoallineInnerFrame, text="想定コスト", foreground="#FFF", font=font, background="#324A5F").place(x=8, y=55, width=80, height=40)
        self.costEntry = AddTaskWindowEntry(self.writeGoallineInnerFrame, "center")
        self.costEntry.place(x=96, y=56, width=48, height=40)
        self.costEntry.bind("<Configure>", lambda event: self.data_functions.validate_entry(event, self.costEntry, float))
        self.costEntry.bind("<KeyRelease>", lambda event: self.data_functions.validate_entry(event, self.costEntry, float))
        self.costEntry.bind("<FocusOut>", lambda event: self.data_functions.validate_entry(event, self.costEntry, float))
        self.addGoallineWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.costEntry, dataType=float))
        
        self.memoLabel = ttk.Label(self.writeGoallineInnerFrame, text="メモ", foreground="#FFF", font=font2, background="#324A5F")
        self.memoTextFrame = tk.Frame(self.writeGoallineInnerFrame, background="#324A5F")
        self.memoText = tk.Text(self.memoTextFrame, bg="#253645", fg="#FFF", relief="flat", bd=0, insertbackground="#FFF", font=("Noto Sans JP", 12), wrap="word")
        self.memoText.pack(side="left", fill="both")
        self.memoText.bind("<Control-z>", lambda e: self.memoText.edit_undo())
        

        ttk.Label(self.writeGoallineInnerFrame, text="グラフに表示", foreground="#FFF", font=font, background="#324A5F").place(x=8, y=112, width=96, height=40)
        self.graphDispVarList[id] = tk.BooleanVar()
        self.graphDispVarList[id].set(False)
        self.checkbox = tk.Checkbutton(self.writeGoallineInnerFrame, 
            text="", 
            background="#324A5F",
            width=20,  # サイズ調整（任意）
            height=20,
            padx=0, pady=0, bd=0,
            activebackground="#324A5F",  # クリック時背景色
            highlightthickness=0,    # フォーカス枠なし
            variable=self.graphDispVarList[id],
            command=lambda id=id:self.graphDispCheckFunction(id),
            relief="flat"
        )
        self.checkbox.place(x=112, y=112, width=32, height=40)


        # カテゴリごとの数値の編集
        self.editCategorySizesFrame = tk.Frame(self.writeGoallineInnerFrame, background="#324A5F")


        self.categorySizeList = {}
        self.deleteButton = ""

        if dispPattern == 1:
            self.memoLabel.place(x=8, y=164, width=40, height=40)
            self.memoTextFrame.place(x=8, y=204, width=480, height=126)

            for category in self.controller.category_list.categories:
                self.categorySizeList[category.id] = tk.StringVar()
                self.categorySizeList[category.id].set(0)


        if dispPattern == 2:
            
            for category in self.controller.category_list.categories:
                self.categorySizeList[category.id] = tk.StringVar()
                cost = self.controller.goalline_list.goallines[id-1].categorySize[category.id-1]
                cost = int(cost) if cost == int(cost) else cost
                self.categorySizeList[category.id].set(cost)

            self.graphDispVarList[id].set(self.goalline_list.goallines[id-1].graphDisp)
            

            # メモ、削除ボタン配置
            if(self.graphDispVarList[id].get()):
                self.memoLabel.place(x=8, y=368, width=40, height=40)
                self.memoTextFrame.place(x=8, y=408, width=480, height=126)
                self.deleteButton = DeleteButton(self.writeGoallineInnerFrame, self.deleteGoalline, id, 564)
            else:
                self.memoLabel.place(x=8, y=164, width=40, height=40)
                self.memoTextFrame.place(x=8, y=204, width=480, height=126)
                self.deleteButton = DeleteButton(self.writeGoallineInnerFrame, self.deleteGoalline, id, 356)



        if(self.graphDispVarList[id].get()):
            self.editCategorySizesFrame.place(x=8, y=160, width=208, height=180)

        for i, category in enumerate(self.controller.category_list.categories):
            editCategorySizeFrame = tk.Frame(self.editCategorySizesFrame, width=208, height=64, background="#324A5F")
            editCategorySizeFrame.pack(side="top", pady=6, anchor="nw")

            tk.Frame(editCategorySizeFrame, bg=category.color, width=32, height=16).pack(side="left", anchor="w")
            tk.Label(editCategorySizeFrame, bg="#324A5F", text=category.title, fg="#FFF", font=font).pack(side="left", padx=4, anchor="w")

            self.categorySizeEntryWrapFrame = tk.Frame(editCategorySizeFrame, width=48, height=32)
            self.categorySizeEntry[i] = AddTaskWindowEntry(self.categorySizeEntryWrapFrame, "center")
            self.categorySizeEntry[i].config(textvariable=self.categorySizeList[category.id])
            self.categorySizeEntryWrapFrame.pack(side="left")
            self.categorySizeEntry[i].place(x=0,y=0,width=48,height=32)
            self.categorySizeEntry[i].bind("<Configure>", lambda event, w=self.categorySizeEntry[i]: self.atCreateCategorySizeEntry(event, w))
            self.categorySizeEntry[i].bind("<KeyRelease>", lambda event, w=self.categorySizeEntry[i]: self.atCreateCategorySizeEntry(event, w))
            self.categorySizeEntry[i].bind("<FocusOut>", lambda event, w=self.categorySizeEntry[i]: self.atCreateCategorySizeEntry(event, w))

            self.addGoallineWindow.after(0, self.data_functions.validate_entry(event=None, widget=self.categorySizeEntry[i], dataType=float))

        self.propertySumName = ttk.Label(self.writeGoallineInnerFrame, text="プロパティ合計:", foreground="#FFF", font=font, background="#324A5F")
        self.propertySumLabel = ttk.Label(self.writeGoallineInnerFrame, text="-", foreground="#FFF", font=font2, background="#324A5F")
        if(self.graphDispVarList[id].get()):
            self.propertySumName.place(x=172, y=118, width=120, height=24)
            self.propertySumLabel.place(x=300, y=116, width=120, height=28)

        
        self.calcCategorySize()    

        # 色の選択
        addColor = tk.Frame(self.addGoallineWindow, background="#324A5F")
        addColor.place(x=584, y=122, width=208, height=180)

        self.selectColorVar = tk.StringVar(value="1")
        for i, color in enumerate(self.colors):
            selectColorFrame = tk.Frame(addColor, width=208, height=32, background="#324A5F")
            selectColorFrame.pack(side="top", pady=4)
            tk.Radiobutton(selectColorFrame, text="", variable=self.selectColorVar, value=i+1, fg="#142C30", bg="#324A5F", activebackground="#324A5F", selectcolor="white", cursor="hand2", relief="flat", bd=0).place(x=0,y=0,width=24,height=24)
            tk.Frame(selectColorFrame, bg=color["bg"]).place(x=28, y=4, width=32, height=16)


    
        # スクロールバー

        # スクロールバー用のスクロールバーのスタイル設定
        self.writeGoallineScrollbarStyle = ttk.Style()
        self.writeGoallineScrollbarStyle.theme_use('default')  # カスタマイズが反映されやすいテーマを使用

        self.writeGoallineScrollbarStyle.configure(
            "Custom.Vertical.TScrollbar",
            background="#3C5C77",      # スライダーの
            troughcolor="#2C4459",     # トラックの色（灰色）
            bordercolor="#2C4459",
            lightcolor="#2C4459",
            darkcolor="#2C4459",
            arrowcolor="#2C4459",      # 見えなくする用（矢印を目立たせない）
            width=2,                  # スクロールバーの幅
            borderwidth=0,
            relief="flat"
        )
        # ホバー状態で色が変わらないようにmapを無効化
        self.writeGoallineScrollbarStyle.map("Custom.Vertical.TScrollbar",
                background=[("active", "#3E5F7A")],  # hover
                arrowcolor=[("active", "#3C5C77")])
        self.writeGoallineScrollbar = ttk.Scrollbar(self.addProperties,
            orient=tk.VERTICAL,
            command=self.writeGoallineCanvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        self.writeGoallineCanvas.configure(yscrollcommand=self.writeGoallineScrollbar.set)

         # CanvasにFrameを埋め込む
        window_id = self.writeGoallineCanvas.create_window((0, 0), window=self.writeGoallineInnerFrame, anchor="nw")

        def on_frame_configure(event):
            bbox = self.writeGoallineCanvas.bbox("all")
            self.writeGoallineCanvas.configure(scrollregion=bbox)
            self.writeGoallineCanvas.itemconfig(window_id, width=self.writeGoallineCanvas.winfo_width())

            self.writeGoallineCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            if self.graphDispVarList[id].get():
                self.styles.bind_to_all_children(self.addProperties, "<MouseWheel>", self.on_mousewheel_writeGoalline)
                self.writeGoallineScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                self.styles.bind_to_all_children(self.addProperties, "<MouseWheel>", self.on_mousewheel_writeGoallineLock)
                self.writeGoallineScrollbar.pack_forget()
        
        self.addGoallineWindow.bind("<Configure>", on_frame_configure)

    def graphDispCheckFunction(self, id):
        if self.graphDispVarList[id].get():
            self.dispSetCategorySizeList()
        else:
            self.forgetCategorySizeList()


    def dispSetCategorySizeList(self):
        self.propertySumName.place(x=172, y=118, width=120, height=24)
        self.propertySumLabel.place(x=300, y=116, width=120, height=28)
        self.editCategorySizesFrame.place(x=8, y=160, width=208, height=180)
        self.memoLabel.place(x=8, y=368, width=40, height=40)
        self.memoTextFrame.place(x=8, y=408, width=480, height=126)
        if self.deleteButton != "":
            self.deleteButton.reposition(564)

    def forgetCategorySizeList(self):
        self.propertySumName.place_forget()
        self.propertySumLabel.place_forget()
        self.editCategorySizesFrame.place_forget()
        self.memoLabel.place(x=8, y=164, width=40, height=40)
        self.memoTextFrame.place(x=8, y=204, width=480, height=126)
        if self.deleteButton != "":
            self.deleteButton.reposition(356)



    def calcCategorySize(self):
        propertySum = 0
        for key, categorySizeEntry in self.categorySizeEntry.items():
            if categorySizeEntry.get() != "":
                propertySum += float(categorySizeEntry.get())
        propertySum = int(propertySum) if propertySum == int(propertySum) else propertySum
        self.propertySumLabel.config(text=propertySum)

    def atCreateCategorySizeEntry(self, event, w):
        self.data_functions.validate_entry(event, w, float)
        self.calcCategorySize()


    def on_mousewheel_writeGoalline(self, event):
        self.writeGoallineCanvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_mousewheel_writeGoallineLock(self, event):
        self.writeGoallineCanvas.yview_scroll(0, "units")

    def openAddGoallineWindow(self):
        self.openWriteGoallineWindow(self.addGoalline, len(self.goalline_list.goallines)+1, 1)
            
        # モーダルのイベントループを開始
        self.root.wait_window(self.addGoallineWindow)  # ウインドウが閉じられるまで待機

    def openEditGoallineWindow(self, id):
        self.openWriteGoallineWindow(self.editGoalline, id, 2)

        goalline = next((goalline for goalline in self.goalline_list.goallines if goalline.id == id), None)
        if goalline:
            self.titleEntry.insert(0, goalline.title)

            cost = goalline.cost
            cost = int(cost) if cost == int(cost) else cost
            self.costEntry.insert(0, cost)
            self.memoText.insert("1.0", goalline.memo)
            self.selectColorVar.set(goalline.color_id)


    def setNewGoalline(self, id):
        title = self.titleEntry.get()
        cost = self.costEntry.get()
        memo = self.memoText.get("1.0", "end-1c")
        color_id = int(self.selectColorVar.get())
        graphDispBool = self.graphDispVarList[id].get()

        categorySizeList = []
        for key, categorySize in self.categorySizeList.items():
            categorySizeList.append(categorySize.get())

        self.new_goalline = {"id": id, "title": str(title), "cost": float(cost), "color_id": color_id, "memo": str(memo), "graphDisp": graphDispBool, "categorySize": categorySizeList}


    def addGoalline(self, *_):
        self.setNewGoalline(len(self.goalline_list.goallines)+1)
        print("goalline-store")
        self.controller.addGoalline(self.new_goalline)
        self.controller.view.visualizeFrame.viewGoallineListFrame.updateFrame()

    def editGoalline(self, id, *_):
        # ボタンに紐づけているidが来る
        self.setNewGoalline(id)
        self.controller.editGoalline(self.new_goalline, id)
        self.controller.view.visualizeFrame.viewGoallineListFrame.updateFrame()

    def deleteGoalline(self, id, *_):
        def deleteGoallineExecution():
            goalLine = self.goallineUnitSlaves[id]
            for widget in goalLine.values():
                widget.destroy()
            self.addGoallineWindow.destroy()
            self.controller.deleteGoalline(id)
            del self.goallineUnitSlaves[id]

            self.controller.view.taskDispFrame.goalLineUnitFrameList[id]['frame'].destroy()
            del self.controller.view.taskDispFrame.goalLineUnitFrameList[id]
        
        # ダイアログウィンドウ作成
        dialog = DeleteDialogModal(self.root, "削除確認", "この項目を削除しますか?", deleteGoallineExecution)


class TaskTitle():
    def __init__(self, parent, text, controller):
        self.controller = controller
        self.text_var = tk.StringVar()
        self.text_var.set(text)

        self.edit_icon = tk.PhotoImage(file="./imgs/edit_icon_2.png")

        self.label = tk.Label(parent, 
            textvariable=self.text_var,
            font=("Noto Sans JP", 13),
            foreground="#FFF",
            background="#112F48",
        )
        self.label.pack(side="left", padx=4)

        self.entry = tk.Entry(parent,
            bg="#0F1E2B", fg="#FFF",
            insertbackground="#FFF",  
            relief="flat", bd=0,
            borderwidth=2,
            highlightthickness=1, 
            highlightbackground="#5A6D80",  
            highlightcolor="#4E667A",      
            font=("Noto Sans JP", 13),
            justify="left",
            width=40,
            textvariable=self.text_var,
            selectbackground="#4F8C9C"
        )

        self.taskTitleEditButton = ttk.Style()
        self.taskTitleEditButton.configure("taskTitleEdit.TButton", 
            font=("Noto Sans JP", 12),
            background="#112F48",foreground="#DADADA",
            relief = "flat", borderwidth=0
        )
        self.taskTitleEditButton.map("taskTitleEdit.TButton",
            background=[("active", "#112F48")],
            foreground=[("active", "#E5E5E5")]
        )

        self.taskTitleSaveButton = ttk.Style()
        self.taskTitleSaveButton.configure("taskTitleSave.TButton", 
            font=("Noto Sans JP", 12),
            background="#0F7592",foreground="#DADADA",
            relief = "flat", borderwidth=0
        )
        self.taskTitleSaveButton.map("taskTitleSave.TButton",
            background=[("active", "#14809E")],
            foreground=[("active", "#E5E5E5")]
        )

        self.edit_button = ttk.Button(parent,
            style="taskTitleEdit.TButton",
            image=self.edit_icon, compound="center",
            # text="Edit",
            command=self.labelEdit,
            cursor="hand2", takefocus=0,
            width=4
        )
        self.edit_button.pack(side="left", padx=8)

        self.store_button = ttk.Button(parent,
            style="taskTitleSave.TButton",
            text="Save",
            command=self.store,
            cursor="hand2", takefocus=0,
            width=4
        )

    def labelEdit(self):
        entry = self.entry
        self.entry.pack(side="left", padx=3)
        entry.after(20, lambda: [entry.focus_set(), entry.icursor(tk.END)])
        
        self.label.pack_forget()
        self.edit_button.pack_forget()
        self.store_button.pack(side="left", padx=4)

    def store(self):
        new_title = self.entry.get()
        self.label.config(text=new_title)
        self.entry.pack_forget()
        self.label.pack(side="left", padx=4)
        self.controller.project_title = new_title
        self.edit_button.pack(side="left", padx=4)
        self.store_button.pack_forget()


class TaskHeader(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, width=543, height=24, bg="#2A445A")

        self.header_img_01 = tk.PhotoImage(file="./imgs/header_img_01.png")
        self.header_img_02 = tk.PhotoImage(file="./imgs/header_img_02.png")
        self.header_img_03 = tk.PhotoImage(file="./imgs/header_img_03.png")
        self.header_img_04 = tk.PhotoImage(file="./imgs/header_img_04.png")


        tk.Frame(self, bg="#324F67").place(x=2, y=2, width=20, height=20)
        tk.Frame(self, bg="#324F67").place(x=24, y=2, width=4, height=20)
        tk.Label(self, bg="#324F67", image=self.header_img_01, compound="center").place(x=30, y=2, width=32, height=20)
        tk.Label(self, bg="#324F67", image=self.header_img_02, compound="center").place(x=64, y=2, width=20, height=20)
        tk.Label(self, bg="#324F67", image=self.header_img_03, compound="center").place(x=86, y=2, width=32, height=20)
        tk.Label(self, bg="#324F67", fg="#F2F2F2", text="タイトル", font=("Noto Sans JP", 11), anchor="w").place(x=120, y=2, relwidth=1.0, width=-309, height=20)
        tk.Label(self, bg="#324F67", image=self.header_img_04, compound="center").place(x=-187, y=2, width=20, height=20, relx=1.0)
        tk.Label(self, bg="#324F67", fg="#F2F2F2", text="目安ライン", font=("Noto Sans JP", 11), anchor="w").place(x=-151, y=2, width=122, height=20, relx=1.0)



        
        




class CategoryListFrame():
    def __init__(self, parent, category, controller):

        self.category = category
        self.controller = controller
        self.edit_icon = tk.PhotoImage(file="./imgs/edit_icon_2.png")

        self.text_var = tk.StringVar()
        self.text_var.set(category.title)

        categoryListFrame = tk.Frame(parent,
            background="#324A5F", width=320, height=40, pady=16
        )
        categoryListFrame.pack(side="top")
        tk.Frame(categoryListFrame, bg=category.color).place(x=4, y=4, width=40, height=18)
        self.categoryNameLabel = tk.Label(categoryListFrame, 
            textvariable=self.text_var, 
            fg="#FFF", bg="#324A5F", font=("Noto Sans JP", 12)
        )
        self.categoryNameLabel.place(x=56, y=-3)
        self.categoryEditButton = tk.Button(categoryListFrame,
            command=self.categoryEdit,
            background="#324A5F", activebackground="#324A5F",
            image=self.edit_icon, compound="center", anchor="center", 
            cursor="hand2", relief="flat", bd=0, highlightthickness=0
        )
        self.categoryEditButton.place(x=280, y=4, width=40, height=18)
        self.categoryNameEntry = tk.Entry(categoryListFrame,
            textvariable=self.text_var, 
            bg="#132535", fg="#FFF",
            insertbackground="#FFF",  
            relief="flat", bd=0,
            borderwidth=2,
            highlightthickness=1,    
            highlightbackground="#5A6D80",  
            highlightcolor="#253645",      
            font=("Noto Sans JP", 12),
            justify="left",
            selectbackground="#4F8C9C"
        )
        
        self.categorySaveButton = ttk.Style()
        self.categorySaveButton.configure("categorySave.TButton", 
            font=("Noto Sans JP", 12),
            background="#0F7592",foreground="#DADADA",
            relief = "flat", borderwidth=0
        )
        self.categorySaveButton.map("categorySave.TButton",
            background=[("active", "#14809E")],
            foreground=[("active", "#E5E5E5")]
        )
        self.categorySaveButton = ttk.Button(categoryListFrame,
            style="categorySave.TButton",
            text="Save",
            command=self.categorySave,
            cursor="hand2", takefocus=0,
            padding=(0,-2)
        )


    def categoryEdit(self):
        self.categoryNameLabel.place_forget()
        entry = self.categoryNameEntry
        entry.place(x=55, y=-4, width=212, height=32)
        entry.after(20, lambda: [entry.focus_set(), entry.icursor(tk.END)])
        self.categoryEditButton.place_forget()
        self.categorySaveButton.place(x=272, y=-3, width=48, height=26)

    def categorySave(self):
        self.categoryNameLabel.place(x=56, y=-3)
        self.categoryNameEntry.place_forget()
        self.categoryEditButton.place(x=280, y=4, width=40, height=20)
        self.categorySaveButton.place_forget()
        self.controller.editCategory(self.category.id, self.text_var.get())



class GraphView(tk.Frame):
    def __init__(self, master, controller, visualizeFrame):
        super().__init__(master, width=348, height=326, bg="#324A5F")
        self.graph_bg = tk.Frame(master, bg="#324A5F", width=348, height=326)
        
        self.line_colors = ["#E3A8DD","#A48DFF","#F9BA9F","#E9F877"]

        self.controller = controller
        self.visualizeFrame = visualizeFrame
        self.colors = ['#7EAE1A', '#2A9E62', '#5F4AC1', '#AA6D0A']

        self.diffDispFrameList = []
        
        self.isDispTask = False
        self.isDispGoalline = False


        self.drawGraph()


    def drawGraph(self):

        if self.visualizeFrame.diffDispSwitchFlag:
            self.config(height=330)
            self.graph_bg.place(x=0, y=40, width=348, height=330)
        else:
            self.config(height=306)
            self.graph_bg.place(x=0, y=40, width=348, height=306)



        # データ
        categories = self.controller.category_list.categories
        x = []
        for category in categories:
            x.append(category.title)

        tasks = self.controller.task_list.tasks

        y = [0, 0, 0, 0]
        self.isDispTask = False
        self.isDispGoalline = False


        for task in tasks:
            for num in range(len(categories)):
                if task.category.id == num+1 and task.check and task.displayOrder != 9999:
                    y[num] += task.estimatedCost
                    self.isDispTask = True


        if self.isDispTask:


            goallines= self.controller.goalline_list.goallines

            thresholds_list = {}

            for goalline in goallines:
                if goalline.graphDisp:
                    thresholds_list[goalline.id]=goalline.categorySize,goalline.color_id
                    self.isDispGoalline = True

            if self.isDispGoalline:
                self.visualizeFrame.dispDiffDispSwitchButton()
            else:
                self.visualizeFrame.undispDiffDispSwitchButton()


            # グラフ作成（少し横長にするが、Tk上ではサイズに収まる）
            self.fig, self.ax = plt.subplots(figsize=(6, 2.5))
            self.ax.bar(x, y, color=self.colors)


            # 各棒に対応する基準ラインを引く
            for key, (thresholds, color_id) in thresholds_list.items():
                for i, threshold in enumerate(thresholds):
                    self.ax.hlines(y=threshold, xmin=i - 0.44, xmax=i + 0.44, colors=self.line_colors[color_id-1], linestyles='-',linewidth=3)


            # 背景色
            self.fig.patch.set_facecolor('#324A5F')
            self.ax.set_facecolor('#324A5F')

            # タイトルや軸ラベルは非表示
            self.ax.set_title("", color='white', fontsize=14)
            self.ax.set_xlabel("", color='white', fontsize=14)
            self.ax.set_ylabel("", color='white', fontsize=14)

            # スパインを非表示
            for spine in ['top', 'right', 'left', 'bottom']:
                self.ax.spines[spine].set_visible(False)

            # 軸線描画
            self.ax.axhline(y=0, color='white', linewidth=2)
            self.ax.axvline(x=-0.5, color='white', linewidth=1)

            # 目盛り設定（短線消去、色、サイズ）
            self.ax.tick_params(axis='x', colors='white', labelsize=10, length=0)
            self.ax.tick_params(axis='y', colors='white', labelsize=10, length=0)

            # ラベルのフォントと太さ
            for label in self.ax.get_xticklabels():
                label.set_fontname('Noto Sans JP')
                label.set_fontweight('bold')
            for label in self.ax.get_yticklabels():
                label.set_fontname('Noto Sans JP')
                label.set_fontweight('bold')

            # Y軸グリッドを点線で表示（棒の上には描かれないように制限）
            self.ax.set_ylim(0, max(y) + 1.5)  # 棒の上に余白を持たせてグリッドを回避
            self.ax.yaxis.grid(True, linestyle='dotted', color='white', alpha=0.6)

            max_digits = len(str(abs(max(y, key=abs))))
            if max_digits>8:
                max_digits = 4

            # Tkinterに埋め込む
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.draw()
            self.update_idletasks()

            if self.visualizeFrame.diffDispSwitchFlag:
                self.canvas.get_tk_widget().place(x=-48+max_digits*8, y=4, width=str(424-max_digits*8), height="336")
            else:
                self.canvas.get_tk_widget().place(x=-48+max_digits*8, y=-20, width=str(424-max_digits*8), height="336")

        else:
            if not self.isDispGoalline:
                self.visualizeFrame.undispDiffDispSwitchButton()

            tk.Label(self, 
                text="表示する項目がありません", font=("Noto Sans JP", 12), 
                fg="#FFF", bg="#324A5F"
            ).place(x=70, y=148, width=212, height=36)

        self.after(100, self.graph_bg.place_forget)


        if self.isDispTask:

            if self.visualizeFrame.diffDispSwitchFlag:

                diff_dict_list = []
                for goalline in self.controller.goalline_list.goallines:
                    if goalline.graphDisp:
                        diff_list=[]
                        for i, categorySize in enumerate(goalline.categorySize):
                            diff_list.append(y[i] - categorySize)
                        diff_dict_list.append({'color_id': goalline.color_id, 'diff_list': diff_list, 'cost': goalline.cost})

                y_max = max(y)

                    
                value_lists = []
                for i, category in enumerate(categories):
                    value_list = []
                    for diff_dict in diff_dict_list:
                        value_list.append({'color_id': diff_dict["color_id"], 'diff': diff_dict['diff_list'][i], 'cost': diff_dict["cost"]})
                        
                    # 並べ替える
                    value_list = sorted(value_list, key=lambda x: x["cost"], reverse=True)
                    
                    value_lists.append(value_list)
                

                
                for i, value_list in enumerate(value_lists):
                    diffDispFrame = tk.Frame(self, bg="#333C55", pady=4)
                    self.diffDispFrameList.append(diffDispFrame)
                    deno = y_max if y_max!=0 else 1
                    if len(diff_dict_list)==1:
                        y_pos =  274 - 248*(y[i]/deno)
                    elif len(diff_dict_list)==2:
                        y_pos =  254 - 248*(y[i]/deno)
                    else:
                        y_pos =  234 - 248*(y[i]/deno)
                    if y_pos < -12: y_pos = -12
                    diffDispFrame.place(x=72*(i+1)-24, y=y_pos)
                    for value in value_list:
                        diffListFrame = tk.Frame(diffDispFrame, bg="#333C55", height=10)
                        diffListFrame.pack(side="top", anchor="w", padx=2)
                        tk.Frame(diffListFrame, bg=self.line_colors[value["color_id"]-1], width=8, height=3).pack(side="left", padx=4)
                        diff = value["diff"]
                        diff = int(diff) if diff == int(diff) else diff
                        if diff>0:
                            tk.Label(diffListFrame, bg="#333C55", fg="#FF1E00", text=f"+{diff}", font=("Noto Sans", 11), anchor="w").pack(side="left")
                        else:
                            tk.Label(diffListFrame, bg="#333C55", fg="#4284FF", text=diff, font=("Noto Sans", 11)).pack(side="left")


        self.bind("<MouseWheel>", self.visualizeFrame.on_mousewheel_visualize)
        for widget in WidgetFundtions.get_all_descendants(self):
            widget.bind("<MouseWheel>", self.visualizeFrame.on_mousewheel_visualize)



    def updateGraph(self):
        if self.isDispTask:
            if self.ax is not None:
                self.ax.clear()

            for diffDispFrame in self.diffDispFrameList:
                diffDispFrame.destroy()

            self.canvas.get_tk_widget().destroy()
            
        self.drawGraph()




        
class ViewGoallineListFrame():
    def __init__(self, parent, controller, visualizeFrame, mode):
        self.innerFrame = tk.Frame(parent, width=348, bg="#324A5F")
        self.innerFrame.pack(pady=(0, 4))
        self.parent = parent
        self.controller = controller
        self.visualizeFrame = visualizeFrame
        self.mode = mode
        self.goallines = controller.goalline_list.goallines
        self.goalline_functions = GoallineFunctions(self,controller,self.goallines)

        self.setFrame()


    def setFrame(self):
        margin_top_farme = tk.Frame(self.innerFrame, width=348, height=12, bg="#324A5F")
        margin_top_farme.pack(side="top")
        hasCount = 0
        for goalline in self.goallines:
            if (self.mode==1 and goalline.graphDisp) or (self.mode==2 and not goalline.graphDisp):
                hasCount += 1
                wrapFrame = tk.Frame(self.innerFrame, width=348, height=32, bg="#324A5F", cursor="hand2")
                wrapFrame.pack(side="top", pady=4)
                colorLabel = tk.Frame(wrapFrame, bg=self.goalline_functions.colors[goalline.color_id-1]["bg"])
                colorLabel.place(x=16, y=14, width=64, height=4)
                titleLabel = tk.Label(wrapFrame, text=goalline.title, font=("Noto Sans JP", 13), bg="#324A5F", fg="#FFF", justify="left",anchor="w")
                titleLabel.place(x=96, y=4, width=148, height=20)

                if self.mode == 1:
                    propertySum = sum(goalline.categorySize)
                else:
                    propertySum = goalline.cost
                propertySum = int(propertySum) if propertySum == int(propertySum) else propertySum
                tk.Label(wrapFrame, text=f"合計：{propertySum}", font=("Noto Sans JP", 12), bg="#324A5F", fg="#F8F8F8", justify="right",anchor="e").place(x=236, y=5, width=96, height=20)
                wrapFrame.bind("<Button-1>", lambda e, id=goalline.id: self.controller.view.goalline_functions.openEditGoallineWindow(id))
                colorLabel.bind("<Button-1>", lambda e, id=goalline.id: self.controller.view.goalline_functions.openEditGoallineWindow(id))
                titleLabel.bind("<Button-1>", lambda e, id=goalline.id: self.controller.view.goalline_functions.openEditGoallineWindow(id))

     
        if hasCount == 0:
                callHasNotFrame = tk.Frame(self.innerFrame, width=348, height=80, bg="#324A5F")
                callHasNotFrame.pack(side="top")
                if self.mode==1:
                    tk.Label(callHasNotFrame, text="グラフ表示用目安ラインなし", font=("Noto Sans JP", 11), bg="#324A5F", fg="#FFF", justify="center",anchor="center").pack(pady=24)
                else:
                    tk.Label(callHasNotFrame, text="グラフに表示しない用目安ラインなし", font=("Noto Sans JP", 11), bg="#324A5F", fg="#FFF", justify="center",anchor="center").pack(pady=24)
                tk.Frame(self.innerFrame, width=348, height=12, bg="#324A5F").pack(side="top")
        elif hasCount == 1:
            margin_top_farme.config(height=30)
            tk.Frame(self.innerFrame, width=348, height=30, bg="#324A5F").pack(side="top")
        else:
            tk.Frame(self.innerFrame, width=348, height=12, bg="#324A5F").pack(side="top")


        
    def updateFrame(self):
        self.innerFrame.destroy()
        self.innerFrame = tk.Frame(self.parent, width=348, bg="#324A5F")
        if self.mode == 1:
            self.innerFrame.pack(after=self.visualizeFrame.visualizeGoallineFrameTitleFrame)
        else:
            self.innerFrame.pack(after=self.visualizeFrame.visualizeGoallineFrameTitleFrame2)
        self.setFrame()

        self.innerFrame.bind("<MouseWheel>", self.visualizeFrame.on_mousewheel_visualize)
        for widget in WidgetFundtions.get_all_descendants(self.innerFrame):
            widget.bind("<MouseWheel>", self.visualizeFrame.on_mousewheel_visualize)
        self.visualizeFrame.styles.bind_to_all_children(self.visualizeFrame.visualizeCanvas, "<MouseWheel>", self.visualizeFrame.on_mousewheel_visualize)

        
        