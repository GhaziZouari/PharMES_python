from init_SB import INIT_SB
from Weighing import WeighingProcess  # Assuming you've created this file
import customtkinter as ctk


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.current_frame = None
        self.show_init_screen()

    def show_init_screen(self):
        #Show the initial smart box connection screen
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = INIT_SB(self.root, self.start_weighing_process)
        self.current_frame.pack(fill="both", expand=True)

    def start_weighing_process(self, smart_box,smartbox_type):
        #Start the weighing process with the given smart box
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = WeighingProcess(self.root,  smart_box, smartbox_type)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.config(cursor="none")
    root.attributes('-fullscreen', True)
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")

    # Initialize the main application
    app = MainApplication(root)
    
    root.mainloop()