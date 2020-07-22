from tkinter import *
from tkinter.font import Font
#import main
from threading import Thread
from time import sleep


class ProgramThread(Thread):
    instance_created = False

    def run(self):
        if ProgramThread.instance_created is not True:
            #main.welcome_user()
            #main.main()
            ProgramThread.instance_created = False

    def set_instance_created(self):
        ProgramThread.instance_created = True


class Application(Frame):
    def __init__(self):
        super().__init__()
        self.MainMenu()
        self.SettingsMenu().pack_forget()

    color_theme = {
        1: '#4C95BB',  # Regular Buttons
        2: '#F4761D',  # Quit Button
        3: '#636363',  # Integrated Frames
        4: '#4C4A49'  # Background
    }

    class AppButton:
        def __init__(self, text, frame, color1=None, color2=None, font_color='black', command=None, offx=10, offy=10):
            if color1 is None:
                color1 = Application.color_theme[1]
            if color2 is None:
                color2 = Application.color_theme[1]

            my_font = Font(size=15)
            button = Button(frame, text=text, height=1, width=8, bg=color1,
                            activebackground=color2, fg=font_color,
                            padx=20, pady=10)
            if command is not None:
                button['command'] = command
            button['font'] = my_font
            button.pack(padx=offx, pady=offy)

    class MainMenu(Frame):
        def __init__(self):
            super().__init__()
            self.init_widgets()

        # region COMMANDS
        def go_to_settings(self):
            self.pack_forget()
            Application.SettingsMenu().open_page()
        # endregion

        def set_up_menu(self):
            background_frame = Frame(self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)

            top_frame = Frame(background_frame, bg=Application.color_theme[4])
            top_frame.pack(side=TOP, fill=X)

            left_frame = Frame(top_frame, bg=Application.color_theme[3])
            left_frame.pack(expand=False, fill=Y, side=LEFT, pady=10, padx=10)

            title_font = Font(size=20)
            title = Label(left_frame, text='TSReporter',
                          bg=Application.color_theme[4], font=title_font, padx=17, pady=5, fg=Application.color_theme[2])
            title.pack(side=TOP)

            report_button = Application.AppButton('Report Bugs', frame=left_frame)
            batch_report_button = Application.AppButton('Batch Report', frame=left_frame)
            settings_button = Application.AppButton('Settings', frame=left_frame, command=self.go_to_settings)
            quit_button = Application.AppButton('QUIT', color1=Application.color_theme[2], color2=Application.color_theme[2],
                                                frame=left_frame, font_color='white')

        def init_widgets(self):
            self.pack(fill=BOTH, expand=True)
            self.set_up_menu()

        def open_page(self):
            self.pack()

    class SettingsMenu(Frame):
        def __init__(self):
            super().__init__()
            self.init_widgets()

        # region COMMANDS
        def go_to_main_menu(self):
            self.pack_forget()
            Application.MainMenu().open_page()
        # endregion

        def open_page(self):
            self.pack(fill=BOTH, expand=True)

        def init_widgets(self):
            background = Frame(self, bg=Application.color_theme[4])
            background.pack(fill=BOTH, expand=True)
            button = Application.AppButton('BACK', frame=background, command=self.go_to_main_menu)


root = Tk()
root.geometry('960x540')
root.minsize(width=960, height=540)
root.maxsize(width=960, height=540)
root.wm_iconbitmap('.//resources/icon.ico')
root.wm_title('TSReporter')
app = Application()
root.mainloop()
