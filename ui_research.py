from tkinter import *
from tkinter.font import Font
import main
from threading import Thread
from time import sleep


class ProgramThread(Thread):
    instance_created = False

    def run(self):
        if ProgramThread.instance_created is not True:
            main.welcome_user()
            main.main()
            ProgramThread.instance_created = False

    def set_instance_created(self):
        ProgramThread.instance_created = True


class Application(Frame):
    color_theme = {
        1: '#4C95BB',  # Regular Buttons
        2: '#F4761D',  # Quit Button
        3: '#636363',  # Integrated Frames
        4: '#4C4A49'   # Background
    }

    class MenuButton:
        def __init__(self, text, frame, color1=None, color2=None,font_color='black'):
            if color1 is None:
                color1 = Application.color_theme[1]
            if color2 is None:
                color2 = Application.color_theme[1]

            my_font = Font(size=15)
            report_bugs_button = Button(frame, text=text, height=1, width=10, bg=color1,
                                        activebackground=color2,
                                        padx=20, pady=20)
            report_bugs_button['font'] = my_font
            report_bugs_button.pack(padx=10, pady=10)

    def __init__(self):
        super().__init__()
        self.init_widgets()

    def set_up_menu(self):
        background_frame = Frame(self, bg=self.color_theme[4])
        background_frame.pack(fill=BOTH, expand=True)

        top_frame = Frame(background_frame, bg=self.color_theme[4])
        top_frame.pack(side=TOP, fill=X)

        left_frame = Frame(top_frame, bg=self.color_theme[3])
        left_frame.pack(side=LEFT, pady=10, padx=10)

        title_font = Font(size=20)
        title = Label(left_frame, text='TSReporter',
                      bg=self.color_theme[4], font=title_font, padx=17, pady=5, fg=self.color_theme[2])
        title.pack(side=TOP)

        report_button = self.MenuButton('Report Bugs', frame=left_frame)
        batch_report_button = self.MenuButton('Batch Report', frame=left_frame)
        settings_button = self.MenuButton('Settings', frame=left_frame)
        quit_button = self.MenuButton('QUIT', color1=self.color_theme[2], color2=self.color_theme[2],
                                      frame=left_frame, font_color='white')

    def init_widgets(self):
        self.pack(fill=BOTH, expand=True)
        self.set_up_menu()


root = Tk()
root.geometry('1200x600')
root.wm_iconbitmap('.//resources/icon.ico')
root.wm_title('TSReporter')
app = Application()
root.mainloop()
