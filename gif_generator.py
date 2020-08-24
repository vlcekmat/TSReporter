from tkinter import *
from tkinter.font import Font
from PIL import Image
import imageio
from tkinter import filedialog


class GifMaker:
    frames = []
    gif_name = ""
    save_gifs_here = ""

    def set_save_location(self, location):
        self.save_gifs_here = location

    def add_frame(self, image_location):
        if len(self.frames) == 0:
            self.gif_name = self.save_gifs_here + '/' + image_location.split('/')[-1][0:-4] + ".gif"
        new_frame = Image.open(image_location)
        new_frame.thumbnail((1200, 700))
        self.frames.append(new_frame)

    def remove_frame(self, index):
        self.frames.pop(index)

    def save_gif(self, fps):
        imageio.mimwrite(self.gif_name, self.frames, fps=fps)


class GifGeneratorPage(Frame):
    current_color_theme = None
    app = None
    gif_maker = GifMaker()
    duration = 1

    def __init__(self, app, location):
        super().__init__()
        self.dur_var = StringVar()
        self.gif_maker.set_save_location(location)
        self.pack(fill=BOTH, expand=True)
        self.app = app
        self.current_color_theme = app.current_color_theme
        self.init_widgets()

    def go_to_main_menu(self):
        self.pack_forget()
        self.app.main_menu = self.app.MainMenu()
        self.app.gif_page = None

    def find_image(self):
        self.gif_maker.add_frame(filedialog.askopenfile().name)

    def convert_to_gif(self):
        self.gif_maker.save_gif(self.duration)

    def callback(self, dur_var):
        # TODO: make sure dur_var is float
        dv = dur_var.get()
        if dv == '':
            self.duration = 1
        else:
            self.duration = 1000/int(dv)

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
                                            command=self.convert_to_gif, side=RIGHT)
        find_button = self.app.AppButton('Find', frame=bottom_frame,
                                         command=self.find_image, side=RIGHT)
        fps_frame = Frame(master=bottom_frame, bg=self.current_color_theme[4])
        fps_frame.pack(side=RIGHT, padx=10)

        fps_text = Label(master=fps_frame, bg=self.current_color_theme[4], fg=self.current_color_theme[2],
                         text='Delay', font=Font(size=15)).grid(row=0, column=0)
        dur_var = StringVar()
        dur_var.trace("w", lambda name, index, mode, var=dur_var: self.callback(var))
        fps_entry = Entry(master=fps_frame, bg=self.current_color_theme[3], fg=self.current_color_theme[2],
                          width=10, font=Font(size=15), textvariable=dur_var).grid(row=1, column=0)
