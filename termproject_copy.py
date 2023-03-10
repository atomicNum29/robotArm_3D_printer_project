
import re    # Gcode해석용 정규표현식 모듈.
import pandas    # Gcode 내부 저장 및 데이터프레임 생성용 pandas 모듈.
import tkinter    # GUI tkinter 모듈.
import tkinter.ttk    # GUI 추가 위젯 모듈.
import tkinter.font    # GUI 추가 폰트 모듈.
from tkinter import filedialog    # 파일 가져오기용 모듈.
import numpy as np    # 행렬식 표현 및 행렬연산용 넘파이 모듈.
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt    # 3d 그래프 그리기용 matplot 모듈.
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)    # 3d 그래프 GUI 내부출력용 모듈.
from matplotlib.backend_bases import key_press_handler    # 3d 그래프 GUI 내부 span용 모듈.
# from matplotlib.figure import Figure    # matplot 모듈 Figure 생성용 모듈.
# ikpy
from ikpy.chain import Chain
import ikpy.utils.plot as plot_utils

# 전역 변수의 선언
infolist = []
gcode_dir = None
gcode_name = None
data = None
X = []
Y = []
Z = []
F = []
X2 = [0]
Y2 = [0]
Z2 = [0]
layer = []
urdf_dir = None
my_chain = None

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

    # G1으로 시작하는 문자열만 잘라넣기 위한 리스트
    filtlist = []
    # G1으로 시작하는 문장만 저장한다.
    for line in loadlines:
        if line.startswith('G1'):
            filtlist.append(line)

    #1) 초기값 설정. X, Y, Z, F 각 정보는 각각의 리스트로 저장됨.
    XHomepos, YHomepos, ZHomepos, Ffirstval = '0', '0', '0', '1000'
    global X, Y, Z, F, data
    global X2, Y2, Z2
    X = [0]
    Y = [0]
    Z = [0]
    F =[100]
    x0 = XHomepos
    y0 = YHomepos
    z0 = ZHomepos
    f0 = Ffirstval
    #2) 정규표현식을 활용하여 X, Y, Z, E, F에 후행하는 임의의 숫자 패턴 생성.
    x_coordinate = re.compile('(?<=X)[-+]?\d*[.]?\d*')
    y_coordinate = re.compile('(?<=Y)[-+]?\d*[.]?\d*')
    z_coordinate = re.compile('(?<=Z)[-+]?\d*[.]?\d*')
    e_distance = re.compile('(?<=E)[-+]?\d*[.]?\d*')
    f_val = re.compile('(?<=F)[-+]?\d*[.]?\d*')
    #3) 각 문장에 X, Y, Z, E, F 정보가 존재한다면 해당 정보를 리스트에 담고,
    #   그렇지 않다면 이전 문장에 존재했던 해당 정보를 리스트에 담는다.
    #   단, E와 F에 대한 정보만 존재한다면 그 문장은 의미없는 문장이므로 건너뛴다.
    for line in filtlist:
        x1 = x_coordinate.findall(line)
        y1 = y_coordinate.findall(line)
        z1 = z_coordinate.findall(line)
        e = e_distance.findall(line)
        f1 = f_val.findall(line)
        # x1, y1, z1 모두 정보가 없으면 건너뜀.
        if not( len(x1) or len(y1) or len(z1) ):
            continue
        if len(x1): X.append(float(x1[0])); x0 = x1[0]
        else: X.append(float(x0))
        if len(y1): Y.append(float(y1[0])); y0 = y1[0]
        else: Y.append(float(y0))
        if len(z1): Z.append(float(z1[0])); z0 = z1[0]
        else: Z.append(float(z0))
        if len(f1): F.append(float(f1[0])); f0 = f1[0]
        else: F.append(float(f0))
    X=tuple(X)
    Y=tuple(Y)
    Z=tuple(Z)
    F=tuple(F)
    for i in range(len(X)):
        X2.append(X[i] / 1000)
        Y2.append(Y[i] / 1000)
        Z2.append(Z[i] / 1000)
    X2 = tuple(X2)
    Y2 = tuple(Y2)
    Z2 = tuple(Z2)
    data = pandas.DataFrame({'Xi':X, 'Yi':Y, 'Zi':Z}, columns=['Xi','Yi','Zi','','J1','J2','J3','J4','J5','J6','J7','','Xf','Yf','Zf'])
    inform(f'import {gcode_dir.name} done')

# URDF 파일의 경로와 이름을 알아낸다.
def openURDF():
    global my_chain, urdf_dir
    urdf_dir = filedialog.askopenfile(filetypes=(('URDF files', '*.URDF'), ('all types', '*.*')))
    if urdf_dir is None:
        inform('open cancled')
        return
    my_chain = Chain.from_urdf_file(urdf_dir.name)
    inform(f'imported URDF from {urdf_dir.name}')

# 불러온 로봇팔을 그려서 보여준다.
def plot_chain():
    global my_chain
    if my_chain is None:
        inform('null arm error')
        return
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    fig, ax = plot_utils.init_3d_figure()
    my_chain.plot([0]*len(my_chain.links), ax)
    canvas = FigureCanvasTkAgg(fig, master=frame1L)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, frame1L, pack_toolbar=False)
    toolbar.update()
    toolbar.place(x=0, y=476, width=800, height=25)
    canvas.get_tk_widget().place(x=0,y=0, width=800, height=476)
    inform('chain plot done')

# "한 점"에 대한 로봇팔의 IK 연산 결과를 보자.
def plot_IK():
    global X, Y, Z
    global X2, Y2, Z2
    global my_chain
    if my_chain is None:
        inform("don't have arm")
        return
    if type(X2) is not tuple:
        inform("don't have GCODE data")
    # 죄측 plot figure 배치 frame 추출 및 기타 widget destroy
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    
    # 1) 그래프 생성.
    # fig = plt.figure(figsize=(10,10), dpi=500)
    # ax = fig.add_subplot(111, projection='3d')
    fig, ax = plot_utils.init_3d_figure()
    # 어느 좌표에 대해 그릴 지 입력받을 슬라이더를 만들고
    fig.subplots_adjust(bottom=0.2)
    axSlider = fig.add_axes([0.2, 0.1, 0.65, 0.03])
    initalVal = len(X2)//2
    point_slider = Slider(
        ax=axSlider,
        label='point',
        valmin=0,
        valmax=len(X2),
        valinit=initalVal,
        valstep=1,
        dragging=True
    )
    # 그 좌표에 대해 엔드 이펙터의 방향까지 고려해 계산한 결과를
    # 로봇팔과 함께 그려주는 코드를 작성하였다.
    def update(val):
        ax.clear()
        target_position = [ X2[val], Y2[val], Z2[val]]
        stateofArm = my_chain.inverse_kinematics(target_position, target_orientation, orientation_axis)
        my_chain.plot(stateofArm, ax, target_position)
        ax.set_xlim(-0.1, 0.1)
        ax.set_ylim(-0.1, 0.1)
        ax.set_zlim(-0.1, 0.1)
    point_slider.on_changed(update)
    target_position = [ X2[initalVal], Y2[initalVal], Z2[initalVal]]
    target_orientation = [0, 0, -1]
    orientation_axis = "Z"
    stateofArm = my_chain.inverse_kinematics(target_position, target_orientation, orientation_axis)
    my_chain.plot(stateofArm, ax, target_position)
    ax.set_xlim(-0.1, 0.1)
    ax.set_ylim(-0.1, 0.1)
    ax.set_zlim(-0.1, 0.1)
    # 2) GUI에 canvas로 그림.
    canvas = FigureCanvasTkAgg(fig, master=frame1L)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, frame1L, pack_toolbar=False)
    toolbar.update()
    toolbar.place(x=0, y=476, width=800, height=25)
    canvas.get_tk_widget().place(x=0,y=0, width=800, height=476)
    inform('plot drawing done')

# 필터링된 Gcode를 텍스트로 저장한 뒤 GUI에 띄우는 함수.
def openfilteredtxt():
    global data
    if data is None:
        inform('import gcode before filtering')
        return
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    txt_edit = tkinter.Text(frame1L)
    txt_edit.place(x=0,y=0, width=797, height=497)
    for i in data.index:
        valx = data.iloc[i, 0]
        valy = data.iloc[i, 1]
        valz = data.iloc[i, 2]
        txt_edit.insert(tkinter.END, f' G1  X{valx}  Y{valy}  Z{valz}\n')
    inform('filtered gcode opened.')

# 생성된 X,Y,Z가 정상인지 확인하기 위해 numpy에서 3차원 plot으로 시각화해서 확인함.
def drawgraph():
    global X, Y, Z, F
    global X2, Y2, Z2
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    # 1) 그래프 생성.
    fig = plt.figure(figsize=(10,10), dpi=500)
    ax = fig.add_subplot(projection='3d')
    ax.plot(X2, Y2, Z2, linewidth=0.1, alpha = 0.8)
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

# Gcode 텍스트로 열고 수정하는 함수.
def opentxt():
    global gcode_dir, gcode_name
    if gcode_dir is None:
        inform('import gcode plz')
        return
    frame1L = window.children['!frame'].children['!frame']
    widgetList = frame1L.winfo_children()
    for widget in widgetList:
        if not widget.winfo_name().startswith('!button'):
            widget.destroy()
    txt_edit = tkinter.Text(frame1L)
    txt_edit.place(x=0,y=0, width=797, height=497)
    with open(gcode_dir.name, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tkinter.END, text)
    inform(f'gcode opened. you can edit {gcode_name}. please save after editing.')

# 수정한 Gcode를 텍스트로 저장하는 함수.
def savetxt():
    global gcode_dir
    if gcode_dir is None:
        inform('no have gcode directory')
        return
    frame1L = window.children['!frame'].children['!frame']
    if not '!text' in frame1L.children.keys():
        inform('no changed gcode')
        return
    txt_edit = frame1L.children['!text']
    with open(gcode_dir.name, "w") as output_file:
        text = txt_edit.get(1.0, tkinter.END)
        output_file.write(text)
    inform('file saved')

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
    buttonL2 = tkinter.Button(frame1L, text="Edit Gcode", relief="solid", command=opentxt)
    buttonL2.place(x=110, y=499, width=90, height=41)
    buttonL3 = tkinter.Button(frame1L, text="Save", relief="solid", command=savetxt)
    buttonL3.place(x=205, y=499, width=90, height=41)
    buttonL4 = tkinter.Button(frame1L, text="plot arm", relief="solid", command=plot_chain)
    buttonL4.place(x=300, y=499, width=90, height=41)
    buttonL5 = tkinter.Button(frame1L, text="plot IK", relief="solid", command=plot_IK)
    buttonL5.place(x=395, y=499, width=90, height=41)

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
    buttonR4 = tkinter.Button(frame1R, text="Import URDF", relief="solid", command=openURDF)
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