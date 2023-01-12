
########################################################################################
#  사용 모듈 불러오기                                                                       #
########################################################################################

import re    # Gcode해석용 정규표현식 모듈.
import pandas    # Gcode 내부 저장 및 데이터프레임 생성용 pandas 모듈.
import xlrd    # 엑셀을 데이터프레임으로 불러오기 위한 xlrd 모듈.
import openpyxl    # 데이터프레임 엑셀로 내보내기용 openpyxl모듈.
import numpy as np    # 행렬식 표현 및 행렬연산용 넘파이 모듈.
import matplotlib.pyplot as plt    # 3d 그래프 그리기용 matplot 모듈.
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)    # 3d 그래프 GUI 내부출력용 모듈.
from matplotlib.backend_bases import key_press_handler    # 3d 그래프 GUI 내부 span용 모듈.
from matplotlib.figure import Figure    # matplot 모듈 Figure 생성용 모듈.
import tkinter    # GUI tkinter 모듈.
import tkinter.ttk    # GUI 추가 위젯 모듈.
import tkinter.font    # GUI 추가 폰트 모듈.
from tkinter.filedialog import askopenfilename, asksaveasfilename    # GUI에서 텍스트 편집하기용 모듈.
from tkinter import filedialog    # 파일 가져오기용 모듈.

########################################################################################
#  Gcode 해석 관련 함수 정의                                                            #
########################################################################################

matlab_directory = 'D:/python_VSCode/data_files/'

# 지정된 경로의 gcode 파일 불러옴. gcode 이름을 변수에 저장함.
def opengcode():
    global gcode_file_path, file_name
    gcode_file_path = gcode_directory
    file_name = str(re.findall('[a-zA-Z]*[.]gcode',gcode_file_path)).strip("[]'").removesuffix('.gcode')

# 불러온 파일을 열고, 리스트 형식으로 불러온 다음, 끝부분에 입력된 \n 문자를 없애 리스트로 저장.
def gcode2list():
    global loadlines
    with open(gcode_file_path, 'r') as gcode:
        loadlines_with_enter = gcode.readlines()
    
    loadlines = list(map(lambda s: s.strip(), loadlines_with_enter))

# 'G1'으로 시작하는 문장들만 리스트에 저장되게 필터링함.
def filtlist():
    global filtlines
    filtlines = []
    for line in loadlines:
        if line.startswith('G1'):
            filtlines += [line]

# filtlines를 토대로 한 X, Y, Z, F 정보를 갖고 있는 리스트 생성.
def getcoords():
    #1) 초기값 설정. X, Y, Z, F 각 정보는 각각의 리스트로 저장됨.
    global X, Y, Z, F
    XHomepos, YHomepos, ZHomepos, Ffirstval = '0', '0', '0', '1000'
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
    for line in filtlines:
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
    X=tuple(X)
    Y=tuple(Y)
    Z=tuple(Z)
    F=tuple(F)

# 엑셀 파일명을 생성하기 위해 현재시간을 불러옴.
def gettime():
    global current_time
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime('%m.%d %H.%M')

# X, Y, Z 값들을 데이터프레임 형식으로 저장한 뒤 엑셀 파일로 내보낸다.
def gcode2data():
    global data
    data = pandas.DataFrame({'Xi':X, 'Yi':Y, 'Zi':Z}, columns=['Xi','Yi','Zi','','J1','J2','J3','J4','J5','J6','J7','','Xf','Yf','Zf'])

########################################################################################
# GUI 관련 함수 정의                                                                      #
########################################################################################

########################################################################################
# 탭1 관련                                                                               #
########################################################################################

# 생성된 X,Y,Z가 정상인지 확인하기 위해 numpy에서 3차원 plot으로 시각화해서 확인함.
def drawgraph():
    for widget in frame1L.winfo_children():
        if str(widget) not in button_list:
            widget.destroy()
    opengcode()
    gcode2list()
    filtlist()
    getcoords()
    # 1) 그래프 생성.
    fig = Figure(figsize=(10,10), dpi=500)
    ax = fig.add_subplot(projection='3d')
    line, = ax.plot(X, Y, Z, linewidth=0.1, alpha = 0.8)
    ax.set_xlim(40,80)
    ax.set_ylim(40,80)
    ax.set_zlim(-1,39)
    ax.set_aspect('equal')
    # 2) GUI에 canvas로 그림.
    canvas = FigureCanvasTkAgg(fig, master=frame1L)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, frame1L, pack_toolbar=False)
    toolbar.update()
    toolbar.place(x=0, y=476, width=800, height=25)
    canvas.get_tk_widget().place(x=0,y=0, width=800, height=476)
    inform('plot drawing done')

# Gcode 파일 가져오는 함수.
def get_gcodedir():
    global gcode_directory
    gcodedir = filedialog.askopenfile(initialdir='/Users/kyprus77/Desktop', filetypes=(('gcode files', '*.gcode'), ('all types', '*.*')))
    inform(f'imported success : file path = {gcodedir.name}')
    gcode_directory = gcodedir.name
    opengcode()

# Gcode 텍스트로 열고 수정하는 함수.
def opentxt():
    global txt_edit
    txt_edit = tkinter.Text(frame1L)
    txt_edit.place(x=0,y=0, width=797, height=549)
    with open(gcode_file_path, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tkinter.END, text)
    buttonL1 = tkinter.Button(frame1L, text="Plot", relief="solid", command=drawgraph)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame1L, text="Edit Gcode", relief="solid", command=opentxt)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame1L, text="Save as.. ", relief="solid", command=savetxt)
    buttonL3.place(x=205, y=499, width=90, height=41)
    inform(f'gcode opened. you can edit {file_name}. please save after editing.')
    
# 수정한 Gcode를 텍스트로 저장하는 함수.
def savetxt():
    with open(gcode_file_path, "w") as output_file:
        text = txt_edit.get(1.0, tkinter.END)
        output_file.write(text)
    inform('file saved')
    
# 필터링된 Gcode를 텍스트로 저장한 뒤 GUI에 띄우는 함수.
def openfilteredtxt():
    global txt_edit
    txt_edit = tkinter.Text(frame1L)
    txt_edit.place(x=0,y=0, width=797, height=549)
    opengcode()
    gcode2list()
    filtlist()
    getcoords()
    gcode2data()
    for i in data.index:
        valx = data.iloc[i, 0]
        valy = data.iloc[i, 1]
        valz = data.iloc[i, 2]
        txt_edit.insert(tkinter.END, f' G1  X{valx}  Y{valy}  Z{valz}\n')
    buttonL1 = tkinter.Button(frame1L, text="Plot", relief="solid", command=drawgraph)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame1L, text="Edit Gcode", relief="solid", command=opentxt)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame1L, text="Save as.. ", relief="solid", command=savetxt)
    buttonL3.place(x=205, y=499, width=90, height=41)
    inform('filtered gcode opened.')

# 필터링된 Gcode를 매트랩 경로에 저장하는 함수.
def exportfilteredgcode():
    opengcode()
    gcode2list()
    filtlist()
    getcoords()
    gcode2data()
    data.to_excel(f'{matlab_directory}{file_name}-coord.xlsx', sheet_name='XYZ coordinates')
    inform(f'filtered gcode successfully saved to {matlab_directory}.')

# Gcode에 문제가 있는지 확인하는 함수.
def checkgcode():
    inform(f'{file_name}.gcode has {0} problems.')

########################################################################################
# 탭2 관련                                                                               #
########################################################################################

# 순기구학 연산을 통해 역기구학 연산이 잘 수행되었는지 플롯으로 확인.
def drawFK():
    drawgraph()

# 매트랩을 통해 구한 각도 파일을 엶.
def openangles():
    global txt_edit, Angles
    txt_edit = tkinter.Text(frame2L)
    txt_edit.place(x=0,y=0, width=797, height=549)
    for i in Angles.index:
        valx = Angles.iloc[i, 5]
        valy = Angles.iloc[i, 6]
        valz = Angles.iloc[i, 7]
        vala = Angles.iloc[i, 8]
        valb = Angles.iloc[i, 9]
        valc = Angles.iloc[i, 10]
        vald = Angles.iloc[i, 11]
        txt_edit.insert(tkinter.END, f'G1  X{valx}  Y{valy}  Z{valz}  A{vala}  B{valb}  C{valc}  D{vald}\n')
    buttonL1 = tkinter.Button(frame2L, text="Plot FK", relief="solid", command=drawFK)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame2L, text="Edit Angles", relief="solid", command=openangles)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame2L, text="Edit Done", relief="solid", command=saveangles)
    buttonL3.place(x=205, y=499, width=90, height=41)
    inform('Angle file opened.')

# 수정한 각도 파일을 xlxs 형식으로 저장하는 함수.
def saveangles():
    return

# 탭1과 2는 같은 엑셀 파일을 공유하므로 이미 각도관련 엑셀 파일의 경로를 알고 있음.
def get_angledir():
    inform(f'{matlab_directory}{file_name}-coord.xlsx')

# 매트랩으로 구한 각 값들에 문제가 있는지 확인하는 함수.
def checkangles():
    inform(f'{file_name} Angle file has {0} problems.')

# Matlab에서 연산해 저장한 엑셀 파일을 다시 불러와 데이터프레임으로 저장.
def readangles():
    global excel_file_path, Angles
    excel_file_path = f'{matlab_directory}{file_name}-coord.xlsx'
    Angles = pandas.read_excel('/Users/kyprus77/MATLAB-Drive/cube-coord.xlsx')
    inform(f'{file_name} opened successfully.')

# 역기구학으로 구한 파일을 따로 xlxs 파일 형식으로 저장.
def exportangles():
    angledir = filedialog.asksaveasfile(initialdir='{matlab_directory}{file_name}-coord', filetypes=(('Microsoft excel files', '*.xlxs'), ('all types', '*.*')))
    Angles.to_excel(f'{matlab_directory}{file_name}-coord', sheet_name='XYZ coordinates')
    inform(f'{file_name} saved successfully.')

########################################################################################
# 탭3 관련, etc                                                                          #
########################################################################################

# 우측하단 프레임에 정보 알림용 라벨 생성 함수.
def inform(s):
    global infolist
    for widget in frameR_t.winfo_children():
        widget.destroy()
    infolist.insert(0, s)
    n = 1
    for line in infolist:
        if n < 15:
            information = tkinter.Label(frameR_t, text=line, wraplength=225)
            information.pack(side='bottom', pady=5)
            n += 1
        else: pass

# 우측하단 정보 알림용 프레임 비우기 함수.
def clearinfo():
    global infolist
    for widget in frameR_t.winfo_children():
        widget.destroy()
    infolist = []
    
# GUI내에서 다른 탭으로 이동시 호출되는 함수.
def tabchange(*args):
    global t_nos
    t_nos=str(notebook.index(notebook.select()))
    checktab(int(t_nos))

# 몇번 탭으로 이동했는지 알아보는 함수.
def checktab(n):
    if n==0: tab1refresh()
    elif n==1: tab2refresh()
    else: tab3refresh()

# 1번 탭으로 이동했을 때 1번 탭 리프레쉬.
def tab1refresh():
    global frame1L, frame1R, frameR_t
    frame1L.destroy()
    frame1R.destroy()

    frame1L=tkinter.Frame(frame1, relief="groove", bd=2)
    frame1L.place(x=0,y=0, width=800, height=552)


    buttonL1 = tkinter.Button(frame1L, text="Plot", relief="solid", command=drawgraph)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame1L, text="Edit Gcode", relief="solid", command=opentxt)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame1L, text="Save as.. ", relief="solid", command=savetxt)
    buttonL3.place(x=205, y=499, width=90, height=41)


    frame1R = tkinter.Frame(frame1, relief="groove", bd=2)
    frame1R.place(x=800,y=0, width=258, height=552)
    frameR_t = tkinter.Frame(frame1R, relief='groove', bd=2)
    frameR_t.place(x=12, y=270, width=230, height=270)
    inform('tab swapped')

    buttonR1 = tkinter.Button(frame1R, text="Import Gcode", relief="solid", command=get_gcodedir)
    buttonR1.place(x=12, y=30, width=230, height=30)
    buttonR2 = tkinter.Button(frame1R, text="Check Gcode", relief="solid", command=checkgcode)
    buttonR2.place(x=12, y=75, width=230, height=30)
    buttonR3 = tkinter.Button(frame1R, text="See Filtered gcode", relief="solid", command=openfilteredtxt)
    buttonR3.place(x=12, y=120, width=230, height=30)
    buttonR3 = tkinter.Button(frame1R, text="Export", relief="solid", command=exportfilteredgcode)
    buttonR3.place(x=12, y=165, width=230, height=30)
    clearbtn = tkinter.Button(frame1R, text="clear", relief="solid", command=clearinfo)
    clearbtn.place(x=195, y=244, width=48, height=25)

# 2번 탭으로 이동했을 때 2번 탭 리프레쉬.
def tab2refresh():
    global frame2L, frame2R, frameR_t
    frame2L.destroy
    frame2R.destroy

    frame2L = tkinter.Frame(frame2, relief="groove", bd=2, width=500)
    frame2L.place(x=0,y=0, width=800, height=552)

    buttonL1 = tkinter.Button(frame2L, text="Plot FK", relief="solid", command=drawFK)
    buttonL1.place(x=15, y=499, width=90, height=41)
    buttonL2 = tkinter.Button(frame2L, text="Edit Angles", relief="solid", command=openangles)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame2L, text="Edit Done", relief="solid", command=saveangles)
    buttonL3.place(x=205, y=499, width=90, height=41)

    frame2R = tkinter.Frame(frame2, relief='groove', bd=2)
    frame2R.place(x=800,y=0, width=258, height=552)
    frameR_t = tkinter.Frame(frame2R, relief='groove', bd=2)
    frameR_t.place(x=12, y=270, width=230, height=270)
    inform('tab swapped')

    buttonR1 = tkinter.Button(frame2R, text="Import xlsx", relief="solid", command=get_angledir)
    buttonR1.place(x=12, y=30, width=230, height=30)
    buttonR2 = tkinter.Button(frame2R, text="Check Angles", relief="solid", command=checkangles)
    buttonR2.place(x=12, y=75, width=230, height=30)
    buttonR3 = tkinter.Button(frame2R, text="See Angles", relief="solid", command=readangles)
    buttonR3.place(x=12, y=120, width=230, height=30)
    buttonR3 = tkinter.Button(frame2R, text="Export", relief="solid", command=exportangles)
    buttonR3.place(x=12, y=165, width=230, height=30)
    clearbtn = tkinter.Button(frame2R, text="clear", relief="solid", command=clearinfo)
    clearbtn.place(x=195, y=244, width=48, height=25)

# 3번 탭으로 이동했을 때 3번 탭 리프레쉬.
def tab3refresh():
    global frame3_1
    frame3_1.destroy

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

########################################################################################
#  코드 시작                                                                             #
########################################################################################

# GUI 생성 및 기본 창 설정.
window = tkinter.Tk()
window.title('Gcode Interpreter v1')
window.geometry('1112x616+150+85')
window.resizable(False, False)
notebook=tkinter.ttk.Notebook(window, width=1112, height=616)
notebook.pack()
frame1=tkinter.Frame(window)
notebook.add(frame1, text=" pre-process ")
frame2=tkinter.Frame(window)
notebook.add(frame2, text=" after-process ")
frame3 = tkinter.Frame(window)
notebook.add(frame3, text='     exit     ')
frame1L=tkinter.Frame()
frame1R=tkinter.Frame()
frame2L=tkinter.Frame()
frame2R=tkinter.Frame()
frame2R_t=tkinter.Frame()
frame3_1=tkinter.Frame()
frameR_t=tkinter.Frame()

infolist = []
button_list = ['.!frame.!frame.!button', '.!frame.!frame.!button2', '.!frame.!frame.!button3']

# 노트북 바인딩 및 GUI 메인루프 실행.
notebook.bind('<<NotebookTabChanged>>',tabchange)
window.mainloop()
########################################################################################
#  코드 종료                                                                             #
########################################################################################
