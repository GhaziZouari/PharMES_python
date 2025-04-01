import customtkinter as ctk
from utils import get_mac_address, get_ip_address  # Importing utility functions from utils
import requests

API_URL = "http://192.168.137.1:8000/api/check_box"

class INIT_SB(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        # Close button at the top right
        bouton_fermer = ctk.CTkButton(self, text="X", fg_color="red", text_color="white", width=50, height=50, command=self.fermer_fenetre)
        bouton_fermer.place(relx=1.0, rely=0.0, anchor="ne")

        # Automatically fetch MAC & IP and send request
        self.mac_address = get_mac_address() 
        self.ip_address = get_ip_address()
        self.send_request()
    
    #Function to close the main window
    def fermer_fenetre(self):
        self.destroy()

    def clear_screen(self):
        #Clear all widgets except the close button
        for widget in self.winfo_children():
            if widget.winfo_y() > 50:  # Don't delete the close button
                widget.destroy()

    def send_request(self):
        #Send the MAC and IP address to the Laravel API and handle the response
        payload = {"mac_addr": self.mac_address, "ip_addr": self.ip_address}

        try:
            # Send POST request to the API
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "Inconnu")
                if "error" in data:
                    self.update_status_screen("Serveur inaccessible")                
                elif status == "SB Connected":
                    self.update_status_screen("",show_start=True)
                elif status == "Missing position":  
                    self.update_status_screen("Manque de position")
                elif status == "Missing implantation":
                    self.update_status_screen("Manque d'implantation", show_back_button=True)
                elif status == "SB not identified":
                    self.update_status_screen("SmartBox non Identifiée", show_back_button=True)
            else:
                self.update_status_screen(f"Erreur: {response.status_code}")
        except requests.exceptions.ConnectionError:
        # Handle server connection issues (e.g., server unreachable)
            self.update_status_screen("Serveur inaccessible")
        except requests.exceptions.RequestException as e:
        # Handle other types of errors (e.g., timeout)
            self.update_status_screen("Veuillez réessayer")

        self.after(1000, self.send_request)

    def update_status_screen(self, message, show_start=False, show_back_button=False):
        # Update the display to show the status message
        self.clear_screen()

        # Display the status message in the center
        label_status = ctk.CTkLabel(self, text=message, font=("Arial", 40, "bold"), text_color="white")
        label_status.place(relx=0.5, rely=0.5, anchor="center")

        # Show the "Commencer" button only if status is "SB Connecté"
        if show_start:
            start_button = ctk.CTkButton(self, text="Charger", command=self.start_process,fg_color="blue", width=150, height=50, font=("Arial", 30, "bold"))
            start_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def start_process(self):
        #Open a new frame (in the same window) for the next step
        self.clear_screen()
        label_process = ctk.CTkLabel(self, text="", font=("Arial", 24, "bold"), text_color="white")
        label_process.place(relx=0.5, rely=0.4, anchor="center")


    

   