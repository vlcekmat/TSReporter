from tkinter import *
from tkinter.font import Font


class GifGeneratorPage(Frame):
    current_color_theme = None
    app = None

    def __init__(self, app):
        super().__init__()
        self.pack(fill=BOTH, expand=True)
        self.app = app
        self.current_color_theme = app.current_color_theme
        self.init_widgets()

    def go_to_main_menu(self):
        self.pack_forget()
        self.app.main_menu = self.app.MainMenu()
        self.app.gif_page = None

    def find_images(self):
        pass

    def convert_to_gif(self):
        pass

    def init_widgets(self):
        background = Frame(master=self, bg=self.current_color_theme[4])
        background.pack(fill=BOTH, expand=True)

        top_frame = Frame(master=background, bg=self.current_color_theme[3])
        top_frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

        bottom_frame = Frame(master=background, bg=self.current_color_theme[4])
        bottom_frame.pack(fill=X, side=BOTTOM)

        images_list_frame = Frame(master=top_frame, bg=self.current_color_theme[3])
        images_list_frame.pack(side=LEFT, padx=20)

        for i in range(10):
            Label(master=images_list_frame, bg=self.current_color_theme[3], fg=self.current_color_theme[2],
                         text=f'Image {i+1}: ', font=Font(size=10)).grid(row=i, column=0)

        back_button = self.app.AppButton('Main Menu', frame=bottom_frame,
                                       command=self.go_to_main_menu, side=LEFT)
        convert_button = self.app.AppButton('Convert', frame=bottom_frame,
                                         command=self.find_images, side=RIGHT)
        find_button = self.app.AppButton('Find', frame=bottom_frame,
                                       command=self.convert_to_gif, side=RIGHT)
        fps_frame = Frame(master=bottom_frame, bg=self.current_color_theme[4])
        fps_frame.pack(side=RIGHT, padx=10)

        fps_text = Label(master=fps_frame, bg=self.current_color_theme[4], fg=self.current_color_theme[2],
                         text='Delay', font=Font(size=15)).grid(row=0, column=0)

        fps_entry = Entry(master=fps_frame, bg=self.current_color_theme[3], fg=self.current_color_theme[2],
                          width=10, font=Font(size=15)).grid(row=1, column=0)
