from tkinter import *
from tkinter.font import Font
from threading import Thread
import bugs
import config
from PIL import ImageTk, Image
import main


class ProgramThread(Thread):
    # When this class is called, calls a function from main.py to report a bug
    # This is a separate thread from the gui thread, it is also a singleton
    instance_created = False

    def run(self):
        # After creating the thread object, call its ProgramThread().start() to call run()
        if ProgramThread.instance_created is not True:
            ProgramThread.instance_created = False
            password = 'CrYVhn7FSM'
            main.report_option(use_mode=1, cfg_handler=config.ConfigHandler(), password=password)

    def set_instance_created(self):
        # This is needed for singleton, we do not want to run multiple reporting threads at the same time... yet
        ProgramThread.instance_created = True


class Application(Frame):
    # The first GUI element put in the basic Win window, important for layout, everything sits on this
    main_menu = None
    settings_menu = None
    projects_page = None
    duplicates = None
    # It's important to keep in mind the class instances above,
    # when gui is active, exactly one has to have a non Null value, cuz having more than one pages active
    # at the same time is BS

    def __init__(self):
        super().__init__()
        self.main_menu = self.MainMenu()

    color_theme = {
        # Change the values below to change the overall color theme of the app
        1: 'white',  # Regular Buttons, bugs counter text
        2: '#ffa500',  # Quit Button, text
        3: '#484848',  # Integrated Frames
        4: '#2B2B2B'  # Background
    }

    class Page(Frame):
        # All pages inherit from this class
        def open_page(self):
            self.pack(fill=BOTH, expand=True)

        def close_page(self):
            self.pack_forget()

    class AppButton:
        text = None
        element = None
        # The basic template that is used for most buttons in the app
        # Create an instance of this class to quickly create a new button

        def __init__(self, text, frame, color1=None, color2=None, font_color='black', command=None,
                     offx=10, offy=10, font_size=15, text_spacing=20, side=None, pady=10):
            if color1 is None:
                color1 = Application.color_theme[1]
            if color2 is None:
                color2 = Application.color_theme[1]

            self.text = text

            my_font = Font(size=font_size)
            button = Button(frame, text=text, height=1, width=8, bg=color1,
                            activebackground=color2, fg=font_color,
                            padx=text_spacing, pady=pady)
            self.element = button
            if command is not None:
                button['command'] = command
            button['font'] = my_font
            button.pack(padx=offx, pady=offy, side=side)

        def set_sunken(self):
            self.element['relief'] = SUNKEN
            self.element['state'] = ACTIVE

        def set_raised(self):
            self.element['relief'] = RAISED
            self.element['state'] = DISABLED

        def get_text(self):
            return self.text

        def get_element(self):
            return self.element

    class MainMenu(Page):
        # The first page that is displayed when the program starts
        # Its first instance is created in the constructor of the Application class
        def __init__(self):
            super().__init__()
            self.init_widgets()

        # region COMMANDS
        # Commands are functions callable by buttons
        def go_to_settings(self):
            # ACHTUNG! When you destroy an instance of a page class, remember to create a new one of a different
            # page class as following:
            self.pack_forget()
            app.settings_menu = Application.SettingsMenu()
            app.settings_menu.open_page()
            self.destroy()

        def start_reporting(self):
            # Here we create a new thread on which the reporting loop is running
            ProgramThread().start()

        def go_to_projects(self):
            self.pack_forget()
            app.projects_page = Application.SelectProject()
            app.projects_page.open_page()
            self.destroy()

        # endregion

        def set_up_menu(self):
            # Think of this as HTML, but much more messy and frustrating

            try:
                # Handles the variables needed for the bug counter for ATS
                ats_bugs_count = bugs.count_bugs()[0]
            except FileNotFoundError:
                ats_bugs_count = 'N/A'

            try:
                # Same but for ETS
                ets_bugs_count = bugs.count_bugs()[1]
            except FileNotFoundError:
                ets_bugs_count = 'N/A'

            background_frame = Frame(self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)
            # The main frame of this page

            top_frame = Frame(background_frame, bg=Application.color_theme[4])
            top_frame.pack(side=TOP, fill=X)
            # duh

            left_frame = Frame(top_frame, bg=Application.color_theme[3])
            left_frame.pack(expand=False, fill=Y, side=LEFT, pady=10, padx=10)

            # From now on the variable names are pretty self-explanatory

            title_font = Font(size=20)

            title = Label(left_frame, text='TSReporter',
                          bg=Application.color_theme[4], font=title_font, padx=17, pady=5, fg=Application.color_theme[2])
            title.pack(side=TOP)

            report_button = Application.AppButton('Report Bugs', frame=left_frame,
                                                  command=self.go_to_projects)
            batch_report_button = Application.AppButton('Batch Report', frame=left_frame)
            settings_button = Application.AppButton('Settings', frame=left_frame,
                                                    command=self.go_to_settings)

            placeholder_frame = Frame(left_frame, bg=Application.color_theme[3])
            placeholder_frame.pack(fill=BOTH, pady=70)
            # This is only for creating the gap between regular buttons and the quit button

            quit_button = Application.AppButton('QUIT', color1=Application.color_theme[2], color2=Application.color_theme[2],
                                                frame=left_frame, font_color='white', command=quit)

            # region BUG COUNTER
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
            # endregion

            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, fill=X)

            img = ImageTk.PhotoImage(Image.open("./resources/logo.png"))
            img_panel = Label(top_frame, image=img, bg=Application.color_theme[4])
            img_panel.image = img
            img_panel.place(x=0, y=0)
            img_panel.pack(pady=100, side=BOTTOM)

            with open('version.txt', 'r') as version_file:
                # Reads the version and displays it on the screen
                version = version_file.readline()
            version_label = Label(bottom_frame, text=version,
                                  bg=Application.color_theme[4],
                                  fg=Application.color_theme[2])
            version_label.pack(side=RIGHT)

        def init_widgets(self):
            self.pack(fill=BOTH, expand=True)
            self.set_up_menu()

    class SettingsMenu(Page):
        # The settings page where you can change, you guessed it, settings! AKA former config
        def __init__(self):
            super().__init__()
            self.init_widgets()

        class SettingsOption:
            # Instance of this class creates a new row (option)
            # What you enter in the "text" attribute will be analyzed to find the path in config.txt
            def __init__(self, background, row, text, include_button=True, button_text='Change', command=None):
                subtitle_font = Font(size=15)
                minimized_font = Font(size=10)
                super_minimized_font = Font(size=7)

                setting_name_frame = Frame(background, bg=Application.color_theme[3])
                setting_name_frame.grid(row=row, column=0, sticky=W+E+N+S, pady=5)

                value_frame = Frame(background, bg=Application.color_theme[3])
                value_frame.grid(row=row, column=1, sticky=W+E+N+S, pady=5, padx=10)

                button_frame = Frame(background, bg=Application.color_theme[4])
                button_frame.grid(row=row, column=2, padx=10, sticky=W+E+N+S, pady=10)

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
                directory_path = config.read_config(key_to_find)

                directory_value_frame = Frame(value_frame, bg=Application.color_theme[3])
                directory_value_frame.pack(fill=BOTH, side=TOP)

                if len(directory_path) <= 48:
                    directory_value = Label(directory_value_frame, text=f'{directory_path}',
                                                  font=subtitle_font,
                                                  fg=Application.color_theme[2],
                                                  bg=Application.color_theme[3],
                                                  pady=5, padx=10)
                elif len(directory_path) <= 75:
                    directory_value = Label(directory_value_frame, text=f'{directory_path}',
                                            font=minimized_font,
                                            fg=Application.color_theme[2],
                                            bg=Application.color_theme[3],
                                            pady=5, padx=10)
                elif len(directory_path) <= 107:
                    directory_value = Label(directory_value_frame, text=f'{directory_path}',
                                            font=super_minimized_font,
                                            fg=Application.color_theme[2],
                                            bg=Application.color_theme[3],
                                            pady=5, padx=10)
                else:
                    directory_value = Label(directory_value_frame, text=f'...',
                                            font=subtitle_font,
                                            fg=Application.color_theme[2],
                                            bg=Application.color_theme[3],
                                            pady=5, padx=10)


                directory_value.pack(side=LEFT, fill=BOTH)
                if include_button:
                    directory_button_frame = Frame(button_frame, bg=Application.color_theme[3])
                    directory_button_frame.pack(fill=X, side=TOP)
                    directory_button = Button(directory_button_frame, text=button_text,
                                                    bg=Application.color_theme[1],
                                                    activebackground=Application.color_theme[1])
                    if command == None:
                        directory_button['command'] = lambda: self.ask_for_directory(row)
                    else:
                        directory_button['command'] = command

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

        def submit(self, text_input, event=None):
            username = text_input.get()
            config.ConfigHandler.gui_config_edit(3, entered_text=username)
            app.settings_menu.go_to_main_menu()
            app.main_menu.go_to_settings()
        text_input_activated = False

        def show_text_input(self, master):
            if not self.text_input_activated:
                self.text_input_activated = True
                text_input = Entry(master, bg=Application.color_theme[3], fg=Application.color_theme[2], width=25,
                                   font=Font(size=20))
                text_input.pack()
                submit_button = Button(master, bg=Application.color_theme[3], fg=Application.color_theme[2], text='Submit',
                                       command=lambda: self.submit(text_input))
                root.bind('<Return>', lambda x: self.submit(text_input))
                submit_button.pack(pady=5)

        # endregion

        def init_widgets(self):
            template_background = Frame(self, bg=Application.color_theme[4])
            template_background.pack(fill=BOTH, expand=True)

            background = Frame(template_background, bg=Application.color_theme[4])
            background.pack(fill=BOTH, expand=True, padx=10, pady=10)

            subbackground = Frame(background, bg=Application.color_theme[4])
            subbackground.pack(fill=Y, expand=False, padx=10, pady=10)

            grid_i = 0
            for setting in config.ConfigHandler.config_layout.keys():
                if config.ConfigHandler.config_layout[setting] == "secret":
                    continue
                elif config.ConfigHandler.config_layout[setting] == "text":
                    self.SettingsOption(background=subbackground, row=grid_i, text=f'{setting.capitalize()}: ', command=lambda: self.show_text_input(background))
                    grid_i += 1
                else:
                    self.SettingsOption(background=subbackground, row=grid_i, text=f'{setting.capitalize()}: ')
                    grid_i += 1

            button = Application.AppButton('Main Menu', frame=template_background, command=self.go_to_main_menu, side=LEFT)

    class SelectProject(Page):
        def __init__(self):
            super().__init__()
            self.init_widgets()

        # region COMMANDS
        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            self.destroy()

        def go_to_duplicates(self, project):
            self.pack_forget()
            app.duplicates = Application.Duplicates(project=project)
            self.destroy()

        def select_project(self, button):
            selected_project = button.get_text()
            self.go_to_duplicates(selected_project)

        # endregion

        def init_widgets(self):
            background = Frame(self, bg=Application.color_theme[4])
            background.pack(fill=BOTH, expand=True)

            bottom_frame = Frame(background, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, fill=X)

            back_button = Application.AppButton('Main Menu', frame=bottom_frame, command=self.go_to_main_menu, side=LEFT)

            buttons_background = Frame(background, bg=Application.color_theme[2])
            buttons_background.pack(padx=10, pady=30, side=LEFT, fill=Y)

            buttons_frame = Frame(buttons_background, bg=Application.color_theme[3])
            buttons_frame.pack(side=LEFT, padx=10, pady=10, fill=Y)
            ats_internal_button = Application.AppButton(text='ATS - INTERNAL', frame=buttons_frame, font_size=10,
                                                        text_spacing=52, pady=5)
            ats_public_button = Application.AppButton(text='ATS - PUBLIC', frame=buttons_frame, font_size=10,
                                                      text_spacing=52, pady=5)
            ats_public_seniors_button = Application.AppButton(text='ATS - PUBLIC - SENIORS', frame=buttons_frame,
                                                              font_size=10, text_spacing=52, pady=5)
            gap = Frame(buttons_frame, bg=Application.color_theme[3])
            gap.pack(fill=Y, pady=20)
            ets_internal_button = Application.AppButton(text='ETS 2 - INTERNAL', frame=buttons_frame, font_size=10,
                                                        text_spacing=52, pady=5)
            ets_public_button = Application.AppButton(text='ETS 2 - PUBLIC', frame=buttons_frame, font_size=10,
                                                      text_spacing=52, pady=5)
            ets_public_seniors_button = Application.AppButton(text='ETS 2 - PUBLIC - SENIORS', frame=buttons_frame,
                                                              font_size=10, text_spacing=52, pady=5)

            buttons = [ats_internal_button, ats_public_button, ats_public_seniors_button,
                       ets_internal_button, ets_public_button, ets_public_seniors_button]

            ats_internal_button.get_element()['command'] = lambda: self.select_project(ats_internal_button)
            ats_public_button.get_element()['command'] = lambda: self.select_project(ats_public_button)
            ats_public_seniors_button.get_element()['command'] = lambda: self.select_project(ats_public_seniors_button)
            ets_internal_button.get_element()['command'] = lambda: self.select_project(ets_internal_button)
            ets_public_button.get_element()['command'] = lambda: self.select_project(ets_public_button)
            ets_public_seniors_button.get_element()['command'] = lambda: self.select_project(ets_public_seniors_button)

    class Duplicates(Page):
        selected_project = None

        def __init__(self, project):
            super().__init__()
            self.selected_project = project
            self.init_widgets()

        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            self.destroy()

        def init_widgets(self):
            background_frame = Frame(master=self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)
            print(self.selected_project)
            button = Application.AppButton('Main Menu', frame=background_frame, command=self.go_to_main_menu,
                                           side=LEFT)

# Creates the basic "box" in which you can put all of the GUI elements
# It also takes care of misc stuff, s.a. fixed window size, title on the app window and the icon
root = Tk()
root.geometry('960x540')
root.minsize(width=960, height=540)
root.maxsize(width=960, height=540)
root.wm_iconbitmap('.//resources/icon.ico')
root.wm_title('TSReporter')
app = Application()
root.mainloop()
