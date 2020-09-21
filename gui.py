import copy
import os
import subprocess
from collections import deque
from time import sleep
from tkinter import *
from tkinter import colorchooser
from tkinter.font import Font
from threading import Thread
from PIL import ImageTk, Image
from selenium.common.exceptions import SessionNotCreatedException, NoSuchWindowException, WebDriverException

from information_compile import determine_bug_category, extract_asset_name, extract_asset_path
from password import get_password
from versions import find_version
import bugs
import config
from config import get_theme
from gui_bughandler import BugHandler
from chromedrivers import DriverHandler, gui_login
from sector_seek import find_assign_to
from chromedrivers import log_into_mantis
import utils
import reporter
import gif_generator


custom_theme = None
version = "0.4.4"


class Application(Frame):
    # The first GUI element put in the basic Win window, important for layout, everything sits on this
    setup = None  # These represent the active frame. Only one should exist and others should be None
    main_menu = None  # We tried making just one variable current_frame instead of this
    settings_menu = None  # But it didn't work due to some methods not recognising that their frame is current
    projects_page = None  # So self didn't work properly
    reporting = None
    reported = None
    batch = None
    login = None
    gif_page = None

    # It's important to keep in mind the class instances above,
    # when gui is active, exactly one has to have a non Null value, because having more than one pages active
    # at the same time is BS

    password = None  # Mantis password is saved here
    current_color_theme = ""

    def __init__(self):
        super().__init__()

        config_path = "./config.cfg"
        if not os.path.isfile(config_path):
            config.ConfigHandler()
            self.current_color_theme = get_theme(config.read_config("current theme"))
            Application.current_color_theme = get_theme(config.read_config("current theme"))
            self.settings_menu = self.SettingsMenu(first_time=True)
            self.settings_menu.open_page()
            if self.current_color_theme == "":
                config.write_config("current theme", "ph")
        else:
            config.ConfigHandler()
            self.current_color_theme = get_theme(config.read_config("current theme"))
            Application.current_color_theme = get_theme(config.read_config("current theme"))
            self.main_menu = self.MainMenu()
            if config.read_config("save password") == "True":
                self.password = get_password()

    class Page(Frame):
        # All pages inherit from this class
        def open_page(self):
            self.pack(fill=BOTH, expand=True)

    class AppButton:
        # The basic template that is used for most buttons in the app
        # Create an instance of this class to quickly create a new button
        text = None
        element = None

        def __init__(self, text, frame, color1=None, color2=None, font_color='black', command=None,
                     offx=10, offy=10, font_size=15, text_spacing=20, side=None, pady=10, anchor=None):
            if color1 is None:
                color1 = Application.current_color_theme[0]
            if color2 is None:
                color2 = Application.current_color_theme[0]

            self.text = text
            # font_color = Application.current_color_theme[1]

            my_font = Font(size=font_size)
            button = Button(frame, text=text, height=1, width=8, bg=color1, activebackground=color2,
                            fg=font_color, padx=text_spacing, pady=pady, cursor='hand2')
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

        custom_colors = ['', '', '', '']
        theme_editor_exists = False  # for singleton behaviour

        def __init__(self):
            super().__init__()
            self.init_widgets()

        # region COMMANDS
        def go_to_settings(self, first_time=False):
            # ACHTUNG! When you annul an instance of a page class, remember to create
            # a new one of a different page class as following:
            self.pack_forget()
            app.settings_menu = Application.SettingsMenu(first_time=first_time)
            app.settings_menu.open_page()
            app.main_menu = None

        def go_to_projects(self, use_mode):
            app.password = get_password()
            if app.password is None or app.password == '':
                self.pack_forget()
                app.login = Application.Login(use_mode, fail=False)
                app.main_menu = None
            else:
                self.pack_forget()
                app.projects_page = Application.SelectProject(use_mode)
                app.projects_page.open_page()
                app.main_menu = None

        def go_to_gif_generator(self):
            self.pack_forget()
            app.gif_page = gif_generator.GifGeneratorPage(
                app=app, location=config.read_config("edited images location"))
            app.main_menu = None
        # endregion

        class ThemeOption:
            theme_name = None
            button = None

            def __init__(self, theme, master, row, pady=5):
                super().__init__()
                self.pady = pady
                self.theme_name = theme
                self.build_button(master, row)

            def destroy(self):
                self.button.destroy()

            def _on_click(self, _):
                app.current_color_theme = get_theme(self.theme_name)
                Application.current_color_theme = get_theme(self.theme_name)
                config.write_config('current theme', self.theme_name)
                app.main_menu.go_to_settings()
                app.settings_menu.go_to_main_menu()

            def build_button(self, master, row):
                button = Button(master=master, width=15, cursor='hand2')
                button['state'] = DISABLED
                button['relief'] = RAISED

                self.button = button
                color_theme = get_theme(theme=self.theme_name)
                for i in range(4):
                    label = Label(button, bg=color_theme[i], width=3, state=DISABLED)
                    label.bind('<Button-1>', self._on_click)
                    label.grid(column=i, row=0)

                button.grid(column=0, row=row, pady=self.pady, padx=10)
                return button

        def configure_custom_theme(self, theme_button, themes_frame):
            if self.theme_editor_exists:
                return
            self.theme_editor_exists = True
            self.custom_colors = config.get_custom_theme()
            custom_theme_root = Tk()
            custom_theme_root.geometry('250x300')
            custom_theme_root.minsize(width=250, height=300)
            custom_theme_root.maxsize(width=250, height=300)
            custom_theme_root.resizable(0, 0)
            custom_theme_root.wm_iconbitmap('.//resources/icon.ico')
            custom_theme_root.wm_title('Themes')
            background = Frame(master=custom_theme_root, bg=Application.current_color_theme[3])
            background.pack(fill=BOTH, expand=True)

            top_frame = Frame(master=background, bg=Application.current_color_theme[2], pady=10, padx=10)
            top_frame.pack(side=TOP, padx=20, pady=20, fill=BOTH)

            color_entries = []
            color_types = ['Buttons', 'Text', 'Frames', 'Background']
            for i in range(4):
                color_text = Label(master=top_frame, bg=Application.current_color_theme[2],
                                   fg=Application.current_color_theme[1], text=color_types[i] + ': ')
                color_text.grid(column=0, row=i, sticky=W, pady=10)
                color_entry = Entry(master=top_frame, width=10, bg=Application.current_color_theme[2],
                                    fg=Application.current_color_theme[1])
                color_entry.insert(0, self.custom_colors[i])
                color_entry.grid(column=1, row=i, sticky=W, pady=10)
                color_button = Button(
                    master=top_frame, bg=Application.current_color_theme[0], fg='#000000',
                    text="Pick", command=lambda ci=i, e=color_entry: self.choose_color(
                        ci, e, custom_theme_root)
                )
                color_button.grid(column=2, row=i, pady=10, padx=5)
                color_entries.append(color_entry)

            submit_button = Button(master=top_frame, text='Submit', bg=Application.current_color_theme[0],
                                   command=lambda: self.confirm_color(
                                       custom_theme_root, theme_button, themes_frame, color_entries),
                                   fg='#000000')
            submit_button.grid(column=0, row=10, pady=10)
            custom_theme_root.mainloop()

        def choose_color(self, color_index, entry, rt):
            color = colorchooser.askcolor()[1]
            rt.lift()  # This moves the window on top of the main app
            if not color:
                color = ''
            self.custom_colors[color_index] = color
            entry.delete(0, END)
            entry.insert(0, self.custom_colors[color_index])

        def confirm_color(self, rt, theme_button, themes_frame, entries):
            self.theme_editor_exists = False
            theme_button.destroy()
            for i in range(len(self.custom_colors)):
                if self.custom_colors[i] == "":
                    self.custom_colors[i] = "#ffffff"
            for i in range(len(entries)):
                if utils.is_hex_color(entries[i].get()):
                    self.custom_colors[i] = entries[i].get()
            new_theme_str = self.custom_colors[0]
            for color in self.custom_colors[1:]:
                new_theme_str += f";{color}"
            config.write_config("custom theme", new_theme_str)
            rt.destroy()
            new_custom_theme = self.ThemeOption('custom', master=themes_frame, row=9, pady=20)
            Application.current_color_theme = get_theme(config.read_config('current theme'))
            app.main_menu.go_to_settings()
            app.settings_menu.go_to_main_menu()

        @staticmethod
        def refresh_counter(ats_text, ets_text):
            try:
                ats_new_count = str(bugs.count_bugs('ats'))
            except FileNotFoundError:
                ats_new_count = 'N/A'
            try:
                ets_new_count = str(bugs.count_bugs('ets'))
            except FileNotFoundError:
                ets_new_count = 'N/A'
            ats_text['state'] = NORMAL
            ets_text['state'] = NORMAL
            ats_text.delete("1.0", END)
            ats_text.insert("1.0", f"ATS: {ats_new_count}", "center")
            ets_text.delete("1.0", END)
            ets_text.insert("1.0", f"ETS 2: {ets_new_count}", "center")
            ats_text['state'] = DISABLED
            ets_text['state'] = DISABLED

        def set_up_menu(self):
            try:  # Handles the variables needed for the bug counter for ATS
                ats_bugs_count = bugs.count_bugs("ats")
            except FileNotFoundError:
                ats_bugs_count = 'N/A'
            try:  # Same but for ETS
                ets_bugs_count = bugs.count_bugs("ets")
            except FileNotFoundError:
                ets_bugs_count = 'N/A'

            background_frame = Frame(self, bg=Application.current_color_theme[3])
            background_frame.pack(fill=BOTH, expand=True)

            top_frame = Frame(background_frame, bg=Application.current_color_theme[3])
            top_frame.pack(side=TOP, fill=X)

            color_button_frame = Frame(top_frame, bg=Application.current_color_theme[3])
            color_button_frame.pack(side=RIGHT, fill=Y, padx=30, pady=30)

            theme_selection_frame = Frame(color_button_frame, bg=Application.current_color_theme[2])
            theme_selection_frame.pack()

            for index, color_theme in enumerate(get_theme('all')):
                if color_theme != 'custom':
                    theme_option = self.ThemeOption(color_theme, master=theme_selection_frame, row=index)
            custom_theme_option = self.ThemeOption('custom', master=theme_selection_frame, row=index, pady=20)

            custom_theme_button = Button(
                master=theme_selection_frame, text='Custom Theme', cursor='hand2',
                command=lambda: self.configure_custom_theme(custom_theme_option, theme_selection_frame),
                bg=Application.current_color_theme[0], fg='#000000')
            custom_theme_button.grid(column=0, row=10, pady=10)

            left_frame = Frame(top_frame, bg=Application.current_color_theme[2])
            left_frame.pack(expand=False, fill=Y, side=LEFT, pady=10, padx=30)

            title_font = "Helvetica 20 bold"
            title = Label(left_frame, text='TSReporter',
                          bg=Application.current_color_theme[3], font=title_font, padx=17, pady=5,
                          fg=Application.current_color_theme[1])
            title.pack(side=TOP)

            report_button = Application.AppButton('Report Bugs', frame=left_frame,
                                                  command=lambda: self.go_to_projects("normal"))
            # batch_report_button = Application.AppButton('Batch Report \n (WIP)', frame=left_frame,
            #                                             command=lambda: self.go_to_projects("batch"))

            gif_button = Application.AppButton('GIF\nGenerator', frame=left_frame, command=self.go_to_gif_generator)
            settings_button = Application.AppButton('Settings', frame=left_frame,
                                                    command=self.go_to_settings)

            # This is only for creating the gap between regular buttons and the quit button
            placeholder_frame = Frame(left_frame, bg=Application.current_color_theme[2])
            placeholder_frame.pack(fill=BOTH, pady=70)

            quit_button = Application.AppButton('QUIT', color1=Application.current_color_theme[1],
                                                color2=Application.current_color_theme[1],
                                                frame=left_frame, command=sys.exit)

            # region BUG COUNTER
            bugs_count_frame = Frame(top_frame, bg=Application.current_color_theme[2])
            bugs_count_frame.pack(side=TOP, pady=10)
            subtitle_font = Font(size=15)
            reports_count_text = Label(bugs_count_frame, text=f'Number of bugs in bugs.txt',
                                       bg=Application.current_color_theme[3],
                                       fg=Application.current_color_theme[1], font=subtitle_font)

            reports_count_text.pack()

            ats_bugs_counter = Text(bugs_count_frame, width=10, height=1, borderwidth=0,
                                    bg=Application.current_color_theme[2],
                                    fg=Application.current_color_theme[1], font=subtitle_font)
            ats_bugs_counter.tag_configure("center", justify="center")
            ats_bugs_counter.insert(END, f'ATS: {ats_bugs_count}', "center")
            ats_bugs_counter['state'] = DISABLED
            ats_bugs_counter.pack()

            ets2_bugs_counter = Text(bugs_count_frame, width=10, height=1, borderwidth=0,
                                     bg=Application.current_color_theme[2],
                                     fg=Application.current_color_theme[1], font=subtitle_font)
            ets2_bugs_counter.tag_configure("center", justify="center")
            ets2_bugs_counter.insert(END, f'ETS 2: {ets_bugs_count}', "center")
            ets2_bugs_counter['state'] = DISABLED
            ets2_bugs_counter.pack()

            refresh_button = Application.AppButton(frame=top_frame, text="Refresh", font_size=10,
                                                   pady=2, offy=1, text_spacing=1,
                                                   command=lambda: self.refresh_counter(
                                                       ats_text=ats_bugs_counter,
                                                       ets_text=ets2_bugs_counter)
                                                   )
            # endregion

            bottom_frame = Frame(background_frame, bg=Application.current_color_theme[3])
            bottom_frame.pack(side=BOTTOM, fill=X)

            img = ImageTk.PhotoImage(Image.open("./resources/logo.png"))
            img_panel = Label(top_frame, image=img, bg=Application.current_color_theme[3])
            img_panel.image = img
            img_panel.place(x=0, y=0)
            img_panel.pack(pady=100, side=BOTTOM)

            version_label = Label(bottom_frame, text=version,
                                  bg=Application.current_color_theme[3],
                                  fg=Application.current_color_theme[1])
            version_label.pack(side=RIGHT)

        def init_widgets(self):
            self.pack(fill=BOTH, expand=True)
            self.set_up_menu()

    class Login(Page):
        current_mode = None
        entered_password = None
        logged_in = False
        logging_in_process = False
        fail = None

        def __init__(self, use_mode, fail):
            super().__init__()
            self.fail = fail
            self.init_widgets()
            self.current_mode = use_mode
            self.pack(fill=BOTH, expand=True)

        class LoginThread(Thread):
            login_frame = None

            def __init__(self, login_frame):
                super().__init__()
                self.login_frame = login_frame

            def run(self):
                app.login.logging_in_process = True
                animation_thread = app.login.LoginAnimation(self.login_frame.master)
                animation_thread.start()
                successfully_logged_in = gui_login(username=config.read_config('mantis username'),
                                                   password=app.login.entered_password)
                app.login.logged_in = successfully_logged_in
                if successfully_logged_in:
                    app.password = app.login.entered_password
                app.login.logging_in_process = False
                app.login.pack_forget()
                if successfully_logged_in:
                    app.login.go_to_projects()
                else:
                    app.login = Application.Login(app.login.current_mode, fail=True)
                    app.login.open_page()

        class LoginAnimation(Thread):
            master = None

            def __init__(self, master):
                super().__init__()
                self.master = master

            def run(self):
                loading_text = Label(self.master, bg=Application.current_color_theme[3],
                                     fg=Application.current_color_theme[1], font=Font(size=15))
                while app.login and app.login.logging_in_process:
                    loading_text['text'] = 'Logging in'
                    loading_text.pack(expand=True)
                    sleep(0.5)
                    for i in range(3):
                        loading_text['text'] += '.'
                        sleep(0.5)

        def try_log_in(self, text_field, login_frame):
            self.entered_password = text_field.get()
            login_frame.pack_forget()
            self.LoginThread(login_frame).start()

        def go_to_projects(self):
            self.pack_forget()
            app.projects_page = Application.SelectProject(self.current_mode)
            app.projects_page.open_page()
            app.login = None

        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            app.login = None

        def create_login_interface(self, main_background):
            login_border = Frame(main_background, bg=Application.current_color_theme[1], pady=10, padx=10)
            login_border.pack(expand=True)

            login_frame = Frame(login_border, bg=Application.current_color_theme[2], pady=10, padx=10)
            login_frame.pack(expand=True)

            login_text = Label(master=login_frame, bg=Application.current_color_theme[2],
                               fg=Application.current_color_theme[1], font=Font(size=13))
            if not self.fail:
                login_text['text'] = "Please enter your Mantis password:"
            else:
                login_text['text'] = "Invalid password or username..."
            login_text.pack(pady=5)

            password_entry = Entry(login_frame, width=25, bg=Application.current_color_theme[0], font=Font(size=16), show="*")
            password_entry.pack(padx=10)

            login_button = Application.AppButton(
                frame=login_frame, text="LOGIN", command=lambda password_entry=password_entry: self.try_log_in(
                    text_field=password_entry, login_frame=login_border))

            root.bind('<Return>',
                      lambda x: self.try_log_in(text_field=password_entry, login_frame=login_border))

        def init_widgets(self):
            main_background = Frame(master=self, bg=Application.current_color_theme[3])
            main_background.pack(fill=BOTH, expand=True)

            if app.password is None or app.password == '':
                self.create_login_interface(main_background)
                bottom_frame = Frame(main_background, bg=Application.current_color_theme[3])
                bottom_frame.pack(fill=X, expand=False, side=BOTTOM)
                button = Application.AppButton('Main Menu', frame=bottom_frame,
                                               command=self.go_to_main_menu, side=LEFT)
            else:
                self.go_to_projects()

    class SettingsMenu(Page):
        # The settings page where you can change, you guessed it, settings! AKA former config
        first_time = False
        dialog_activated = False

        def __init__(self, first_time=False):
            super().__init__()
            self.first_time = first_time
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

                setting_name_frame = Frame(background, bg=Application.current_color_theme[2])
                setting_name_frame.grid(row=row, column=0, sticky=W + E + N + S, pady=5)

                value_frame = Frame(background, bg=Application.current_color_theme[2])
                value_frame.grid(row=row, column=1, sticky=W + E + N + S, pady=5, padx=10)

                button_frame = Frame(background, bg=Application.current_color_theme[3])
                button_frame.grid(row=row, column=2, padx=10, sticky=W + E + N + S, pady=10)

                setting_name_frame_packed = Frame(setting_name_frame)

                left_frame = Frame(setting_name_frame, bg=Application.current_color_theme[2])
                left_frame.pack(fill=X, side=TOP)
                frame_text = Label(left_frame, text=text,
                                   font=subtitle_font,
                                   fg=Application.current_color_theme[1],
                                   bg=Application.current_color_theme[2],
                                   pady=5, padx=10)
                frame_text.pack(side=LEFT)

                key_to_find = text.lower().split(':')[0]
                directory_path = str(config.read_config(key_to_find))

                span_frame = Frame(value_frame, bg=Application.current_color_theme[2])
                span_frame.pack(fill=X, side=TOP, padx=250)

                directory_value_frame = Frame(value_frame, bg=Application.current_color_theme[2])
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
                                        fg=Application.current_color_theme[1],
                                        bg=Application.current_color_theme[2],
                                        pady=5, padx=10)

                directory_value.pack(side=LEFT, fill=BOTH)
                if include_button:
                    directory_button_frame = Frame(button_frame, bg=Application.current_color_theme[2])
                    directory_button_frame.pack(fill=X, side=TOP)
                    directory_button = Button(directory_button_frame, text=button_text,
                                              bg=Application.current_color_theme[0],
                                              activebackground=Application.current_color_theme[0])
                    if command is None:
                        directory_button['command'] = lambda: self.ask_for_directory(row)
                    else:
                        directory_button['command'] = command

                    directory_button.pack(side=RIGHT)

            def ask_for_directory(self, index):
                config.ConfigHandler.gui_config_edit(index)
                first_time = app.settings_menu.first_time
                app.settings_menu.go_to_main_menu()
                app.main_menu.go_to_settings(first_time=first_time)
        # region COMMANDS

        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            app.settings_menu = None

        def submit(self, text_input):
            username = text_input.get()
            config.ConfigHandler.gui_config_edit(3, entered_text=username)
            self.go_to_main_menu()
            app.main_menu.go_to_settings(first_time=self.first_time)

        def show_text_input(self, master):
            if not self.dialog_activated:
                self.dialog_activated = True
                text_input = Entry(master, bg=Application.current_color_theme[2], fg=Application.current_color_theme[1], width=25,
                                   font=Font(size=20))
                text_input.pack()
                submit_button = Button(master, bg=Application.current_color_theme[2], fg=Application.current_color_theme[1],
                                       text='Submit',
                                       command=lambda: self.submit(text_input))
                root.bind('<Return>', lambda x: self.submit(text_input))
                submit_button.pack(pady=5)

        def ask_yes_no(self, master, setting):
            if not self.dialog_activated:
                self.dialog_activated = True
                buttons_frame = Frame(master, bg=Application.current_color_theme[2])
                buttons_frame.pack(pady=10)

                reported_text = Entry(buttons_frame, bg=Application.current_color_theme[2],
                                      fg=Application.current_color_theme[1], bd=0, font="Helvetica 14", justify=CENTER)
                reported_text.pack(anchor="n", pady=5, padx=5, side=TOP)
                reported_text.insert(0, setting.capitalize() + "?")

                yes_button = Application.AppButton(
                    "Yes", buttons_frame, side=LEFT, text_spacing=0, pady=0, font_size=12,
                    command=lambda: self.submit_yes_no(True, 5)
                )
                no_button = Application.AppButton(
                    "No", buttons_frame, side=RIGHT, text_spacing=0, pady=0, font_size=12,
                    command=lambda: self.submit_yes_no(False, 5)
                )

        def submit_yes_no(self, yes_no, index):
            config.ConfigHandler().gui_config_edit(index=index, yes_no_value=yes_no)
            self.go_to_main_menu()
            app.main_menu.go_to_settings(first_time=self.first_time)

        def show_browser_selection(self, master):
            if not self.dialog_activated:
                self.dialog_activated = True
                options = ["Chrome", "Firefox"]
                frame = Frame(master, bg=Application.current_color_theme[2], padx=10, pady=10)
                frame.pack()
                dialog_text = Label(master=frame, text="Select your preferred browser", font=Font(size=10),
                                    bg=Application.current_color_theme[2], fg=Application.current_color_theme[1])
                dialog_text.pack(side=TOP)
                for i in range(len(options)):
                    option_to_process = options[i].lower()
                    button = Application.AppButton(frame=frame, text=options[i], offx=5, offy=5, side=LEFT,
                                                   command=lambda option=option_to_process:
                                                   self.submit_browser_selection(option),
                                                   text_spacing=2, pady=2, font_size=10)
                    button.get_element().pack()

        def submit_browser_selection(self, chosen_browser):
            config.ConfigHandler().gui_config_edit(index=4, browser_chosen=chosen_browser)
            self.go_to_main_menu()
            app.main_menu.go_to_settings(first_time=self.first_time)
        # endregion

        def init_widgets(self):
            template_background = Frame(self, bg=Application.current_color_theme[3])
            template_background.pack(fill=BOTH, expand=True)

            background = Frame(template_background, bg=Application.current_color_theme[3])
            background.pack(fill=BOTH, expand=True, padx=10, pady=10)

            if self.first_time:
                warning_text = Label(background, bg=Application.current_color_theme[3], fg=Application.current_color_theme[1], font=Font(size=20))
                warning_text['text'] = "FIRST TIME SETUP"
                warning_text.pack()

            subbackground = Frame(background, bg=Application.current_color_theme[3])
            subbackground.pack(fill=Y, expand=False, padx=10, pady=10)

            grid_i = 0
            for setting in config.ConfigHandler.config_layout.keys():
                if "secret" in config.ConfigHandler.config_layout[setting]:
                    continue
                elif config.ConfigHandler.config_layout[setting] == "text":
                    self.SettingsOption(subbackground, parent_frame=self, row=grid_i, text=f'{setting.capitalize()}: ',
                                        command=lambda: self.show_text_input(background))
                elif config.ConfigHandler.config_layout[setting] == "yn":
                    self.SettingsOption(
                        background=subbackground, parent_frame=self, row=grid_i, text=f'{setting.capitalize()}: ',
                        command=lambda s=setting: self.ask_yes_no(background, s)
                    )
                elif config.ConfigHandler.config_layout[setting] == "browser":
                    self.SettingsOption(
                        background=subbackground, parent_frame=self, row=grid_i, text=f'{setting.capitalize()}: ',
                        command=lambda s=setting: self.show_browser_selection(master=background)
                    )
                else:
                    self.SettingsOption(
                        parent_frame=self, background=subbackground, row=grid_i, text=f'{setting.capitalize()}: '
                    )
                grid_i += 1

            button = Application.AppButton('Main Menu', frame=template_background,
                                           command=self.go_to_main_menu, side=LEFT)

            if self.first_time:
                button.get_element()["text"] = "Done"

    class SelectProject(Page):
        use_mode = None

        def __init__(self, use_mode):
            super().__init__()

            # use_mode determines if this screen will take the user to normal or batch reporting screen
            self.use_mode = use_mode
            self.init_widgets()

        # region COMMANDS
        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            app.projects_page = None

        def go_to_reporting(self, project, bug_handler):
            self.pack_forget()
            app.reporting = Application.Reporting(project, bug_handler=bug_handler)
            app.projects_page = None

        def go_to_batch(self, project):
            self.pack_forget()
            app.batch = Application.Batch(project)
            app.projects_page = None

        def try_going_duplicates(self, project, frame):
            bug_handler = BugHandler(project[0])
            if not bug_handler.get_current():
                rewrite_textbox(bug_handler.message, frame)
            else:
                self.go_to_reporting(project, bug_handler)
        # endregion

        def init_widgets(self):
            background = Frame(self, bg=Application.current_color_theme[3])
            background.pack(fill=BOTH, expand=True)

            error_frame = Frame(background, bg=Application.current_color_theme[3])
            error_frame.pack(side=TOP, anchor="n")
            error_textbox = Text(error_frame, height=1, width=80, bg=Application.current_color_theme[3],
                                 fg=Application.current_color_theme[1], bd=0, font="Helvetica 12")
            error_textbox.pack(pady=0, padx=0, side=TOP, anchor='n')
            error_textbox.configure(state=DISABLED)

            bottom_frame = Frame(background, bg=Application.current_color_theme[3])
            bottom_frame.pack(side=BOTTOM, anchor="sw")

            back_button = Application.AppButton('Main Menu', frame=bottom_frame, command=self.go_to_main_menu,
                                                anchor="sw")

            middle_frame = Frame(background, bg=Application.current_color_theme[3])
            middle_frame.pack(anchor="center", pady=70)

            buttons_ats_background = Frame(middle_frame, bg=Application.current_color_theme[1])
            buttons_ats_background.pack(padx=30, pady=30, side=LEFT)

            buttons_ats_frame = Frame(buttons_ats_background, bg=Application.current_color_theme[2])
            buttons_ats_frame.pack(side=LEFT, padx=5, pady=5)

            buttons_ets_background = Frame(middle_frame, bg=Application.current_color_theme[1])
            buttons_ets_background.pack(padx=30, pady=30, side=RIGHT)

            buttons_ets_frame = Frame(buttons_ets_background, bg=Application.current_color_theme[2])
            buttons_ets_frame.pack(side=LEFT, padx=5, pady=5)

            buttons = []
            ats_projects = ['ATS - INTERNAL', 'ATS - PUBLIC', 'ATS - PUBLIC - SENIORS']
            ets_projects = ['ETS 2 - INTERNAL', 'ETS 2 - PUBLIC', 'ETS 2 - PUBLIC - SENIORS']

            for i in range(len(ats_projects)):
                this_button = Application.AppButton(text=ats_projects[i], frame=buttons_ats_frame,
                                                    font_size=15, text_spacing=85, pady=7)
                if self.use_mode == "batch":
                    this_button.get_element()['command'] = lambda c=i: self.go_to_batch(ats_projects[c])
                else:
                    this_button.get_element()['command'] = lambda c=i: self.try_going_duplicates(ats_projects[c],
                                                                                                 error_textbox)
                buttons.append(this_button)

            for i in range(len(ets_projects)):
                this_button = Application.AppButton(text=ets_projects[i], frame=buttons_ets_frame,
                                                    font_size=15, text_spacing=85, pady=7)
                if self.use_mode == "batch":
                    this_button.get_element()['command'] = lambda c=i: self.go_to_batch(ets_projects[c])
                else:
                    this_button.get_element()['command'] = lambda c=i: self.try_going_duplicates(ets_projects[c],
                                                                                                 error_textbox)
                buttons.append(this_button)

    class Reporting(Page):
        selected_project = None
        already_reported = None  # decides if button is 'BACK' or 'Main menu'

        bug_handler = None
        driver_handler = None  # Holds the driver instance

        # These are used for the menus in report options
        severity_var = None
        priority_var = None

        bug_priority = None

        small_img_size = (160, 100)  # Size, to which the BugEntry thumbnails its images
        img_size = (520, 315)

        late_image = None
        category = None
        text_input_frame = None

        dialog_activated = False
        asset_path_input = None

        remember_prefix = False
        rename_images = False

        prefix_box = None
        prefix_check_button = None
        prefix = None
        bug_preview = None

        rename_box = None
        head_img_label = None

        def __init__(self, project, bug_handler, reported=False, prefix=None, last_time_rename_checked=False):
            super().__init__()
            self.rename_images = last_time_rename_checked
            if prefix:
                self.prefix = prefix
            else:
                prefix = ''
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

            self.bug_in_process = current_bug
            self.category = determine_bug_category(current_bug[0].line)

            self.already_reported = reported
            self.pack(fill=BOTH, expand=True)
            self.init_widgets(current_bug)
            if prefix:
                self.prefix_box.delete(0, END)
                self.prefix_box.insert(END, prefix)
                self.prefix_check_button.select()
                self.remember_prefix = True

        def go_to_reported(self):
            self.pack_forget()
            last_bug = self.bug_handler.get_current()
            saved_report = deque(last_bug)
            self.bug_handler.archive()  # Must archive before moving on to next screen
            prefix = self.prefix_box.get()
            app.reported = Application.ReportedScreen(self.bug_handler, saved_report, self.bug_handler.get_current(),
                                                      prefix=prefix, remember_prefix=self.remember_prefix,
                                                      remember_rename=self.rename_images)
            app.reporting = None

        def update_preview(self):
            if app.reporting:
                self.prefix = self.prefix_box.get()
                opt_prefix = ''
                opt_asset = ''
                if self.prefix:
                    if self.prefix not in ['Enter prefix', '']:
                        opt_prefix = f"{self.prefix} - "

                if self.asset_path_input:
                    if self.asset_path_input.get() not in ['Enter asset path/debug info', '']:
                        if 'DEBUG INFO' in self.asset_path_input.get():
                            opt_asset = f"{extract_asset_name(extract_asset_path(self.asset_path_input.get()))} - "
                        else:
                            opt_asset = f"{extract_asset_name(self.asset_path_input.get())} - "
                current = self.bug_handler.get_current()[0][:-1]
                current = current.split(';')[0]

                category = ''
                if '_' in current:
                    category = f"{current.split('_')[0]}_"
                    current = current.split('_')[1]

                if 'a' in category:
                    opt_prefix = ""

                game_version = find_version(Application.Reporting.selected_project[0])

                current_bug_summary = f"Preview: {game_version} - {opt_prefix}{opt_asset}{current}"
                rewrite_textbox(current_bug_summary, self.bug_preview)

        def show_text_input_asset_path(self, master):
            if not self.dialog_activated:
                self.dialog_activated = True

                asset_info_text = Text(master, font=Font(size=12), bg=Application.current_color_theme[2],
                                       bd=0, height=1,
                                       width=10, fg=app.current_color_theme[2])
                asset_info_text.grid(row=0, column=0)
                asset_info_text.insert(END, "Asset Path")
                asset_info_text.configure(state=DISABLED)

                text_input = Entry(master, bg=Application.current_color_theme[2],
                                   fg=Application.current_color_theme[1], width=25,
                                   font=Font(size=10))
                text_input.grid(row=0, column=1)
                text_input.insert(END, "Enter asset path/debug info")
                text_input.bind('<Button-1>', lambda x: Application.Reporting.clear_text_box(text_input))
                text_input.bind('<KeyRelease>', lambda x: self.update_preview())
                self.asset_path_input = text_input

        def show_prefix_input(self, master):
            asset_info_text = Label(master, font=Font(size=12), bg=Application.current_color_theme[2],
                                    bd=0, height=1, text="Prefix",
                                    width=10, fg=app.current_color_theme[1])
            if self.category == 'm':
                asset_info_text.grid(row=4, column=0)
            # asset_info_text.insert(END, "Prefix")
            # asset_info_text.configure(state=DISABLED)
            text_input = Entry(master, bg=Application.current_color_theme[2],
                               fg=Application.current_color_theme[1], width=25,
                               font=Font(size=10))
            if self.category == 'm':
                text_input.grid(row=4, column=1, pady=10)
            text_input.insert(END, "Enter prefix")
            text_input.bind('<Button-1>', lambda x: Application.Reporting.clear_text_box(text_input))
            text_input.bind('<KeyRelease>', lambda x: self.update_preview())
            self.prefix_box = text_input

        def show_rename_images_input(self, master):
            rename_images_text = Text(master, font=Font(size=12), bg=Application.current_color_theme[2],
                                      bd=0, height=1,
                                      width=10, fg=app.current_color_theme[1])
            rename_images_text.grid(row=6, column=0)
            rename_images_text.insert(END, "Rename img")
            rename_images_text.configure(state=DISABLED)
            text_input = Entry(master, bg=Application.current_color_theme[2],
                               disabledbackground=Application.current_color_theme[3],
                               fg=Application.current_color_theme[1], width=25,
                               font=Font(size=10))
            text_input.grid(row=6, column=1, pady=10)
            text_input.insert(END, "Bug Summary (Default)")
            text_input.bind('<Button-1>', lambda x: Application.Reporting.clear_text_box(text_input))
            self.rename_box = text_input
            if not self.rename_images:
                text_input['state'] = DISABLED

        def submit_asset_info(self):
            if self.asset_path_input.get() != "Enter asset path/debug info":
                reporter.asset_path = self.asset_path_input.get()

        def go_to_main_menu(self):
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            app.reporting = None

        def go_to_projects(self, use_mode):
            self.pack_forget()
            app.projects_page = Application.SelectProject(use_mode)
            app.projects_page.open_page()
            app.reporting = None

        def show_next_report(self, archive):
            if archive:
                self.bug_handler.archive()
                self.bug_handler.read_next()
            else:
                self.bug_handler.read_next(archive_comments=False)
            if not self.bug_handler.get_current():
                self.go_to_main_menu()
                return
            self.pack_forget()
            if self.remember_prefix and self.prefix:
                app.reporting = Application.Reporting(
                    Application.Reporting.selected_project, self.bug_handler, reported=True,
                    prefix=self.prefix, last_time_rename_checked=self.rename_images
                )
            else:
                app.reporting = Application.Reporting(
                    Application.Reporting.selected_project, self.bug_handler, reported=True,
                    last_time_rename_checked=self.rename_images
                )

        def find_missing_image(self, bug_entry, try_again_button, find_img_button=None,
                               image_location_text=None):
            try:
                new_image_path = utils.find_image_path()
                self.bug_handler.set_image(bug_entry.line, new_image_path)
                bug_entry.reload_image(self.bug_handler)

                if image_location_text:
                    image_location_text.insert(END, new_image_path)
                    image_location_text.configure(state=DISABLED)
                    image_location_text.pack(anchor="s", pady=5, padx=5, side=BOTTOM)
                if find_img_button:
                    find_img_button.get_element().pack_forget()
                    find_img_button.get_element().destroy()
                    image_retrieved = bug_entry.get_image()
                else:
                    image_retrieved = bug_entry.get_small_image()
                image_retrieved.thumbnail(Application.Reporting.img_size)
                image_to_show = ImageTk.PhotoImage(image_retrieved)
                self.head_img_label.configure(image=image_to_show)
                self.head_img_label.image = image_to_show
                if try_again_button and self.bug_handler.images_good():
                    try_again_button.get_element().pack_forget()
                    try_again_button.get_element().destroy()
                    self.duplicates_button.get_element()['font'] = Font(size=15)

                self.late_image = new_image_path
            except (TclError, ValueError):
                pass

        class DuplicatesThread(Thread):
            # Threading duplicates search happens here
            bug_line = None

            def __init__(self, bug_line):
                super().__init__()
                self.bug_line = bug_line

            def run(self):
                app.reporting.open_duplicates(bug_line=self.bug_line)

        def open_duplicates(self, bug_line):
            asset_path = None
            if self.category == 'a' and self.asset_path_input.get() not in ["Enter asset path/debug info", ""]:
                self.submit_asset_info()
                asset_path = self.asset_path_input.get()
            try:
                if not self.driver_handler:
                    self.driver_handler = DriverHandler(config.read_config("preferred browser"))
                reporter.check_for_duplicates(
                    config.read_config("mantis username"), app.password, bug_line,
                    driver_handler=self.driver_handler, a_path=asset_path
                )
            except (SessionNotCreatedException, NoSuchWindowException, WebDriverException, AttributeError,
                    TypeError, NameError):
                self.driver_handler = None

        class ReportingThread(Thread):
            bug_line = None

            def __init__(self, bug_line):
                super().__init__()
                self.bug_line = bug_line

            def run(self):
                app.reporting.open_report()

        def open_report(self):
            # This is called when the 'Report' button is pressed, reporting will happen starting here
            prefix = None

            if self.prefix_box.get() not in ["Enter prefix", ""]:
                prefix = self.prefix_box.get()

            if self.category == 'a' and self.asset_path_input.get() not in ["Enter asset path/debug info", ""]:
                self.submit_asset_info()
                reporter.asset_path = self.asset_path_input.get()

            game = self.selected_project[0]
            game_version = find_version(game=game)
            current_bug_deque = self.bug_handler.get_current()

            username = config.read_config('mantis username')
            priority = self.priority_var.get().lower()
            severity = self.severity_var.get().lower()

            if not self.driver_handler:
                self.driver_handler = DriverHandler(config.read_config("preferred browser"))
                if not self.driver_handler:
                    self.driver_handler = "chrome"
                log_into_mantis(self.driver_handler.get_driver(), username, app.password)

            reporter.report_bug(project=self.selected_project, log_lines=current_bug_deque, version=game_version,
                                username=username, password=app.password,
                                _driver_handler=self.driver_handler, priority=priority,
                                severity=severity, late_image=self.late_image, prefix=prefix,
                                rename_images=self.rename_images, new_img_name=self.rename_box.get())
            self.late_image = None

            self.go_to_reported()

        def look_for_images_again(self, current_bug):
            # Handles mass looking for images and updates them
            self.bug_handler.try_images_again()
            for bug in current_bug:
                bug.reload_image(self.bug_handler)

        def update_image_thumbnails(self, current_bug, thumbnails, image_location_text, find_img_button,
                                    try_again_button, canvas):
            # This method takes all Labels in thumbnails[] and tries to update them to the BugEntry's image
            # It also checks if all images are selected and if so, cleans up the buttons
            try:
                self.look_for_images_again(current_bug)
                for i in range(len(current_bug)):
                    if i == 0:
                        image_to_show = ImageTk.PhotoImage(current_bug[i].get_image())
                    else:
                        image_to_show = ImageTk.PhotoImage(current_bug[i].get_small_image())
                    thumbnails[i].configure(image=image_to_show)
                    thumbnails[i].image = image_to_show
                    current_bug[i].get_image().close()
                if current_bug[0].image_location:
                    if find_img_button:
                        find_img_button.get_element().pack_forget()
                        find_img_button.get_element().destroy()
                    image_location_text.insert(END, current_bug[0].image_location)
                    image_location_text.configure(state=DISABLED)
                    image_location_text.pack(anchor="s", pady=5, padx=5, side=BOTTOM)
                    self.head_img_label.bind('<Button-1>',
                                             lambda x=current_bug[0].image_location: open_image_in_editor(x))
                if self.bug_handler.images_good() and try_again_button:
                    try_again_button.get_element().pack_forget()
                    try_again_button.get_element().destroy()
                canvas.config(scrollregion=canvas.bbox("all"))
            except ValueError:
                pass

        def make_this_img_head(self, current_bug, index):
            current_bug[0], current_bug[index] = current_bug[index], current_bug[0]

        class BugEntry:
            # Each line of current bug is represented by a line and an image as instances of this class
            # This class is used to represent the current bug and its images in the Reporting screen
            line = None
            image = None
            image_location = None

            def __init__(self, line, image_location):
                self.line = line
                self.image = Image.open("./resources/image_not_found.png")
                self.image_location = image_location

            def get_image(self):
                # Returns the image scaled to the large view
                temp_image = self.image
                temp_image.thumbnail(Application.Reporting.img_size)
                return temp_image

            def get_small_image(self):
                # Returns the image scaled to a small thumbnail view
                temp_image = copy.deepcopy(self.image)
                temp_image.thumbnail(Application.Reporting.small_img_size)
                return temp_image

            def reload_image(self, bug_handler):
                # Tries to get image location from the bug_handler and if it does, gets its image as well
                self.image_location = bug_handler.try_get_image(self.line)
                if self.image_location:
                    if app.reporting:
                        app.reporting.duplicates_button.get_element()['font'] = Font(size=15)
                    self.image = Image.open(self.image_location)

        def make_scrollable_canvas(self, frame, bug_len, image_labels):
            # Here, a canvas is created to display the image thumbnails and allow for scrolling
            # Taken from https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
            thumbnail_canvas = Canvas(frame, bg=Application.current_color_theme[2],
                                      highlightthickness=0, width=self.small_img_size[0]*2 + 10)
            thumbnail_canvas.grid(row=0, column=0, sticky="news")

            if bug_len > 5:  # Make a Scrollbar if there are more than 5 images (bug head and 4 extra)
                sb = Scrollbar(frame, orient="vertical")
                sb.grid(row=0, column=1, sticky="ns")
                sb.config(command=thumbnail_canvas.yview)
                thumbnail_canvas.config(yscrollcommand=sb.set)

            # Use this thumbnail_frame to insert image thumbnails
            thumbnail_frame = Frame(thumbnail_canvas, bg=Application.current_color_theme[2])
            thumbnail_canvas.create_window((0, 0), window=thumbnail_frame, anchor="nw")

            for line_no in range(bug_len - 1):
                temp_img_label = Label(thumbnail_frame, bg=Application.current_color_theme[2])
                temp_img_label.place(x=0, y=0)
                temp_img_label.grid(row=line_no // 2, column=line_no % 2, sticky="news")
                image_labels.append(temp_img_label)

            thumbnail_canvas.config(scrollregion=thumbnail_frame.bbox("all"))
            return thumbnail_canvas

        @staticmethod
        def clear_text_box(text_box):
            if text_box.get() in ['Enter asset path/debug info', 'Enter prefix', 'Bug Summary (Default)']:
                text_box.delete(0, END)

        def check_prefix(self, value):
            self.remember_prefix = value.get()

        def check_rename(self, value):
            self.rename_images = value.get()
            if self.rename_images:
                self.rename_box['state'] = NORMAL
            else:
                self.rename_box['state'] = DISABLED

        def make_options_sidebar(self, frame):
            # The report options sidebar is created here.
            if 'a' in self.category:
                self.show_text_input_asset_path(frame)

            priority_choices = ['Low', 'Normal', 'High', 'Urgent', 'Immediate']
            self.priority_var = StringVar(frame)
            self.priority_var.set(priority_choices[0])

            priority_menu = OptionMenu(frame, self.priority_var, *priority_choices)
            priority_menu.config(activebackground=Application.current_color_theme[3])
            priority_menu.config(activeforeground=Application.current_color_theme[1])
            priority_menu.config(highlightbackground=Application.current_color_theme[3])

            priority_text = Label(frame, font=Font(size=12), bg=Application.current_color_theme[2],
                                  bd=0, height=1, width=10, fg=Application.current_color_theme[1],
                                  text="Priority")
            priority_text.grid(row=1, column=0)
            # priority_text.insert(END, "Priority")
            # priority_text.config(state=DISABLED)

            priority_menu.grid(row=1, column=1, sticky=W+E)
            priority_menu.config(bg=Application.current_color_theme[2])
            priority_menu.config(fg=Application.current_color_theme[1])
            priority_menu.config(font="Helvetica 10")
            self.priority_var.trace("w", self.priority_callback)  # This binds the callback to the write event

            severity_choices = ['Minor', 'Major']
            self.severity_var = StringVar(frame)
            self.severity_var.set(severity_choices[0])
            severity_text = Label(frame, font=Font(size=12), bg=Application.current_color_theme[2],
                                  bd=0, height=1, text="Severity",
                                  width=10, fg=Application.current_color_theme[1])
            severity_text.grid(row=2, column=0)
            # severity_text.insert(END, "Severity")
            # severity_text.config(state=DISABLED)

            severity_menu = OptionMenu(frame, self.severity_var, *severity_choices)
            severity_menu.config(activebackground=Application.current_color_theme[3])
            severity_menu.config(activeforeground=Application.current_color_theme[1])
            severity_menu.config(highlightbackground=Application.current_color_theme[3])
            severity_menu.grid(row=2, column=1, sticky=W+E)

            severity_menu.config(bg=Application.current_color_theme[2])
            severity_menu.config(fg=Application.current_color_theme[1])
            severity_menu.config(font="Helvetica 10")

            if self.category == 'm' or 'a' in self.category:
                severity_menu['state'] = DISABLED
            # elif 'a' in self.category:
            #     priority_menu['state'] = DISABLED
            #     self.priority_var.set(priority_choices[1])
            #     self.severity_var.set(severity_choices[0])

            self.show_prefix_input(frame)

            checkbox_frame = Frame(master=frame, bg=Application.current_color_theme[2])

            checkbox_description = Label(checkbox_frame, font=Font(size=8), text="Remember prefix",
                                         bg=Application.current_color_theme[2], fg=Application.current_color_theme[1],
                                         bd=0, height=1, width=15, )
            # checkbox_description.insert(END, "Remember prefix")
            # checkbox_description.configure(state=DISABLED)

            prefix_checked = BooleanVar()
            prefix_checkbox = Checkbutton(master=checkbox_frame, bg=Application.current_color_theme[2],
                                          activebackground=Application.current_color_theme[2], variable=prefix_checked,
                                          command=lambda: self.check_prefix(value=prefix_checked),
                                          selectcolor=Application.current_color_theme[2],
                                          fg=Application.current_color_theme[1],
                                          activeforeground=Application.current_color_theme[1])
            if self.category == 'm':
                checkbox_frame.grid(column=1, row=5, sticky=E)
                checkbox_description.pack(side=LEFT)
                prefix_checkbox.pack(side=RIGHT)

            self.show_rename_images_input(frame)

            rename_checkbox_frame = Frame(master=frame, bg=Application.current_color_theme[2])
            rename_checkbox_frame.grid(column=1, row=7, sticky=E)

            rename_checkbox_description = Label(rename_checkbox_frame, font=Font(size=8), bd=0, text="Rename?",
                                                bg=Application.current_color_theme[2], height=1,
                                                width=15, fg=Application.current_color_theme[1])
            rename_checkbox_description.pack(side=LEFT)
            # rename_checkbox_description.insert(END, "Rename?")
            # rename_checkbox_description.configure(state=DISABLED)

            rename_checked = BooleanVar()

            rename_checkbox = Checkbutton(master=rename_checkbox_frame, bg=Application.current_color_theme[2],
                                          activebackground=Application.current_color_theme[2], variable=rename_checked,
                                          command=lambda: self.check_rename(value=rename_checked),
                                          selectcolor=Application.current_color_theme[2],
                                          fg=Application.current_color_theme[1],
                                          activeforeground=Application.current_color_theme[1])

            if self.rename_images:
                rename_checkbox.select()

            rename_checkbox.pack(side=RIGHT)
            bug_summary_text = Text(checkbox_frame, font=Font(size=8), bg=Application.current_color_theme[2],
                                    bd=0, height=1, width=15, fg=Application.current_color_theme[0])

            self.prefix_check_button = prefix_checkbox

            for col in range(frame.grid_size()[0]):
                frame.grid_columnconfigure(col, minsize=120)
            for row in range(frame.grid_size()[0]):
                frame.grid_rowconfigure(row, minsize=40)

        def priority_callback(self, *args):
            # Priority of map bugs determines their severity, see testing guide on wiki
            if self.category == 'm' or 'a' in self.category:
                if self.priority_var.get() == "Low" and self.severity_var.get() == "Major":
                    self.severity_var.set("Minor")
                elif self.priority_var.get() != "Low" and self.severity_var.get() == "Minor":
                    self.severity_var.set("Major")

        def show_canvas(self, thumbnails_frame, options_frame, this_button, current_bug, image_labels,
                        image_location_text, image_path_button, try_again_button, thumbnail_canvas):
            # This switches the frame to the thumbnails_frame and updates all thumbnails and buttons
            # It is not displayed at first, only when show_sidebar() is called
            options_frame.pack_forget()
            thumbnails_frame.pack()
            # This method oversees the transfer from bug options to image thumbnail preview
            if not self.bug_handler.images_good():
                try_again_button.get_element().pack(padx=10, pady=10, side=RIGHT)

            self.update_image_thumbnails(current_bug, image_labels, image_location_text, image_path_button,
                                         try_again_button, thumbnail_canvas)

            this_button.get_element()['text'] = "Report\noptions"
            this_button.get_element()['command'] = lambda: self.show_sidebar(
                    thumbnails_frame, options_frame, this_button, current_bug, image_labels, image_location_text,
                    image_path_button, try_again_button, thumbnail_canvas
                )

        def show_sidebar(self, thumbnails_frame, options_frame, this_button, current_bug, image_labels,
                         image_location_text, image_path_button, try_again_button, thumbnail_canvas):
            # This switches to the report options frame and updates buttons
            thumbnails_frame.pack_forget()
            options_frame.pack()
            if try_again_button:
                try_again_button.get_element().pack_forget()
            this_button.get_element()['text'] = "Image\npreview"
            this_button.get_element()['command'] = lambda: self.show_canvas(
                thumbnails_frame, options_frame, this_button, current_bug, image_labels,
                image_location_text, image_path_button, try_again_button, thumbnail_canvas
            )

        @staticmethod
        def disable_button(button):
            button['state'] = DISABLED

        def init_widgets(self, current_bug):
            # region Frames
            background_frame = Frame(master=self, bg=Application.current_color_theme[3])
            background_frame.pack(fill=BOTH, expand=True)
            game_version = find_version(Application.Reporting.selected_project[0])
            version_line = f"Reporting in project [{Application.Reporting.selected_project}] at version {game_version}"

            version_info_text = Text(background_frame, height=1, width=100, bg=Application.current_color_theme[3],
                                     fg=Application.current_color_theme[1], bd=0, font="Helvetica 12")
            version_info_text.pack(anchor="nw", pady=5, padx=5, side=TOP)
            version_info_text.insert(END, version_line)

            assign_to = find_assign_to(current_bug[0].line, self.selected_project[0])
            if assign_to == "":
                assign_to = "unknown"
            version_info_text.insert(END, f"\t- Assigning to {assign_to}")
            version_info_text.configure(state=DISABLED)

            middle_frame = Frame(background_frame, bg=Application.current_color_theme[2])
            middle_frame.pack(anchor="center", pady=5, padx=15)

            opt_prefix = ''
            opt_asset = ''
            if self.prefix not in ['Enter prefix', ''] and self.prefix:
                opt_prefix = f"{self.prefix} - "

            if self.asset_path_input not in ['Enter asset path/debug info', ''] and self.asset_path_input:
                opt_asset = f"{self.asset_path_input} - "

            current = self.bug_handler.get_current()[0][:-1]
            current_raw = current
            if '_' in current:
                current = current.split('_')[1]
                current = current.split(';')[0]
            else:
                current = current.split(';')[0]

            current_raw_summary = f"{current_raw}"
            current_raw_text = Text(middle_frame, height=1, width=100, bg=Application.current_color_theme[2],
                                    fg=Application.current_color_theme[1], bd=0, font="Helvetica 10")
            current_raw_text.pack(side=TOP, fill=X, pady=0, padx=5)
            current_raw_text.insert(END, current_raw_summary)
            current_raw_text.configure(state=DISABLED)

            current_bug_summary = f"Preview: {game_version} - {opt_prefix}{opt_asset}{current}"
            current_bug_text = Text(middle_frame, height=1, width=100, bg=Application.current_color_theme[2],
                                    fg=Application.current_color_theme[1], bd=0, font="Helvetica 13")
            current_bug_text.pack(side=TOP, fill=X, pady=5, padx=5)
            current_bug_text.insert(END, current_bug_summary)
            current_bug_text.configure(state=DISABLED)
            self.bug_preview = current_bug_text

            left_frame = Frame(middle_frame, bg=Application.current_color_theme[2])
            left_frame.pack(anchor="w", side=LEFT, pady=0, padx=10)
            right_frame = Frame(middle_frame, bg=Application.current_color_theme[2])
            right_frame.pack(anchor="e", side=RIGHT, fill=Y, padx=10)

            frame_for_canvas = Frame(right_frame, bg=Application.current_color_theme[2])  # Frame for the canvas
            frame_for_canvas.pack(side=TOP, pady=0, padx=0)
            frame_for_canvas.grid_columnconfigure(0, weight=1)
            frame_for_sidebar = Frame(right_frame, bg=Application.current_color_theme[2])  # Frame for the sidebar

            # These two frames will be filled and then alternated between in show_canvas and show_sidebar
            right_buttons_frame = Frame(right_frame, bg=Application.current_color_theme[2])
            right_buttons_frame.pack(side=BOTTOM, fill=X)
            bottom_frame = Frame(background_frame, bg=Application.current_color_theme[3])
            bottom_frame.pack(side=BOTTOM, fill=X)

            # All image labels are created here, they will be grid-placed into the thumbnail_frame
            # Except the first one, that is the bug head and gets the big preview
            image_labels = []  # Use this array to reference the labels and update them
            self.head_img_label = Label(left_frame, bg=Application.current_color_theme[2])
            self.head_img_label.place(x=0, y=0)
            self.head_img_label.pack(pady=0, padx=0, side=TOP)
            image_labels.append(self.head_img_label)
            image_location_text = Text(left_frame, height=1, width=80, bg=Application.current_color_theme[2],
                                       fg=Application.current_color_theme[1], bd=0, font="Helvetica 10")
            # The scrollable canvas is created here
            thumbnail_canvas = self.make_scrollable_canvas(frame_for_canvas, len(current_bug), image_labels)
            self.make_options_sidebar(frame_for_sidebar)

            # endregion Frames
            if self.already_reported:
                # If a report has been made already, it is not possible to go back to project selection
                # instead, this button will take the user to the main menu
                back_button = Application.AppButton(
                    'Main Menu', frame=bottom_frame, command=lambda: self.go_to_main_menu(), side=LEFT)
            else:
                back_button = Application.AppButton(
                    'BACK', frame=bottom_frame, side=LEFT, command=lambda: app.reporting.go_to_projects("normal")
                )
            report_options_button = Application.AppButton("Report\noptions", right_buttons_frame, side=RIGHT)

            if not current_bug[0].image_location:
                image_path_button = Application.AppButton("Find image", left_frame, side=BOTTOM,
                                                          pady=5, text_spacing=10)
            else:
                image_path_button = None

            if not self.bug_handler.images_good():
                try_again_button = Application.AppButton(
                    "Try again", right_buttons_frame, side=RIGHT,
                    command=lambda: self.update_image_thumbnails(current_bug, image_labels, image_location_text,
                                                                 image_path_button, try_again_button, thumbnail_canvas)
                )
            else:
                try_again_button = None  # Why try again if you have everything

            report_options_button.get_element()['command'] = lambda: self.show_sidebar(
                frame_for_canvas, frame_for_sidebar, report_options_button, current_bug, image_labels,
                image_location_text, image_path_button, try_again_button, thumbnail_canvas
            )  # These are needed for the sidebar switching to be able to hide/show all the elements

            if image_path_button:
                image_path_button.get_element()['command'] = lambda: self.find_missing_image(
                    current_bug[0], try_again_button, image_path_button, image_location_text
                )

            self.update_image_thumbnails(current_bug, image_labels, image_location_text, image_path_button,
                                         try_again_button, thumbnail_canvas)
            self.show_sidebar(
                frame_for_canvas, frame_for_sidebar, report_options_button, current_bug, image_labels,
                image_location_text, image_path_button, try_again_button, thumbnail_canvas)
            # region Bottom

            button_report = Application.AppButton(
                "REPORT", bottom_frame, side=RIGHT,
                command=lambda: [self.ReportingThread(self.bug_handler.get_current()[0][:-1]).start(), self.disable_button(button_report.get_element())]
            )

            button_find_duplicates = Application.AppButton(
                "Find\nduplicates", bottom_frame, side=RIGHT,
                command=lambda: self.DuplicatesThread(self.bug_handler.get_current()[0][:-1]).start()
            )

            self.duplicates_button = button_find_duplicates

            button_skip_report = Application.AppButton(
                "Delete report", bottom_frame, side=RIGHT, command=lambda: self.show_next_report(True)
            )
            button_skip_report = Application.AppButton(
                "Skip report", bottom_frame, side=RIGHT, command=lambda: self.show_next_report(False)
            )
            # endregion Bottom

    class ReportedScreen(Page):
        bug_handler = None
        last_bug = None
        prefix = None
        new_img_name = None
        rename_images = False

        def __init__(self, bug_handler, last_bug, next_bug, prefix, remember_prefix, remember_rename=False):
            super().__init__()
            if remember_prefix and prefix not in ['', 'Enter prefix'] and prefix:
                self.prefix = prefix
            self.last_bug = last_bug
            self.rename_images = remember_rename
            self.bug_handler = bug_handler
            self.pack(fill=BOTH, expand=True)
            self.init_widgets()

        def go_to_reporting(self):
            reporter.asset_path = None
            app.reported.pack_forget()
            self.pack_forget()
            self.bug_handler.read_next()
            app.reported = None
            if self.bug_handler.get_current:
                try:
                    app.reporting = Application.Reporting(None, bug_handler=self.bug_handler,
                                                          reported=True, prefix=self.prefix,
                                                          last_time_rename_checked=self.rename_images)
                except TypeError:
                    app.main_menu = Application.MainMenu()
            else:
                app.main_menu = Application.MainMenu()

        def go_to_main_menu(self):
            # If there is a comment in the last report, it is not archived!
            # This also makes the program throw an IndexError if there is only a comment in bugs.txt
            self.pack_forget()
            app.main_menu = Application.MainMenu()
            app.reported = None

        def init_widgets(self):
            background_frame = Frame(master=self, bg=Application.current_color_theme[3])
            background_frame.pack(fill=BOTH, expand=True)
            bottom_frame = Frame(background_frame, bg=Application.current_color_theme[3])
            bottom_frame.pack(side=BOTTOM, fill=X)

            middle_frame = Frame(background_frame, bg=Application.current_color_theme[2])
            middle_frame.pack(anchor="center", pady=85, padx=15)

            current_bug_summary = self.last_bug[0][:-1]
            current_bug_text = Text(middle_frame, height=1, width=100, bg=Application.current_color_theme[2],
                                    fg=Application.current_color_theme[0], bd=0, font="Helvetica 13")
            current_bug_text.pack(side=TOP, pady=10, padx=10)
            current_bug_text.insert(END, current_bug_summary)
            current_bug_text.configure(state=DISABLED)

            reported_text = Label(middle_frame, bg=Application.current_color_theme[2],
                                  fg=Application.current_color_theme[0], bd=0,
                                  font="Helvetica 30", justify=CENTER, text="Opened Mantis report")
            reported_text.pack(anchor="n", pady=35, padx=35, side=TOP)

            menu_button = Application.AppButton(
                'Main Menu', frame=bottom_frame, command=self.go_to_main_menu, side=LEFT)

            next_report_button = Application.AppButton(
                'Next Report', frame=middle_frame, command=self.go_to_reporting, side=TOP, font_size=20,
                offx=40, offy=30, text_spacing=25, color1=Application.current_color_theme[1]
            )

    class Batch(Page):  # This might not get used
        def __init__(self, project):
            super().__init__()
            self.pack(fill=BOTH, expand=True)
            self.init_widgets()

        def init_widgets(self):
            # Placeholder screen for batch reporting
            background_frame = Frame(master=self, bg=Application.current_color_theme[3])
            background_frame.pack(fill=BOTH, expand=True)

            bottom_frame = Frame(background_frame, bg=Application.current_color_theme[3])
            bottom_frame.pack(side=BOTTOM, anchor="sw")
            back_button = Application.AppButton('BACK', frame=bottom_frame, anchor="sw",
                                                command=lambda: self.go_to_projects("normal"))

        def go_to_projects(self, use_mode):
            self.pack_forget()
            app.projects_page = Application.SelectProject(use_mode)
            app.projects_page.open_page()
            app.main_menu = None


def rewrite_textbox(message, textbox):
    # use this to clear a textbox and display a message
    textbox.configure(state=NORMAL)
    textbox.delete("1.0", END)
    textbox.insert(END, message)
    textbox.configure(state=DISABLED)


def open_image_in_editor(img_path):
    img_path = './test.jpg'
    subprocess.call(['start', img_path], shell=True)


# region Program init
# Creates the basic "box" in which you can put all of the GUI elements
# It also takes care of misc stuff, s.a. fixed window size, title on the app window and the icon

root = Tk()
root.geometry('960x540')
root.minsize(width=960, height=540)
root.maxsize(width=960, height=540)
root.resizable(0, 0)
root.wm_iconbitmap('.//resources/icon.ico')
root.wm_title('TSReporter')
app = Application()
root.mainloop()
# endregion
