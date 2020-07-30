from tkinter import *
from tkinter.font import Font
from threading import Thread
from PIL import ImageTk, Image

import main
from versions import find_version
import bugs
import config
from gui_bughandler import BugHandler
from chromedrivers import DriverHandler
import utils
import reporter


class ProgramThread(Thread):
    # When this class is called, calls a function from main.py to report a bug
    # This is a separate thread from the gui thread, it is also a singleton
    instance_created = False

    def run(self):
        # After creating the thread object, call its ProgramThread().start() to call run()
        if ProgramThread.instance_created is not True:
            ProgramThread.instance_created = False
            password = 'CrYVhn7FSM'
            config.ConfigHandler()
            main.report_option(use_mode=1, password=password)

    @staticmethod
    def set_instance_created(self):
        # This is needed for singleton, we do not want to run multiple reporting threads at the same time... yet
        ProgramThread.instance_created = True


class Application(Frame):
    # The first GUI element put in the basic Win window, important for layout, everything sits on this
    main_menu = None
    settings_menu = None
    projects_page = None
    reporting = None
    batch = None

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
                     offx=10, offy=10, font_size=15, text_spacing=20, side=None, pady=10, anchor=None):
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
            button.pack(padx=offx, pady=offy, side=side, anchor=anchor)

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

        @staticmethod
        def start_reporting(self):
            # Here we create a new thread on which the reporting loop is running
            ProgramThread().start()

        def go_to_projects(self, use_mode):
            self.pack_forget()
            app.projects_page = Application.SelectProject(use_mode)
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

            # title_font = Font(size=20)
            title_font = "Helvetica 20 bold"

            title = Label(left_frame, text='TSReporter',
                          bg=Application.color_theme[4], font=title_font, padx=17, pady=5,
                          fg=Application.color_theme[2])
            title.pack(side=TOP)

            report_button = Application.AppButton('Report Bugs', frame=left_frame,
                                                  command=lambda: self.go_to_projects("normal"))
            batch_report_button = Application.AppButton('Batch Report', frame=left_frame,
                                                        command=lambda: self.go_to_projects("batch"))
            settings_button = Application.AppButton('Settings', frame=left_frame,
                                                    command=self.go_to_settings)

            placeholder_frame = Frame(left_frame, bg=Application.color_theme[3])
            placeholder_frame.pack(fill=BOTH, pady=70)
            # This is only for creating the gap between regular buttons and the quit button

            quit_button = Application.AppButton('QUIT', color1=Application.color_theme[2],
                                                color2=Application.color_theme[2],
                                                frame=left_frame, font_color='white', command=quit)

            # region BUG COUNTER
            bugs_count_frame = Frame(top_frame, bg=Application.color_theme[3])
            bugs_count_frame.pack(side=TOP, pady=10)
            subtitle_font = Font(size=15)
            reports_count_text = Label(bugs_count_frame, text=f'Number of bugs in bugs.txt',
                                       bg=Application.color_theme[4], fg=Application.color_theme[2], font=subtitle_font)
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
                setting_name_frame.grid(row=row, column=0, sticky=W + E + N + S, pady=5)

                value_frame = Frame(background, bg=Application.color_theme[3])
                value_frame.grid(row=row, column=1, sticky=W + E + N + S, pady=5, padx=10)

                button_frame = Frame(background, bg=Application.color_theme[4])
                button_frame.grid(row=row, column=2, padx=10, sticky=W + E + N + S, pady=10)

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

                selected_text = f'{directory_path}'
                if len(directory_path) <= 48:
                    selected_font = subtitle_font
                elif len(directory_path) <= 75:
                    selected_font = minimized_font
                elif len(directory_path) <= 107:
                    selected_font = super_minimized_font
                else:
                    selected_font = subtitle_font
                    selected_text = '...'
                directory_value = Label(directory_value_frame, text=selected_text,
                                        font=selected_font,
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
                    if command is None:
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
                submit_button = Button(master, bg=Application.color_theme[3], fg=Application.color_theme[2],
                                       text='Submit',
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
                    self.SettingsOption(background=subbackground, row=grid_i, text=f'{setting.capitalize()}: ',
                                        command=lambda: self.show_text_input(background))
                    grid_i += 1
                else:
                    self.SettingsOption(background=subbackground, row=grid_i, text=f'{setting.capitalize()}: ')
                    grid_i += 1

            button = Application.AppButton('Main Menu', frame=template_background, command=self.go_to_main_menu,
                                           side=LEFT)

    class SelectProject(Page):
        use_mode = None

        def __init__(self, use_mode):
            super().__init__()
            self.use_mode = use_mode
            self.init_widgets()

        # region COMMANDS
        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            self.destroy()

        def go_to_duplicates(self, project, bug_handler):
            self.pack_forget()
            app.reporting = Application.Reporting(project, bug_handler=bug_handler)
            self.destroy()

        def go_to_batch(self, project):
            self.pack_forget()
            app.batch = Application.Batch(project)
            self.destroy()

        def try_going_duplicates(self, project, frame):
            bug_handler = BugHandler(project[0])
            if not bug_handler.get_current():
                make_error_textbox(bug_handler.message, frame)
            else:
                self.go_to_duplicates(project, bug_handler)

        # endregion

        def init_widgets(self):
            background = Frame(self, bg=Application.color_theme[4])
            background.pack(fill=BOTH, expand=True)

            error_frame = Frame(background, bg=Application.color_theme[4])
            error_frame.pack(side=TOP, anchor="n")
            error_textbox = Text(error_frame, height=1, width=80, bg=Application.color_theme[4],
                                 fg=Application.color_theme[2], bd=0, font="Helvetica 12")
            error_textbox.pack(pady=0, padx=0, side=TOP, anchor='n')

            bottom_frame = Frame(background, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, anchor="sw")

            back_button = Application.AppButton('Main Menu', frame=bottom_frame, command=self.go_to_main_menu,
                                                anchor="sw")

            middle_frame = Frame(background, bg=Application.color_theme[4])
            middle_frame.pack(anchor="center", pady=70)

            buttons_ats_background = Frame(middle_frame, bg=Application.color_theme[2])
            buttons_ats_background.pack(padx=30, pady=30, side=LEFT)

            buttons_ats_frame = Frame(buttons_ats_background, bg=Application.color_theme[3])
            buttons_ats_frame.pack(side=LEFT, padx=10, pady=10)

            buttons_ets_background = Frame(middle_frame, bg=Application.color_theme[2])
            buttons_ets_background.pack(padx=30, pady=30, side=RIGHT)

            buttons_ets_frame = Frame(buttons_ets_background, bg=Application.color_theme[3])
            buttons_ets_frame.pack(side=LEFT, padx=10, pady=10)

            buttons = []
            ats_projects = ['ATS - INTERNAL', 'ATS - PUBLIC', 'ATS - PUBLIC - SENIORS']
            ets_projects = ['ETS2 - INTERNAL', 'ETS2 - PUBLIC', 'ETS2 - PUBLIC - SENIORS']

            for i in range(len(ats_projects)):
                this_button = Application.AppButton(text=ats_projects[i], frame=buttons_ats_frame,
                                                    font_size=15, text_spacing=85, pady=5)
                if self.use_mode == "batch":
                    this_button.get_element()['command'] = lambda c=i: self.go_to_batch(ats_projects[c])
                else:
                    this_button.get_element()['command'] = lambda c=i: self.try_going_duplicates(ats_projects[c],
                                                                                                 error_textbox)
                buttons.append(this_button)

            for i in range(len(ets_projects)):
                this_button = Application.AppButton(text=ets_projects[i], frame=buttons_ets_frame,
                                                    font_size=15, text_spacing=85, pady=5)
                if self.use_mode == "batch":
                    this_button.get_element()['command'] = lambda c=i: self.go_to_batch(ets_projects[c])
                else:
                    this_button.get_element()['command'] = lambda c=i: self.try_going_duplicates(ets_projects[c],
                                                                                                 error_textbox)
                buttons.append(this_button)

    class Reporting(Page):
        selected_project = None
        already_reported = None
        bug_handler = None
        image_location = None
        driver_handler = None

        def __init__(self, project, bug_handler, reported=False):
            super().__init__()

            if not bug_handler:
                raise ValueError
            else:
                self.bug_handler = bug_handler

            self.already_reported = reported
            self.selected_project = project
            self.pack(fill=BOTH, expand=True)
            self.init_widgets()

        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            self.destroy()

        def go_to_projects(self):
            self.pack_forget()
            app.projects_page = Application.SelectProject("normal")
            app.projects_page.open_page()
            self.destroy()

        def show_next_report(self):
            self.bug_handler.read_next()
            if not self.bug_handler.get_current():
                self.go_to_main_menu()
                return
            self.pack_forget()
            app.reporting = Application.Reporting(self.selected_project, self.bug_handler, reported=True)
            self.destroy()

        def find_missing_image(self, mode, image_label, buttons_frame, image_location_text):
            if mode == 0:
                self.image_location = utils.find_image_path()
            else:
                self.image_location = self.bug_handler.try_get_image()
            if self.image_location:
                img_to_show = self.get_displayable_image()
                image_label.configure(image=img_to_show)
                image_label.image = img_to_show
                buttons_frame.pack_forget()
                buttons_frame.destroy()
                image_location_text.insert(END, self.image_location)

        def get_displayable_image(self):
            image = Image.open(self.image_location)
            image.thumbnail((520, 520))
            img_to_show = ImageTk.PhotoImage(image)
            return img_to_show

        def open_duplicates(self, bug_line, report_button):
            if not self.driver_handler:
                self.driver_handler = DriverHandler(config.read_config("preferred browser"))
            reporter.check_for_duplicates(
                config.read_config("mantis username"), "CrYVhn7FSM", bug_line,
                driver_handler=self.driver_handler
            )
            report_button.get_element()['text'] = "REPORT"
            report_button.get_element()['command'] = lambda: self.open_report(bug_line)

        def open_report(self, bug_line):
            print(f"Reporting: {bug_line}")
            self.show_next_report()

        def init_widgets(self):
            background_frame = Frame(master=self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)
            version = find_version(self.selected_project[0])
            version_line = f"Reporting in project [{self.selected_project}] at version {version}"

            version_info_text = Text(background_frame, height=1, width=60, bg=Application.color_theme[4],
                                     fg=Application.color_theme[2], bd=0, font="Helvetica 12")
            version_info_text.pack(anchor="nw", pady=5, padx=5, side=TOP)
            version_info_text.insert(END, version_line)

            bug_bg_frame = Frame(background_frame, bg=Application.color_theme[3])
            bug_bg_frame.pack(anchor="center", pady=5, padx=15)

            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, fill=X)

            if self.already_reported:
                # If a report has been made already, it is not possible to go back to project selection
                # instead, this button will take the user to the main menu
                back_button = Application.AppButton(
                    'Main Menu', frame=bottom_frame, command=self.go_to_main_menu, side=LEFT)
            else:
                back_button = Application.AppButton(
                    'BACK', frame=bottom_frame, command=self.go_to_projects, side=LEFT)

            current_bug_summary = self.bug_handler.get_current()[0][:-1]
            current_bug_text = Text(bug_bg_frame, height=1, bg=Application.color_theme[3],
                                    fg=Application.color_theme[1], bd=0, font="Helvetica 14")
            current_bug_text.pack(side=TOP, fill=X, pady=5, padx=5)
            current_bug_text.insert(END, current_bug_summary)

            if not self.image_location:
                self.image_location = self.bug_handler.try_get_image()
            img_label = Label(bug_bg_frame, bg=Application.color_theme[3])
            img_label.place(x=0, y=0)
            img_label.pack(pady=5, side=TOP)
            image_location_text = Text(bug_bg_frame, height=1, width=60, bg=Application.color_theme[3],
                                       fg=Application.color_theme[1], bd=0, font="Helvetica 10")
            image_location_text.pack(anchor="s", pady=5, padx=5, side=BOTTOM)
            if self.image_location:
                img_to_show = self.get_displayable_image()
                img_label.configure(image=img_to_show)
                img_label.image = img_to_show
                image_location_text.insert(END, self.image_location)
            else:
                img_to_show = ImageTk.PhotoImage(Image.open("./resources/image_not_found.png"))
                img_label.configure(image=img_to_show)
                img_label.image = img_to_show
                image_buttons_frame = Frame(bug_bg_frame, bg=Application.color_theme[3])
                image_buttons_frame.pack(side=BOTTOM, padx=10, pady=10)
                try_again_button = Application.AppButton(
                    "Try again", image_buttons_frame, side=LEFT,
                    command=lambda: self.find_missing_image(1, img_label, image_buttons_frame, image_location_text)
                )
                image_path_button = Application.AppButton(
                    "Locate image", image_buttons_frame, side=LEFT,
                    command=lambda: self.find_missing_image(0, img_label, image_buttons_frame, image_location_text)
                )

            button_find_duplicates = Application.AppButton(
                "Find duplicates", bottom_frame, side=RIGHT,
                command=lambda: self.open_duplicates(current_bug_summary, button_find_duplicates)
            )
            button_skip_report = Application.AppButton(
                "Don't report", bottom_frame, side=RIGHT, command=self.show_next_report
            )

    class Batch(Page):
        def __init__(self, project):
            super().__init__()
            self.pack(fill=BOTH, expand=True)
            self.init_widgets()

        def go_to_projects(self):
            self.pack_forget()
            app.projects_page = Application.SelectProject("batch")
            app.projects_page.open_page()
            self.destroy()

        def init_widgets(self):
            background_frame = Frame(master=self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)

            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, anchor="sw")
            back_button = Application.AppButton('BACK', frame=bottom_frame, command=self.go_to_projects, anchor="sw")


def make_error_textbox(message, error_textbox):
    # error_textbox = Text(frame, height=1, width=80, bg=Application.color_theme[4],
    #                      fg=Application.color_theme[2], bd=0, font="Helvetica 12")
    # error_textbox.pack(pady=5, padx=5, side=TOP, anchor='n')
    error_textbox.delete("1.0", END)
    error_textbox.insert(END, message)


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
