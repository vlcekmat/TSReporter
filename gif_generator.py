from tkinter import *
from tkinter.font import Font
from PIL import Image
import imageio
from tkinter import filedialog
import os

from numpy import iterable


def rewrite_textbox(message, textbox):
    # use this to clear a textbox and display a message
    textbox.configure(state=NORMAL)
    textbox.delete("1.0", END)
    textbox.insert(END, message)
    textbox.configure(state=DISABLED)


class GifMaker:
    # This class handles the frames of the gif and the gif generation
    frames = []  # list of tuples of frames that will be in the gif
    # frames[0] are PIL Images from Image.open()
    # frames[1] is a bool if the image was a png and therefore a .jpg was generated and needs to be deleted
    gif_name = ""  # this is the name that the gif will be saved under, same as first frame but .gif
    save_gifs_here = ""  # folder where the gif will be saved, should be "edited images location" from cfg

    def set_save_location(self, location):
        self.save_gifs_here = location

    def add_frame(self, image_location, was_png):
        if len(self.frames) == 0:
            self.gif_name = self.save_gifs_here + '/' + image_location.split('/')[-1][0:-4] + ".gif"
        new_frame = Image.open(image_location)
        new_frame.thumbnail((1200, 700))
        self.frames.append((new_frame, was_png))

    def remove_frame(self, index):
        remove_me = self.frames.pop(index)
        remove_me[0].close()
        if remove_me[1]:
            os.remove(remove_me[0].filename)
        if index == 0:
            if len(self.frames) == 0:
                self.gif_name = ""
            else:  # Set the gif name to be the new gif head
                self.gif_name = self.save_gifs_here + '/' + self.frames[0].split('/')[-1][0:-4] + ".gif"

    def clear_frames(self):
        while len(self.frames) > 0:
            remove_me = self.frames.pop()
            remove_me[0].close()
            if remove_me[1]:
                os.remove(remove_me[0].filename)

        self.gif_name = ""

    def save_gif(self, fps):
        if self.gif_name != "" and len(self.frames) > 0:
            imageio.mimwrite(self.gif_name, [fr[0] for fr in self.frames], fps=fps)
            # The [...] takes makes list of 0th tuple member from self.frames (the images themselves)


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
        self.gif_maker.clear_frames()
        self.pack_forget()
        self.app.main_menu = self.app.MainMenu()
        self.app.gif_page = None

    def find_image(self):
        img_tuple = filedialog.askopenfilenames(
            filetypes=[
                ("image", ".png"),
                ("image", ".jpg")
            ]
        )
        if img_tuple:
            img_list = []
            for img in img_tuple:
                img_list.append(img)
            del img_tuple
            for img in img_list:
                old_img_name = img
                new_img_name = old_img_name
                was_png = False
                if old_img_name[-4:] == ".png":
                    was_png = True
                    new_img_name = old_img_name[:-4] + ".jpg"
                    with Image.open(old_img_name) as convert_me:
                        convert_me.save(new_img_name, optimize=True, quality=85)
                self.gif_maker.add_frame(new_img_name, was_png)

    def clear_gif_frames(self):
        self.gif_maker.clear_frames()

    def convert_to_gif(self):
        self.gif_maker.save_gif(self.duration)

    def callback(self, dur_var):
        dv = dur_var.get()
        self.duration = 1
        try:
            float(dv)
        except ValueError:
            return
        if dv != '':
            self.duration = 1000/int(dv)

    def init_widgets(self):
        background = Frame(master=self, bg=self.current_color_theme[4])
        background.pack(fill=BOTH, expand=True)

        top_frame = Frame(master=background, bg=self.current_color_theme[3])
        top_frame.pack(fill=BOTH, expand=True, pady=20, padx=20)

        bottom_frame = Frame(master=background, bg=self.current_color_theme[4])
        bottom_frame.pack(fill=X, side=BOTTOM)

        images_list_frame = Frame(master=top_frame, bg=self.current_color_theme[3])
        # images_list_frame.pack(side=LEFT, padx=20)

        for i in range(10):
            Label(master=images_list_frame, bg=self.current_color_theme[3], fg=self.current_color_theme[2],
                  text=f'Image {i+1}: ', font=Font(size=10)).grid(row=i, column=0)

        back_button = self.app.AppButton('Main Menu', frame=bottom_frame,
                                         command=self.go_to_main_menu, side=LEFT)
        convert_button = self.app.AppButton('Convert', frame=bottom_frame,
                                            command=self.convert_to_gif, side=RIGHT)
        find_button = self.app.AppButton('Find', frame=bottom_frame,
                                         command=self.find_image, side=RIGHT)
        clear_button = self.app.AppButton('Clear', frame=bottom_frame,
                                          command=self.clear_gif_frames, side=RIGHT)
        fps_frame = Frame(master=bottom_frame, bg=self.current_color_theme[4])
        fps_frame.pack(side=RIGHT, padx=10)

        fps_text = Label(master=fps_frame, bg=self.current_color_theme[4], fg=self.current_color_theme[2],
                         text='Delay', font=Font(size=15)).grid(row=0, column=0)
        dur_var = StringVar()
        dur_var.set(1000)
        dur_var.trace("w", lambda name, index, mode, var=dur_var: self.callback(var))
        fps_entry = Entry(master=fps_frame, bg=self.current_color_theme[3], fg=self.current_color_theme[2],
                          width=10, font=Font(size=15), textvariable=dur_var).grid(row=1, column=0)
