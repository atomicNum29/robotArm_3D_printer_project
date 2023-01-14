
import re    # Gcode해석용 정규표현식 모듈.
import pandas    # Gcode 내부 저장 및 데이터프레임 생성용 pandas 모듈.
import tkinter    # GUI tkinter 모듈.
import tkinter.ttk    # GUI 추가 위젯 모듈.
import tkinter.font    # GUI 추가 폰트 모듈.
from tkinter import filedialog    # 파일 가져오기용 모듈.
import numpy as np    # 행렬식 표현 및 행렬연산용 넘파이 모듈.
import matplotlib.pyplot as plt    # 3d 그래프 그리기용 matplot 모듈.
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)    # 3d 그래프 GUI 내부출력용 모듈.
from matplotlib.backend_bases import key_press_handler    # 3d 그래프 GUI 내부 span용 모듈.
from matplotlib.figure import Figure    # matplot 모듈 Figure 생성용 모듈.

# 전역 변수의 선언
infolist = []
gcode_dir = None
gcode_name = None
data = None
X = []
Y = []
Z = []
F = []

# 우측하단 프레임에 정보 알림용 라벨 생성 함수.
def inform(s):
    global infolist
    if not notebook.select() in ['.!frame', '.!frame2']:
        return
    labelFrame = window.children[notebook.select().strip('.')].children['!frame2'].children['!frame']
    for widget in labelFrame.winfo_children():
        widget.destroy()
    infolist.insert(0, s)
    n = 0
    for line in infolist:
        if n < 8:
            information = tkinter.Label(labelFrame, text=line, wraplength=225)
            information.pack(side='bottom', pady=5)
            n += 1
        else: break

# 우측하단 정보 알림용 프레임 비우기 함수.
def clearinfo():
    global infolist
    labelFrame = window.children[notebook.select().strip('.')].children['!frame2'].children['!frame']
    for widget in labelFrame.winfo_children():
        widget.destroy()
    infolist = []

# GCODE 파일의 경로와 이름을 알아낸다.
# X, Y, Z, F 값을 추출하여 튜플 형태로 저장한다.
def openGCODE():
    global gcode_dir, gcode_name
    gcode_dir = filedialog.askopenfile(filetypes=(('gcode files', '*.gcode'), ('all types', '*.*')))
    if gcode_dir is None:
        inform('import cancled')
        return
    gcode_name = re.findall('[a-zA-Z]*[.]gcode', gcode_dir.name)[0].removesuffix('.gcode')
    print(gcode_dir.name)
    print(gcode_name)
    
    with open(gcode_dir.name, 'r') as gcode:
        loadlines = list(map(str.strip, gcode.readlines()))

    filtlist = []

    for line in loadlines:
        if line.startswith('G1'):
            filtlist.append(line)

    #1) 초기값 설정. X, Y, Z, F 각 정보는 각각의 리스트로 저장됨.
    XHomepos, YHomepos, ZHomepos, Ffirstval = '0', '0', '0', '1000'
    global X, Y, Z, F
    X = [0]
    Y = [0]
    Z = [0]
    F =[100]
    x0 = XHomepos
    y0 = YHomepos
    z0 = ZHomepos
    f0 = Ffirstval
    #2) 정규표현식을 활용하여 X, Y, Z, E, F에 후행하는 임의의 숫자 패턴 생성.
    x_coordinate = re.compile('[X]\d*[.]?\d*')
    y_coordinate = re.compile('[Y]\d*[.]?\d*')
    z_coordinate = re.compile('[Z]\d*[.]?\d*')
    e_distance = re.compile('[E]-?\d*[.]?\d*')
    f_val = re.compile('[F]\d*[.]?\d*')
    #3) 각 문장에 X, Y, Z, E, F 정보가 존재한다면 해당 정보를 리스트에 담고,
    #   그렇지 않다면 이전 문장에 존재했던 해당 정보를 리스트에 담는다.
    #   단, E와 F에 대한 정보만 존재한다면 그 문장은 의미없는 문장이므로 건너뛴다.
    for line in filtlist:
        x1 = str(x_coordinate.findall(line)).strip("X[]'")
        y1 = str(y_coordinate.findall(line)).strip("Y[]'")
        z1 = str(z_coordinate.findall(line)).strip("Z[]'")
        e = str(e_distance.findall(line)).strip("E[]'")
        f1 = str(f_val.findall(line)).strip("F[]'")
        if not x1 and not y1 and not z1 and e and f1:
            continue
        if x1: X.append(float(x1)); x0 = x1
        else: X.append(float(x0))
        if y1: Y.append(float(y1)); y0 = y1
        else: Y.append(float(y0))
        if z1: Z.append(float(z1)); z0 = z1
        else: Z.append(float(z0))
        if f1: F.append(float(f1)); f0 = f1
        else: F.append(float(f0))
    # X=tuple(X)
    # Y=tuple(Y)
    # Z=tuple(Z)
    # F=tuple(F)
    inform(f'import {gcode_dir.name} done')

# 필터링된 Gcode를 텍스트로 저장한 뒤 GUI에 띄우는 함수.
def openfilteredtxt():
    global data
    if data is None:
        inform('open gcode file before filtering')
        return
    data = pandas.DataFrame({'Xi':X, 'Yi':Y, 'Zi':Z}, columns=['Xi','Yi','Zi','','J1','J2','J3','J4','J5','J6','J7','','Xf','Yf','Zf'])
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    txt_edit = tkinter.Text(frame1L)
    txt_edit.place(x=0,y=0, width=797, height=498)
    for i in data.index:
        valx = data.iloc[i, 0]
        valy = data.iloc[i, 1]
        valz = data.iloc[i, 2]
        txt_edit.insert(tkinter.END, f' G1  X{valx}  Y{valy}  Z{valz}\n')
    inform('filtered gcode opened.')

# 필터링된 Gcode를 매트랩 경로에 저장하는 함수.
def exportfilteredgcode():
    global gcode_dir, data
    if gcode_dir is None or data is None:
        inform('open gcode and filtering before export')
        return
    # gcode 디렉토리에 gcode파일명_coord.xlsx 파일로 저장함.
    xlsx_dir = f'{gcode_dir.name.removesuffix(".gcode")}_coord.xlsx'
    data.to_excel(xlsx_dir, sheet_name='XYZ coordinates')
    inform(f'filtered gcode successfully saved to {xlsx_dir}.')

# 생성된 X,Y,Z가 정상인지 확인하기 위해 numpy에서 3차원 plot으로 시각화해서 확인함.
def drawgraph():
    global X, Y, Z, F
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    # 1) 그래프 생성.
    fig = Figure(figsize=(10,10), dpi=500)
    ax = fig.add_subplot(projection='3d')
    ax.plot(X, Y, Z, linewidth=0.1, alpha = 0.8)
    # ax.set_xlim(40,80)
    # ax.set_ylim(40,80)
    # ax.set_zlim(-1,39)
    ax.set_aspect('equal')
    # 2) GUI에 canvas로 그림.
    canvas = FigureCanvasTkAgg(fig, master=frame1L)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, frame1L, pack_toolbar=False)
    toolbar.update()
    toolbar.place(x=0, y=476, width=800, height=25)
    canvas.get_tk_widget().place(x=0,y=0, width=800, height=476)
    inform('plot drawing done')

# GUI내에서 다른 탭으로 이동시 호출되는 함수.
def tabchange(event):
    tab_id = notebook.select()
    print(tab_id)
    inform('tab changed')
    notebook.select(tab_id)

# 1번 탭으로 이동했을 때 1번 탭 리프레쉬.
def tab1refresh():

    frame1L=tkinter.Frame(frame1, relief="groove", bd=2)
    frame1L.place(x=0,y=0, width=800, height=552)

    buttonL1 = tkinter.Button(frame1L, text="Plot", relief="solid", command=drawgraph)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame1L, text="Edit Gcode", relief="solid", command=None)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame1L, text="Save as.. ", relief="solid", command=None)
    buttonL3.place(x=205, y=499, width=90, height=41)

    frame1R = tkinter.Frame(frame1, relief="groove", bd=2)
    frame1R.place(x=800,y=0, width=258, height=552)
    frameR_t = tkinter.Frame(frame1R, relief='groove', bd=2)
    frameR_t.place(x=12, y=270, width=230, height=270)
    
    buttonR1 = tkinter.Button(frame1R, text="Import Gcode", relief="solid", command=openGCODE)
    buttonR1.place(x=12, y=30, width=230, height=30)
    buttonR2 = tkinter.Button(frame1R, text="Check Gcode", relief="solid", command=None)
    buttonR2.place(x=12, y=75, width=230, height=30)
    buttonR3 = tkinter.Button(frame1R, text="See Filtered gcode", relief="solid", command=openfilteredtxt)
    buttonR3.place(x=12, y=120, width=230, height=30)
    buttonR4 = tkinter.Button(frame1R, text="Export", relief="solid", command=exportfilteredgcode)
    buttonR4.place(x=12, y=165, width=230, height=30)
    clearbtn = tkinter.Button(frame1R, text="clear", relief="solid", command=clearinfo)
    clearbtn.place(x=195, y=244, width=48, height=25)

# 2번 탭으로 이동했을 때 2번 탭 리프레쉬.
def tab2refresh():

    frame2L = tkinter.Frame(frame2, relief="groove", bd=2, width=500)
    frame2L.place(x=0,y=0, width=800, height=552)

    buttonL1 = tkinter.Button(frame2L, text="Plot FK", relief="solid", command=None)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame2L, text="Edit Angles", relief="solid", command=None)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame2L, text="Edit Done", relief="solid", command=None)
    buttonL3.place(x=205, y=499, width=90, height=41)

    frame2R = tkinter.Frame(frame2, relief='groove', bd=2)
    frame2R.place(x=800,y=0, width=258, height=552)
    frameR_t = tkinter.Frame(frame2R, relief='groove', bd=2)
    frameR_t.place(x=12, y=270, width=230, height=270)

    buttonR1 = tkinter.Button(frame2R, text="Import xlsx", relief="solid", command=None)
    buttonR1.place(x=12, y=30, width=230, height=30)
    buttonR2 = tkinter.Button(frame2R, text="Check Angles", relief="solid", command=None)
    buttonR2.place(x=12, y=75, width=230, height=30)
    buttonR3 = tkinter.Button(frame2R, text="See Angles", relief="solid", command=None)
    buttonR3.place(x=12, y=120, width=230, height=30)
    buttonR4 = tkinter.Button(frame2R, text="Export", relief="solid", command=None)
    buttonR4.place(x=12, y=165, width=230, height=30)
    clearbtn = tkinter.Button(frame2R, text="clear", relief="solid", command=clearinfo)
    clearbtn.place(x=195, y=244, width=48, height=25)

# 3번 탭으로 이동했을 때 3번 탭 리프레쉬.
def tab3refresh():

    frame3_1 = tkinter.Frame(frame3, relief='groove', bd=5)
    frame3_1.place(x=310, y=185, width=450, height=140)

    fontstyle1 = tkinter.font.Font(size=17)
    fontstyle2 = tkinter.font.Font(size=20)
    surelabel=tkinter.Label(frame3_1, anchor='w', pady=0, text="  Are you sure you want to exit?", bg='#9c9c9c', font=fontstyle1)
    surelabel.place(x=0, y=0, width=440, height=23)
    lostlabel=tkinter.Label(frame3_1, anchor='n', pady=10, text="All unsaved changes will be lost", bg='#d4d4d4', font=fontstyle2)
    lostlabel.place(x=0, y=23, width=440, height=50)
    lostlabel=tkinter.Label(frame3_1, anchor='n', bg='#f0f0f0')
    lostlabel.place(x=0, y=73, width=440, height=57)

    yesbutton = tkinter.Button(frame3_1, command=window.destroy, text='YES', width=15, font=fontstyle1)
    yesbutton.place(x=70, y=90, width=125, height=33)
    nobutton = tkinter.Button(frame3_1, command=frame3_1.destroy, text='NO', width=15, font=fontstyle1)
    nobutton.place(x=250, y=90, width=125, height=33)


# GUI 생성 및 기본 창 설정.
window = tkinter.Tk()
window.title('Gcode Interpreter v1')
window.geometry('1112x616+150+85')
window.resizable(False, False)
notebook=tkinter.ttk.Notebook(window, width=1112, height=616)
notebook.pack()
frame1=tkinter.Frame(window)
notebook.add(frame1, text="  pre-process  ")
frame2=tkinter.Frame(window)
notebook.add(frame2, text=" after-process ")
frame3 = tkinter.Frame(window)
notebook.add(frame3, text="     exit     ")

tab1refresh()
tab2refresh()
tab3refresh()

# 노트북 바인딩 및 GUI 메인루프 실행.
notebook.bind('<<NotebookTabChanged>>',tabchange)

window.mainloop()