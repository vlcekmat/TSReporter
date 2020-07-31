import copy
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
    reported = None
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
            parent_frame = None

            def __init__(self, background, row, text, parent_frame,
                         include_button=True, button_text='Change', command=None):
                self.parent_frame = parent_frame
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
                go_to_main_menu(self.parent_frame)
                app.main_menu.go_to_settings()

        # region COMMANDS

        def submit(self, text_input, event=None):
            username = text_input.get()
            config.ConfigHandler.gui_config_edit(3, entered_text=username)
            go_to_main_menu(self)
            app.main_menu.go_to_settings()

        input_activated = False

        def show_text_input(self, master):
            if not self.input_activated:
                self.input_activated = True
                text_input = Entry(master, bg=Application.color_theme[3], fg=Application.color_theme[2], width=25,
                                   font=Font(size=20))
                text_input.pack()
                submit_button = Button(master, bg=Application.color_theme[3], fg=Application.color_theme[2],
                                       text='Submit',
                                       command=lambda: self.submit(text_input))
                root.bind('<Return>', lambda x: self.submit(text_input))
                submit_button.pack(pady=5)

        def ask_yes_no(self, master, setting):
            if not self.input_activated:
                self.input_activated = True
                buttons_frame = Frame(master, bg=Application.color_theme[3])
                buttons_frame.pack(pady=10)

                reported_text = Entry(buttons_frame, bg=Application.color_theme[3],
                                      fg=Application.color_theme[1], bd=0, font="Helvetica 14", justify=CENTER)
                reported_text.pack(anchor="n", pady=5, padx=5, side=TOP)
                reported_text.insert(0, setting.capitalize() + "?")

                yes_button = Application.AppButton(
                    "Yes", buttons_frame, side=LEFT, text_spacing=0, pady=0, font_size=12
                )
                no_button = Application.AppButton(
                    "No", buttons_frame, side=RIGHT, text_spacing=0, pady=0, font_size=12
                )
                # TODO: make these buttons do stuff

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
                    self.SettingsOption(subbackground, parent_frame=self, row=grid_i, text=f'{setting.capitalize()}: ',
                                        command=lambda: self.show_text_input(background))
                elif config.ConfigHandler.config_layout[setting] == "yn":
                    self.SettingsOption(
                        background=subbackground, parent_frame=self, row=grid_i, text=f'{setting.capitalize()}: ',
                        command=lambda s=setting: self.ask_yes_no(background, s)
                    )
                else:
                    self.SettingsOption(
                        parent_frame=self, background=subbackground, row=grid_i, text=f'{setting.capitalize()}: '
                    )
                grid_i += 1

            button = Application.AppButton('Main Menu', frame=template_background,
                                           command=lambda: go_to_main_menu(self), side=LEFT)

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

        def go_to_reporting(self, project, bug_handler):
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
                self.go_to_reporting(project, bug_handler)

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
        driver_handler = None

        small_img_size = (170, 130)
        img_size = (515, 530)

        def __init__(self, project, bug_handler, reported=False):
            super().__init__()

            if not bug_handler:
                raise ValueError
            else:
                self.bug_handler = bug_handler
            if not project and not Application.Reporting.selected_project:
                raise ValueError
            elif project:
                Application.Reporting.selected_project = project

            # Creates an instance of BugEntry for each line of the current bug
            current_bug = []
            for bug_line in self.bug_handler.get_current():
                current_bug.append(self.BugEntry(bug_line, self.bug_handler.try_get_image(bug_line)))

            self.already_reported = reported
            self.pack(fill=BOTH, expand=True)
            self.init_widgets(current_bug)

        def go_to_reported(self):
            self.pack_forget()
            last_bug = self.bug_handler.get_current()
            self.bug_handler.archive()
            app.reported = Application.ReportedScreen(self.bug_handler, last_bug)
            self.destroy()

        def show_next_report(self, archive):
            if archive:
                self.bug_handler.archive()
            self.bug_handler.read_next()
            if not self.bug_handler.get_current():
                go_to_main_menu(self)
                return
            self.pack_forget()
            app.reporting = Application.Reporting(
                Application.Reporting.selected_project, self.bug_handler, reported=True
            )
            self.destroy()

        def find_missing_image(self, image_label, bug_entry, try_again_button, find_img_button=None,
                               image_location_text=None):
            new_image_path = utils.find_image_path()
            self.bug_handler.set_image(bug_entry.line, new_image_path)
            bug_entry.reload_image(self.bug_handler)
            if image_location_text:
                image_location_text.insert(END, new_image_path)
            if find_img_button:
                find_img_button.get_element().pack_forget()
                find_img_button.get_element().destroy()
                image_retrieved = bug_entry.get_image()
            else:
                image_retrieved = bug_entry.get_small_image()
            image_retrieved.thumbnail(Application.Reporting.img_size)
            image_to_show = ImageTk.PhotoImage(image_retrieved)
            image_label.configure(image=image_to_show)
            image_label.image = image_to_show
            if try_again_button:
                try_again_button.get_element().pack_forget()
                try_again_button.get_element().destroy()

        def open_duplicates(self, bug_line, report_button):
            # if not self.driver_handler:
            #     self.driver_handler = DriverHandler(config.read_config("preferred browser"))
            # reporter.check_for_duplicates(
            #     config.read_config("mantis username"), "CrYVhn7FSM", bug_line,
            #     driver_handler=self.driver_handler
            # )
            report_button.get_element()['text'] = "REPORT"
            report_button.get_element()['command'] = self.go_to_reported
            # report_button.get_element()['command'] = lambda: self.open_report(bug_line)

        def open_report(self, bug_line):
            print(f"Reporting: {bug_line}")
            self.go_to_reported()

        def look_for_images_again(self, current_bug):
            self.bug_handler.try_images_again()
            for bug in current_bug:
                bug.reload_image(self.bug_handler)

        def update_image_thumbnails(self, current_bug, thumbnails, image_location_text, find_img_button,
                                    try_again_button):
            self.look_for_images_again(current_bug)
            for i in range(len(current_bug)):
                if i == 0:
                    image_to_show = ImageTk.PhotoImage(current_bug[i].get_image())
                else:
                    image_to_show = ImageTk.PhotoImage(current_bug[i].get_small_image())
                thumbnails[i].configure(image=image_to_show)
                thumbnails[i].image = image_to_show
            if current_bug[0].image_location:
                if find_img_button:
                    find_img_button.get_element().pack_forget()
                    find_img_button.get_element().destroy()
                image_location_text.insert(END, current_bug[0].image_location)
            if self.bug_handler.images_good() and try_again_button:
                try_again_button.get_element().pack_forget()
                try_again_button.get_element().destroy()

        class BugEntry:
            # Each line of current bug is represented by a line and an image as instances of this class
            line = None
            image = None
            image_location = None

            def __init__(self, line, image_location):
                self.line = line
                self.image = Image.open("./resources/image_not_found.png")
                self.image_location = image_location

            def get_image(self):
                temp_image = self.image
                temp_image.thumbnail(Application.Reporting.img_size)
                return temp_image

            def get_small_image(self):
                temp_image = copy.deepcopy(self.image)
                temp_image.thumbnail(Application.Reporting.small_img_size)
                return temp_image

            def reload_image(self, bug_handler):
                self.image_location = bug_handler.try_get_image(self.line)
                if self.image_location:
                    self.image = Image.open(self.image_location)

        def make_scrollable_canvas(self, frame, bug_len):
            # Here, a canvas is created to display the image thumbnails and allow for scrolling
            # Taken from https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
            thumbnail_canvas = Canvas(frame, bg=Application.color_theme[3], highlightthickness=0)
            thumbnail_canvas.grid(row=0, column=0, sticky="news")

            # Make a Scrollbar if there are more than 5 images (bug head and 4 extra)
            # TODO: Fix this, it doesn't want to scroll
            if bug_len > 5:
                sb = Scrollbar(frame, orient="vertical")
                sb.grid(row=0, column=1, sticky="ns")
                thumbnail_canvas.config(yscrollcommand=sb.set)
                sb.config(command=thumbnail_canvas.yview)

            # Use this thumbnail_frame to insert image thumbnails
            thumbnail_frame = Frame(thumbnail_canvas, bg=Application.color_theme[3])
            thumbnail_canvas.create_window((0, 0), window=thumbnail_frame, anchor="nw")

            image_labels = []
            for line_no in range(bug_len - 1):
                temp_img_label = Label(thumbnail_frame, bg=Application.color_theme[3])
                temp_img_label.place(x=0, y=0)
                temp_img_label.grid(row=line_no // 2, column=line_no % 2, sticky="news")
                image_labels.append(temp_img_label)

            thumbnail_canvas.config(scrollregion=thumbnail_frame.bbox("all"))
            return image_labels

        def make_options_sidebar(self, frame):
            # Make some widgets for the sidebar here
            pass

        def show_canvas(self, thumbnails_frame, options_frame, this_button, current_bug, image_labels,
                        image_location_text, image_path_button, try_again_button):
            options_frame.pack_forget()
            thumbnails_frame.pack()
            # This method oversees the transfer from bug options to image thumbnail preview
            if not self.bug_handler.images_good():
                try_again_button.get_element().pack(padx=10, pady=10, side=RIGHT)

            self.update_image_thumbnails(current_bug, image_labels, image_location_text, image_path_button,
                                         try_again_button)

            this_button.get_element()['text'] = "Report\noptions"
            this_button.get_element()['command'] = lambda: self.show_sidebar(
                    thumbnails_frame, options_frame, this_button, current_bug, image_labels, image_location_text,
                    image_path_button, try_again_button
                )

        def show_sidebar(self, thumbnails_frame, options_frame, this_button, current_bug, image_labels,
                         image_location_text, image_path_button, try_again_button):
            thumbnails_frame.pack_forget()
            options_frame.pack()
            if try_again_button:
                try_again_button.get_element().pack_forget()
            this_button.get_element()['text'] = "Image\npreview"
            this_button.get_element()['command'] = lambda: self.show_canvas(
                thumbnails_frame, options_frame, this_button, current_bug, image_labels, image_location_text,
                image_path_button, try_again_button
            )

        def init_widgets(self, current_bug):
            # region Frames
            background_frame = Frame(master=self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)
            version = find_version(Application.Reporting.selected_project[0])
            version_line = f"Reporting in project [{Application.Reporting.selected_project}] at version {version}"

            version_info_text = Text(background_frame, height=1, width=60, bg=Application.color_theme[4],
                                     fg=Application.color_theme[2], bd=0, font="Helvetica 12")
            version_info_text.pack(anchor="nw", pady=5, padx=5, side=TOP)
            version_info_text.insert(END, version_line)

            middle_frame = Frame(background_frame, bg=Application.color_theme[3])
            middle_frame.pack(anchor="center", pady=5, padx=15)

            current_bug_summary = self.bug_handler.get_current()[0][:-1]
            current_bug_text = Text(middle_frame, height=1, width=100, bg=Application.color_theme[3],
                                    fg=Application.color_theme[1], bd=0, font="Helvetica 13")
            current_bug_text.pack(side=TOP, fill=X, pady=5, padx=5)
            current_bug_text.insert(END, current_bug_summary)

            left_frame = Frame(middle_frame, bg=Application.color_theme[3])
            left_frame.pack(anchor="w", side=LEFT, pady=0, padx=10)
            right_frame = Frame(middle_frame, bg=Application.color_theme[3])
            right_frame.pack(anchor="e", side=RIGHT, fill=Y, padx=10)

            frame_for_canvas = Frame(right_frame, bg=Application.color_theme[3])  # Frame for the canvas
            frame_for_canvas.pack(side=TOP, pady=0, padx=0)
            frame_for_canvas.grid_columnconfigure(0, weight=1)
            frame_for_sidebar = Frame(right_frame, bg=Application.color_theme[3])  # Frame for the sidebar
            # These two frames will be filled and then alternated between in show_canvas and show_sidebar

            right_buttons_frame = Frame(right_frame, bg=Application.color_theme[3])
            right_buttons_frame.pack(side=BOTTOM, fill=X)
            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, fill=X)

            # All image labels are created here, they will be grid-placed into the thumbnail_frame
            # Except the first one, that is the bug head and gets the big preview
            image_labels = []  # Use this array to reference the labels and update them
            head_img_label = Label(left_frame, bg=Application.color_theme[3])
            head_img_label.place(x=0, y=0)
            head_img_label.pack(pady=0, padx=0, side=TOP)
            image_labels.append(head_img_label)
            image_location_text = Text(left_frame, height=1, width=60, bg=Application.color_theme[3],
                                       fg=Application.color_theme[1], bd=0, font="Helvetica 10")
            image_location_text.pack(anchor="s", pady=5, padx=5, side=BOTTOM)
            # The scrollable canvas is created here
            image_labels += self.make_scrollable_canvas(frame_for_canvas, len(current_bug))

            self.make_options_sidebar(frame_for_sidebar)

            # endregion Frames
            if self.already_reported:
                # If a report has been made already, it is not possible to go back to project selection
                # instead, this button will take the user to the main menu
                back_button = Application.AppButton(
                    'Main Menu', frame=bottom_frame, command=lambda: go_to_main_menu(self), side=LEFT)
            else:
                back_button = Application.AppButton(
                    'BACK', frame=bottom_frame, side=LEFT, command=lambda: go_to_projects(self, "normal")
                )
            report_options_button = Application.AppButton("Report\noptions", right_buttons_frame, side=RIGHT)

            if not current_bug[0].image_location:
                image_path_button = Application.AppButton("Find image", left_frame, side=BOTTOM)
            else:
                image_path_button = None

            if not self.bug_handler.images_good():
                try_again_button = Application.AppButton(
                    "Try again", right_buttons_frame, side=RIGHT,
                    command=lambda: self.update_image_thumbnails(current_bug, image_labels, image_location_text,
                                                                 image_path_button, try_again_button)
                )
            else:
                try_again_button = None

            report_options_button.get_element()['command'] = lambda: self.show_sidebar(
                frame_for_canvas, frame_for_sidebar, report_options_button, current_bug, image_labels,
                image_location_text, image_path_button, try_again_button
            )

            if image_path_button:
                image_path_button.get_element()['command'] = lambda: self.find_missing_image(
                    head_img_label, current_bug[0], try_again_button, image_path_button, image_location_text
                )

            self.update_image_thumbnails(current_bug, image_labels, image_location_text, image_path_button,
                                         try_again_button)
            # region Bottom
            button_find_duplicates = Application.AppButton(
                "Find\nduplicates", bottom_frame, side=RIGHT,
                # TODO: make new thread here? Else program is 'not responding' until search is complete
                command=lambda: self.open_duplicates(current_bug_summary, button_find_duplicates)
            )
            button_skip_report = Application.AppButton(
                "Don't report", bottom_frame, side=RIGHT, command=lambda: self.show_next_report(True)
            )
            button_skip_report = Application.AppButton(
                "Skip report", bottom_frame, side=RIGHT, command=lambda: self.show_next_report(False)
            )
            # endregion Bottom

    class ReportedScreen(Page):
        bug_handler = None
        last_bug = None

        def __init__(self, bug_handler, last_bug):
            super().__init__()

            self.last_bug = last_bug
            self.bug_handler = bug_handler
            self.pack(fill=BOTH, expand=True)
            self.init_widgets()

        def go_to_reporting(self):
            self.pack_forget()
            self.bug_handler.read_next()
            if self.bug_handler.get_current():
                app.reporting = Application.Reporting(None, bug_handler=self.bug_handler, reported=True)
            else:
                app.main_menu = Application.MainMenu()
            self.destroy()

        def init_widgets(self):
            background_frame = Frame(master=self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)
            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, fill=X)

            middle_frame = Frame(background_frame, bg=Application.color_theme[3])
            middle_frame.pack(anchor="center", pady=85, padx=15)

            current_bug_summary = self.last_bug[0][:-1]
            current_bug_text = Text(middle_frame, height=1, width=100, bg=Application.color_theme[3],
                                    fg=Application.color_theme[1], bd=0, font="Helvetica 13")
            current_bug_text.pack(side=TOP, pady=10, padx=10)
            current_bug_text.insert(END, current_bug_summary)

            reported_text = Entry(middle_frame, bg=Application.color_theme[3],
                                  fg=Application.color_theme[1], bd=0, font="Helvetica 30", justify=CENTER)
            reported_text.pack(anchor="n", pady=35, padx=35, side=TOP)
            reported_text.insert(0, f"Opened Mantis report")

            menu_button = Application.AppButton(
                'Main Menu', frame=bottom_frame, command=lambda: go_to_main_menu(self), side=LEFT)

            next_report_button = Application.AppButton(
                'Next Report', frame=middle_frame, command=self.go_to_reporting, side=TOP, font_size=20,
                offx=40, offy=30, text_spacing=25, color1=Application.color_theme[2]
            )

    class Batch(Page):
        def __init__(self, project):
            super().__init__()
            self.pack(fill=BOTH, expand=True)
            self.init_widgets()

        def init_widgets(self):
            background_frame = Frame(master=self, bg=Application.color_theme[4])
            background_frame.pack(fill=BOTH, expand=True)

            bottom_frame = Frame(background_frame, bg=Application.color_theme[4])
            bottom_frame.pack(side=BOTTOM, anchor="sw")
            back_button = Application.AppButton('BACK', frame=bottom_frame, anchor="sw",
                                                command=lambda: go_to_projects(self, "normal"))


def get_displayable_image(image_location):
    image = Image.open(image_location)
    image.thumbnail((530, 530))
    img_to_show = ImageTk.PhotoImage(image)
    return img_to_show


def go_to_projects(frame, use_mode):
    frame.pack_forget()
    app.projects_page = Application.SelectProject(use_mode)
    app.projects_page.open_page()
    frame.destroy()


def go_to_main_menu(frame):
    frame.pack_forget()
    app.main_menu = Application.MainMenu()
    frame.destroy()


def make_error_textbox(message, error_textbox):
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
