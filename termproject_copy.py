
import re    # Gcode해석용 정규표현식 모듈.
import tkinter    # GUI tkinter 모듈.
import tkinter.ttk    # GUI 추가 위젯 모듈.
import tkinter.font    # GUI 추가 폰트 모듈.
from tkinter import filedialog    # 파일 가져오기용 모듈.

# 전역 변수의 선언
gcode_dir = None
gcode_name = None

# GCODE 파일의 경로와 이름을 알아낸다.
def openGCODE():
    global gcode_dir, gcode_name
    gcode_dir = filedialog.askopenfile(filetypes=(('gcode files', '*.gcode'), ('all types', '*.*')))
    gcode_name = re.findall('[a-zA-Z]*[.]gcode', gcode_dir.name)[0].removesuffix('.gcode')
    print(gcode_dir.name)
    print(gcode_name)

# GUI내에서 다른 탭으로 이동시 호출되는 함수.
def tabchange(event):
    tab_id = notebook.select()
    print(tab_id)
    if tab_id == '.!frame':
        tab1refresh()
    elif tab_id == '.!frame2':
        tab2refresh()
    elif tab_id == '.!frame3':
        tab3refresh()

# 1번 탭으로 이동했을 때 1번 탭 리프레쉬.
def tab1refresh():

    frame1L=tkinter.Frame(frame1, relief="groove", bd=2)
    frame1L.place(x=0,y=0, width=800, height=552)

    buttonL1 = tkinter.Button(frame1L, text="Plot", relief="solid", command=None)
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
    buttonR3 = tkinter.Button(frame1R, text="See Filtered gcode", relief="solid", command=None)
    buttonR3.place(x=12, y=120, width=230, height=30)
    buttonR3 = tkinter.Button(frame1R, text="Export", relief="solid", command=None)
    buttonR3.place(x=12, y=165, width=230, height=30)
    clearbtn = tkinter.Button(frame1R, text="clear", relief="solid", command=None)
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
    buttonR3 = tkinter.Button(frame2R, text="Export", relief="solid", command=None)
    buttonR3.place(x=12, y=165, width=230, height=30)
    clearbtn = tkinter.Button(frame2R, text="clear", relief="solid", command=None)
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

# 노트북 바인딩 및 GUI 메인루프 실행.
notebook.bind('<<NotebookTabChanged>>',tabchange)

window.mainloop()