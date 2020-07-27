from tkinter import *
from tkinter.font import Font
from threading import Thread
import bugs
import config


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
    main_menu = None
    settings_menu = None

    def __init__(self):
        super().__init__()
        self.main_menu = self.MainMenu()

    color_theme = {
        1: '#2C7FDB',  # Regular Buttons
        2: '#ffa500',  # Quit Button
        3: '#484848',  # Integrated Frames
        4: '#2B2B2B'  # Background
    }

    class Page(Frame):
        def open_page(self):
            self.pack(fill=BOTH, expand=True)

        def close_page(self):
            self.pack_forget()

        def refresh_page(self):
            self.pack_forget()
            self.open_page()

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

    class MainMenu(Page):
        def __init__(self):
            super().__init__()
            self.init_widgets()

        # region COMMANDS
        def go_to_settings(self):
            self.pack_forget()
            app.settings_menu = Application.SettingsMenu()
            app.settings_menu.open_page()
            self.destroy()

        # endregion

        def set_up_menu(self):
            try:
                ats_bugs_count = bugs.count_bugs()[0]
            except FileNotFoundError:
                ats_bugs_count = 'N/A'

            try:
                ets_bugs_count = bugs.count_bugs()[1]
            except FileNotFoundError:
                ets_bugs_count = 'N/A'

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

            placeholder_frame = Frame(left_frame, bg=Application.color_theme[3])
            placeholder_frame.pack(fill=BOTH, pady=70)

            quit_button = Application.AppButton('QUIT', color1=Application.color_theme[2], color2=Application.color_theme[2],
                                                frame=left_frame, font_color='white', command=quit)

            bugs_count_frame = Frame(top_frame, bg=Application.color_theme[3])
            bugs_count_frame.pack(side=TOP, pady=10)
            subtitle_font = Font(size=15)
            reports_count_text = Label(bugs_count_frame, text=f'Number of bugs in bugs.txt', bg=Application.color_theme[4], fg=Application.color_theme[2], font=subtitle_font)
            reports_count_text.pack()
            ETS2_bugs_count = Label(bugs_count_frame, text=f'ETS 2: {ets_bugs_count}',
                                       bg=Application.color_theme[3], fg=Application.color_theme[1], font=subtitle_font)
            ETS2_bugs_count.pack()
            ATS_bugs_count = Label(bugs_count_frame, text=f'ATS: {ats_bugs_count}',
                                       bg=Application.color_theme[3], fg=Application.color_theme[1], font=subtitle_font)
            ATS_bugs_count.pack()

            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, fill=X)

            version = 'v 0.2.3'
            version_label = Label(bottom_frame, text=version,
                                  bg=Application.color_theme[4],
                                  fg=Application.color_theme[2])
            version_label.pack(side=RIGHT)

        def init_widgets(self):
            self.pack(fill=BOTH, expand=True)
            self.set_up_menu()

    class SettingsMenu(Page):
        def __init__(self):
            super().__init__()
            self.init_widgets()

        class SettingsOption:
            def __init__(self, background, row, text, include_button=True, button_text='Change'):
                title_font = Font(size=20)
                subtitle_font = Font(size=15)

                setting_name_frame = Frame(background, bg=Application.color_theme[3])
                setting_name_frame.grid(row=row, column=0, sticky=W+E+N+S, pady=10)

                value_frame = Frame(background, bg=Application.color_theme[3])
                value_frame.grid(row=row, column=1, sticky=W+E+N+S, pady=10)

                button_frame = Frame(background, bg=Application.color_theme[3])
                button_frame.grid(row=row, column=2, padx=100, sticky=W+E+N+S, pady=10)

                setting_name_frame_packed = Frame(setting_name_frame)

                left_frame = Frame(setting_name_frame, bg=Application.color_theme[3])
                left_frame.pack(fill=X, side=TOP)
                frame_text = Label(left_frame, text=text,
                                             font=subtitle_font,
                                             fg=Application.color_theme[2],
                                             bg=Application.color_theme[3],
                                             pady=5, padx=10)
                frame_text.pack(side=LEFT)

                key_to_find = text.lower().split(':')[0]
                directory_path = config.ConfigHandler.read(key_to_find)

                directory_value_frame = Frame(value_frame, bg=Application.color_theme[3])
                directory_value_frame.pack(fill=BOTH, side=TOP)
                directory_value = Label(directory_value_frame, text=f'{directory_path}',
                                              font=subtitle_font,
                                              fg=Application.color_theme[2],
                                              bg=Application.color_theme[3],
                                              pady=5, padx=2)
                directory_value.pack(side=LEFT, fill=BOTH)
                if include_button:
                    directory_button_frame = Frame(button_frame, bg=Application.color_theme[3])
                    directory_button_frame.pack(fill=X, side=TOP)
                    directory_button = Button(directory_button_frame, text=button_text,
                                                    bg=Application.color_theme[1],
                                                    activebackground=Application.color_theme[1]
                                                    , command=lambda: self.ask_for_directory(row))
                    directory_button.pack(side=RIGHT)

            def ask_for_directory(self, index):
                config.ConfigHandler.gui_config_edit(index)
                app.settings_menu.go_to_main_menu()
                app.main_menu.go_to_settings()

        # region COMMANDS
        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            self.destroy()
        # endregion

        def init_widgets(self):
            template_background = Frame(self, bg=Application.color_theme[4])
            template_background.pack(fill=BOTH, expand=True)

            background = Frame(template_background, bg=Application.color_theme[3])
            background.pack(fill=BOTH, expand=True, padx=10, pady=10)

            settings_frame = Frame(background, bg=Application.color_theme[3])
            settings_frame.pack(fill=BOTH, expand=True)

            self.SettingsOption(background=settings_frame, row=0, text='TRUNK LOCATION: ')
            self.SettingsOption(background=settings_frame, row=1, text='DOCUMENTS LOCATION: ')
            self.SettingsOption(background=settings_frame, row=2, text='EDITED IMAGES LOCATION: ')
            self.SettingsOption(background=settings_frame, row=3, text='MANTIS USERNAME: ')
            self.SettingsOption(background=settings_frame, row=4, text='PREFERRED BROWSER: ')

            button = Application.AppButton('BACK', frame=template_background, command=self.go_to_main_menu)


root = Tk()
root.geometry('960x540')
root.minsize(width=960, height=540)
root.maxsize(width=960, height=540)
root.wm_iconbitmap('.//resources/icon.ico')
root.wm_title('TSReporter')
app = Application()
root.mainloop()
