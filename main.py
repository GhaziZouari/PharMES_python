from init_SB import INIT_SB
import customtkinter as ctk

# Set appearance mode and default theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    root = ctk.CTk()
    root.config(cursor="none")
    root.attributes('-fullscreen', True)

    largeur_ecran = root.winfo_screenwidth()
    hauteur_ecran = root.winfo_screenheight()
    root.geometry(f"{largeur_ecran}x{hauteur_ecran}")

    app = INIT_SB(root)
    root.mainloop()
