
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

gcode_dir = "data_files/cube.gcode"
urdf_dir = "D:/robotArm_3D_printer_project/data_files/poppy_ergo.URDF"


# 1번 탭으로 이동했을 때 1번 탭 리프레쉬.
def tab1refresh():

    frame1L=tkinter.Frame(frame1, relief="groove", bd=2)
    frame1L.place(x=0,y=0, width=800, height=552)


    frame1R = tkinter.Frame(frame1, relief="groove", bd=2)
    frame1R.place(x=800,y=0, width=258, height=552)
    frameR_t = tkinter.Frame(frame1R, relief='groove', bd=2)
    frameR_t.place(x=12, y=270, width=230, height=270)



# GCODE 읽기
with open(gcode_dir, 'r') as gcode:
    loadlines = list(map(str.strip, gcode.readlines()))

# G1으로 시작하는 문자열만 잘라넣기 위한 리스트
filtlist = []
# G1으로 시작하는 문장만 저장한다.
for line in loadlines:
    if line.startswith('G1'):
        filtlist.append(line)
    if line.startswith(";LAYER_CHANGE"):
        filtlist.append(line)

#1) 초기값 설정. X, Y, Z, F 각 정보는 각각의 리스트로 저장됨.
XHomepos, YHomepos, ZHomepos, Ffirstval = '0', '0', '0', '1000'
X = [0]
Y = [0]
Z = [0]
layer = []
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
    if line.startswith(";LAYER_CHANGE"):
        layer.append(len(X))
        continue
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
layer.append(len(X))
X=tuple(X)
Y=tuple(Y)
Z=tuple(Z)
F=tuple(F)
X2 = []
Y2 = []
Z2 = []
for i in range(len(X)):
    X2.append(X[i] / 1000)
    Y2.append(Y[i] / 1000)
    Z2.append(Z[i] / 1000)
X2 = tuple(X2)
Y2 = tuple(Y2)
Z2 = tuple(Z2)
# GCODE 읽기 끝

# URDF 읽기
my_chain = Chain.from_urdf_file(
                urdf_dir, 
                base_elements=['base_link'])
# URDF 읽기 끝


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
# 노트북 바인딩 및 GUI 메인루프 실행.
notebook.bind('<<NotebookTabChanged>>', None)

# 좌측 plot figure 배치 frame 추출 및 기타 widget destroy
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
fig.subplots_adjust(bottom=0.2, left=0.1)
# 세로 슬라이더, 어떤 레이어를 선택한다.
axLayer = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
layer_slider = Slider(
    ax=axLayer,
    label='layer',
    valmin=0,
    valmax=len(layer)-1,
    valinit=0,
    valstep=1,
    orientation="vertical"
)
# 가로 슬라이더, 한 레이어 내에서 어떤 순간을 선택한다.
axSlider = fig.add_axes([0.2, 0.1, 0.65, 0.03])
point_slider = Slider(
    ax=axSlider,
    label='point',
    valmin=0,
    valmax=layer[1]-layer[0],
    valinit=0,
    valstep=1,
)

# 그 좌표에 대해 엔드 이펙터의 방향까지 고려해 계산한 결과를
# 로봇팔과 함께 그려주는 코드를 작성하였다.
def update(val):
    ax.clear()
    val = layer[layer_slider.val] + point_slider.val
    stateofArm = my_chain.inverse_kinematics([X2[val], Y2[val], Z2[val]], [0, 0, -1], "Z")
    my_chain.plot(stateofArm, ax, [X2[val], Y2[val], Z2[val]])
    ax.set_xlim(-0.1, 0.1)
    ax.set_ylim(-0.1, 0.1)
    ax.set_zlim(-0.1, 0.1)
def update_layer(val):
    point_slider.set_val(0)
    point_slider.valmax = layer[val+1] - layer[val]
    point_slider.ax.set_xlim(point_slider.valmin,point_slider.valmax)
    update(val)
layer_slider.on_changed(update_layer)
point_slider.on_changed(update)
update(0)

# 2) GUI에 canvas로 그림.
canvas = FigureCanvasTkAgg(fig, master=frame1L)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, frame1L, pack_toolbar=False)
toolbar.update()
toolbar.place(x=0, y=476, width=800, height=25)
canvas.get_tk_widget().place(x=0,y=0, width=800, height=476)


window.mainloop()


