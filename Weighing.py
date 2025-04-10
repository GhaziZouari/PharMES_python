import customtkinter as ctk
from utils import get_mac_address, get_ip_address
import requests
from datetime import datetime
import re

API_URL = "http://192.168.1.60:8000/api"
WEIGHING_INFO_ENDPOINT = f"{API_URL}/weighing/info"
VALIDATE_WEIGHING_ENDPOINT = f"{API_URL}/weighing/validate"
CHECK_BOX_ENDPOINT = f"{API_URL}/check_box"


class WeighingProcess(ctk.CTkFrame):
    def __init__(self, parent, smart_box, smartbox_type):
        super().__init__(parent)
        self.pack(fill="both", expand=True) 
        self.smart_box = smart_box
        self.smartbox_type = smartbox_type

        # Close button
        self.close_btn = ctk.CTkButton(self, text="X", fg_color="red", 
                                       text_color="white", width=50, height=50, 
                                       command=self.fermer_fenetre)
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Initialize UI
        self.init_ui()
        self.fetch_weighing_data()
        
    def fermer_fenetre(self):
        self.master.destroy()
        
    def init_ui(self):
        # Clear existing widgets except close button
        for widget in self.winfo_children():
            if widget != self.close_btn:
                widget.destroy()
        
        # Create labels for weighing info
        self.code_label = ctk.CTkLabel(self, text="Code :", font=("Arial", 25), text_color="#FFB347")
        self.lot_label = ctk.CTkLabel(self, text="Lot MP :", font=("Arial", 25), text_color="#FFB347")
        self.designation_label = ctk.CTkLabel(self, text="Designation :", font=("Arial", 25), text_color="#FFB347")
        self.num_contenant_label = ctk.CTkLabel(self, text="Num Contenant :", font=("Arial", 25), text_color="#FFB347")
        self.qte_label = ctk.CTkLabel(self, text="Qte à peser :", font=("Arial", 25), text_color="#FFB347")
        self.f_label = ctk.CTkLabel(self, text="F :", font=("Arial", 25), text_color="#FFB347")
    
        
        self.code_value = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")
        self.lot_value = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")
        self.designation_value_first_line = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")
        self.designation_value_second_line = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")
        self.num_contenant_value = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")
        self.qte_value = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")
        self.f_value = ctk.CTkLabel(self, text="", font=("Arial", 25), text_color="#A2D5F2")

        # Initially hide the send button
        self.send_btn = ctk.CTkButton(self, text="Send", command=self.send_weighing_data, fg_color="blue", width=150, height=50, font=("Arial", 30, "bold"))
        self.send_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        
        # Status message label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 24))
        self.status_label.place(relx=0.5, rely=0.8, anchor="center")
        
    def fetch_weighing_data(self):
        try:
            response = requests.post(WEIGHING_INFO_ENDPOINT, json={"smart_box": self.smart_box})
            
            if response.status_code == 200:
                data = response.json()
                self.error_state = None  # Reset error state

                if "error" in data:
                    if data["error"]["message"] == "No active weighing record found":
                        self.handle_error("Veuillez scanner une matière première")
                    else:
                        self.handle_error(data["error"]["message"])
                else:
                    self.id_fiche_pesse = data.get('id_fiche_pesse')
                    self.init_ui()
                    self.update_weighing_ui(data)
                    self.weighing_data = data
            
        
        except requests.exceptions.RequestException as e:
            self.handle_error("Erreur de connexion au serveur")    

    def split_into_two_lines(self, text, max_first_line_length=35):
        words = text.split()  # Split text into individual words
        first_line = []
        second_line = []
        
        current_length = 0  # Tracks the length of the first line
        
        # Distribute words without breaking them
        for word in words:
            # Check if word fits in the first line
            if current_length + len(word) <= max_first_line_length:
                first_line.append(word)
                current_length += len(word) + 1  # +1 accounts for the space between words
            else:
                second_line.append(word)

        # Handle case where everything fits on one line
        if not second_line:
            return ' '.join(first_line), ""  # Return empty second line
        
        return ' '.join(first_line), ' '.join(second_line)
    
          
    def update_weighing_ui(self, data):
        
        # Get the full designation
        full_designation_value = data.get('designation', 'N/A')
        # Split designation into two parts if too long
        max_first_line_length = 28
 
        first_line, second_line = self.split_into_two_lines(full_designation_value, max_first_line_length)

        if second_line:  
            # Position labels
            self.code_label.place(relx=0.04, rely=0.05, anchor="w")
            self.code_value.place(relx=0.21, rely=0.05, anchor="w")

            self.lot_label.place(relx=0.04, rely=0.15, anchor="w")
            self.lot_value.place(relx=0.26, rely=0.15, anchor="w")

            self.designation_label.place(relx=0.04, rely=0.25, anchor="w")
            self.designation_value_first_line.place(relx=0.36, rely=0.25, anchor="w")
            
            self.designation_value_second_line.place(relx=0.04, rely=0.35, anchor="w")

            self.num_contenant_label.place(relx=0.04, rely=0.45, anchor="w")
            self.num_contenant_value.place(relx=0.45, rely=0.45, anchor="w")

            self.qte_label.place(relx=0.04, rely=0.55, anchor="w")
            self.qte_value.place(relx=0.35, rely=0.55, anchor="w")

            self.f_label.place(relx=0.04, rely=0.65, anchor="w")
            self.f_value.place(relx=0.13, rely=0.65, anchor="w")
        else :    
            # Position labels
            self.code_label.place(relx=0.04, rely=0.05, anchor="w")
            self.code_value.place(relx=0.21, rely=0.05, anchor="w")

            self.lot_label.place(relx=0.04, rely=0.15, anchor="w")
            self.lot_value.place(relx=0.26, rely=0.15, anchor="w")

            self.designation_label.place(relx=0.04, rely=0.25, anchor="w")
            self.designation_value_first_line.place(relx=0.36, rely=0.25, anchor="w")
            
            self.num_contenant_label.place(relx=0.04, rely=0.35, anchor="w")
            self.num_contenant_value.place(relx=0.45, rely=0.35, anchor="w")

            self.qte_label.place(relx=0.04, rely=0.45, anchor="w")
            self.qte_value.place(relx=0.35, rely=0.45, anchor="w")

            self.f_label.place(relx=0.04, rely=0.55, anchor="w")
            self.f_value.place(relx=0.13, rely=0.55, anchor="w")

     # Update labels with weighing data
        self.code_value.configure(text=(data.get('code', 'N/A')))
        self.lot_value.configure(text=data.get('lot_mp', 'N/A'))
        if second_line:
            self.designation_value_first_line.configure(text=first_line)
            self.designation_value_second_line.configure(text=second_line)
        else :
            self.designation_value_first_line.configure(text=first_line)
        self.num_contenant_value.configure(text=data.get('num_contenant', 'N/A'))
        self.qte_value.configure(text=f"{data.get('qte_a_peser', 'N/A')} g")
        self.f_value.configure(text=data.get('F', 'N/A'))
            
       # Enable send button after a delay (simulating balance reading)
        self.after(2000, lambda: self.send_btn.configure(state="normal"))

       
    
  
                
    def handle_error(self, error_message):
        self.error_state = error_message
        self.clear_screen()
        self.show_error_screen()
    
    def show_error_screen(self):
        # Afficher le message d'erreur
        error_label = ctk.CTkLabel(self, 
            text=self.error_state,
            font=("Arial", 24, "bold"),
            text_color="red"
        )
        error_label.place(relx=0.5, rely=0.4, anchor="center")
        
     

    def send_weighing_data(self):
        self.send_btn.configure(state="disabled")
        balance_data = self.read_balance_file()
        
        if not balance_data:
            self.status_label.configure(text="Erreur: Fichier balance non trouvé")
            return
        try: 
        
            payload = {
                "smart_box": self.smart_box,
                "id_fiche_pesse": self.id_fiche_pesse,
                "net": balance_data["net"],
                "gross": balance_data["gross"],
                "tare": balance_data["tare"],
                "balance_name": balance_data["balance_name"],
                "balance_datetime": balance_data["date"],
                "balance_ID": balance_data["balance_ID"]
            }
            
            print(f"DEBUG - Payload envoyé : {payload}")

            response = requests.post(VALIDATE_WEIGHING_ENDPOINT, json=payload)
            print(f"DEBUG - Réponse API : {response.text}") 

            if response.status_code == 200:
                data = response.json()
                
                if data.get("message") == "Max Weight Exceeded":
                    # Save the current weighing data before clearing the screen
                    self.weighing_data = self.weighing_data or {}  # Save existing data
                    # Clear the screen and show the error message centered
                    self.clear_screen()
                    error_label = ctk.CTkLabel(self, text="Vous dépassez la quantité max!", font=("Arial", 30),
                    text_color="red")
                    error_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the error message
                
                    # After 2 seconds, return to the weighing information screen
                    self.after(2000, self.fetch_weighing_data)
                else:
                    # Success - refresh data
                    self.fetch_weighing_data()
                
        except requests.exceptions.RequestException:
            self.status_label.configure(text="Erreur de connexion au serveur")
    
    

    def read_balance_file(self):
        file_path = (
            "/home/advx/PharMES_python/balance_EXCIPIENT.txt" if self.smartbox_type == "EXCIPIENT"
            else "/home/advx/PharMES_python/balance_PRINCIPE_ACTIF.txt"
        )
        def parse_with_regex(file_path,is_excipient=True):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                date_match = re.search(
                    r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})', 
                    content
                )

                # Extract the matched string or None if no match
                date_str = date_match.group(1) if date_match else None
                formatted_date = None

                if date_str:
                    cleaned_date_str = re.sub(r'\s+', ' ', date_str.strip())

                    try:
                        if '.' in cleaned_date_str:
                            parsed_date = datetime.strptime(cleaned_date_str, '%d.%m.%Y %H:%M')
                        elif '-' in cleaned_date_str:
                            parsed_date = datetime.strptime(cleaned_date_str, '%Y-%m-%d %H:%M')
                        else:
                            parsed_date = None
                    except ValueError as e:
                        parsed_date = None

                    if parsed_date:
                        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')

                                
            gross = tare = net = None

            if is_excipient:
                # Extract balance ID
                balance_id_match = re.search(r'Nø r‚f\s+(\w+)', content)
                balance_id = balance_id_match.group(1) if balance_id_match else None

                # Extract balance name (line after "Type de balance")
                name_match = re.search(r'Type de balance\s*\n\s*(.+)', content)
                balance_name = name_match.group(1).strip() if name_match else None

                # Extract Gross, Tare, Net values
                gross_match = re.search(r'[G]\s+([\d.]+)\s*g', content)
                tare_match = re.search(r'[T]\s+([\d.]+)\s*g', content)
                net_match = re.search(r'[N]\s+([\d.]+)\s*g', content)

                gross = float(gross_match.group(1)) if gross_match else None
                tare = float(tare_match.group(1)) if tare_match else None
                net = float(net_match.group(1)) if net_match else None

                return {
                    'date': formatted_date,
                    'balance_ID': balance_id,
                    'balance_name': balance_name,
                    'gross': gross,
                    'tare': tare,
                    'net': net
                }

            else:
                # Extract Tare and Gross
                tare_match = re.search(r'T\s+([\d.]+)\s*g', content)
                tare = float(tare_match.group(1)) if tare_match else None

                gross_match = re.search(r'B\s+([\d.]+)\s*g', content)
                gross = float(gross_match.group(1)) if gross_match else None

                # Case 1: Normal format with Net value labeled as 'N'
                net_match = re.search(r'N\s+([\d.]+)\s*g', content)
                if net_match:
                    net = float(net_match.group(1))
                else:
                    # Case 2: Compact format — look for an unlabelled float value
                    float_matches = re.findall(r'^\s+([\d.]+)\s+g', content, re.MULTILINE)
                    if float_matches:
                        for val in float_matches:
                            fval = float(val)
                            if fval != tare and fval != gross:
                                net = fval
                                break

                return {
                    'date': formatted_date,
                    'balance_ID': '',
                    'balance_name': '',
                    'gross': gross,
                    'tare': tare,
                    'net': net
                }

        is_excipient = self.smartbox_type.upper() == "EXCIPIENT"
        return parse_with_regex(file_path, is_excipient)

    def clear_screen(self):
        #Clear all widgets except the close button
        for widget in self.winfo_children():
            if widget != self.close_btn:  # Don't delete the close button
                widget.destroy()