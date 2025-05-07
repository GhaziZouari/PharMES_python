import customtkinter as ctk
from utils import get_mac_address, get_ip_address
import requests
from datetime import datetime
import re

API_URL = "http://192.168.1.105:8000/api"
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

        # Auto-fetch data to mimic original behavior
        self.load_weighing_data()

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

        # Labels for weighing values (initially hidden)
        self.gross_label = ctk.CTkLabel(self, text="Gross :", font=("Arial", 25), text_color="#FFB347")
        self.net_label = ctk.CTkLabel(self, text="Net :", font=("Arial", 25), text_color="#FFB347")
        self.tare_label = ctk.CTkLabel(self, text="Tare :", font=("Arial", 25), text_color="#FFB347")
        self.gross_value = ctk.CTkLabel(self, text="", font=("Arial", 23), text_color="#A2D5F2")
        self.net_value = ctk.CTkLabel(self, text="", font=("Arial", 23), text_color="#A2D5F2")
        self.tare_value = ctk.CTkLabel(self, text="", font=("Arial", 23), text_color="#A2D5F2")

        # Single action button (initially Load)
        self.action_btn = ctk.CTkButton(self, text="Load", command=self.load_weighing_data,
                                        fg_color="#A2D5F2", width=150, height=50, font=("Arial", 30, "bold"))
        self.action_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # Status message label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 24))
        self.status_label.place(relx=0.5, rely=0.8, anchor="center")

    def load_weighing_data(self):
        #Fetch and display initial weighing data without gross, net, tare
        self.clear_screen()  # Clear previous content
        self.action_btn.configure(state="disabled", text="Load", command=self.load_weighing_data,
                                  fg_color="#A2D5F2")  # Ensure Load mode
        self.fetch_weighing_data(initial=True)

    def fetch_weighing_data(self, initial=False):
        #Fetch weighing data from the API.
      try:
            response = requests.post(WEIGHING_INFO_ENDPOINT, json={"smart_box": self.smart_box})

            if response.status_code == 200:
                data = response.json()
                self.error_state = None  # Reset error state

                if "error" in data:
                    if data["error"]["message"] == "No active weighing record found":
                        self.handle_error("Veuillez scanner une matière première")
                        # After 2 seconds, reload initial weighing data
                        self.after(2000, lambda: self.load_weighing_data())
                    else:
                        self.handle_error(data["error"]["message"])
                else:
                    self.id_fiche_pesse = data.get('id_fiche_pesse')
                    self.weighing_data = data
                    if initial:
                        self.init_ui()  # Re-initialize UI
                        self.update_weighing_ui(data, show_balance=False)
                        # After 2 seconds, show balance data and switch to Send button
                        self.after(2000, lambda: self.show_balance_data())
                    else:
                        self.update_weighing_ui(data, show_balance=True)
                        self.action_btn.configure(state="normal", text="Send",
                                                 command=self.send_weighing_data, fg_color="#A2D5F2")
            else:
                self.handle_error("Veuillez scanner une matière première")

      except requests.exceptions.RequestException as e:
            self.handle_error("Veuillez réessayer")
      finally:
            if not self.error_state:  # Only re-enable if no error
                self.action_btn.configure(state="normal")

    def split_into_two_lines(self, text, max_first_line_length=35):
        words = text.split()
        first_line = []
        second_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) <= max_first_line_length:
                first_line.append(word)
                current_length += len(word) + 1
            else:
                second_line.append(word)
                current_length += len(word) + 1

        if not second_line:
            return ' '.join(first_line), ""
        return ' '.join(first_line), ' '.join(second_line)

    def update_weighing_ui(self, data, show_balance=False):
        #Update the UI with weighing data
        full_designation_value = data.get('designation', 'N/A')
        max_first_line_length = 28
        first_line, second_line = self.split_into_two_lines(full_designation_value, max_first_line_length)

        # Position labels based on whether designation has two lines
        if second_line:
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
            if show_balance:
                self.gross_label.place(relx=0.04, rely=0.75, anchor="w")
                self.net_label.place(relx=0.402, rely=0.75, anchor="w")
                self.tare_label.place(relx=0.69, rely=0.75, anchor="w")
                self.gross_value.place(relx=0.215, rely=0.75, anchor="w")
                self.net_value.place(relx=0.525, rely=0.75, anchor="w")
                self.tare_value.place(relx=0.83, rely=0.75, anchor="w")
        else:
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
            if show_balance:
                self.gross_label.place(relx=0.04, rely=0.65, anchor="w")
                self.net_label.place(relx=0.402, rely=0.65, anchor="w")
                self.tare_label.place(relx=0.69, rely=0.65, anchor="w")
                self.gross_value.place(relx=0.215, rely=0.65, anchor="w")
                self.net_value.place(relx=0.525, rely=0.65, anchor="w")
                self.tare_value.place(relx=0.83, rely=0.65, anchor="w")

        # Update labels with weighing data
        self.code_value.configure(text=data.get('code', 'N/A'))
        self.lot_value.configure(text=data.get('lot_mp', 'N/A'))
        if second_line:
            self.designation_value_first_line.configure(text=first_line)
            self.designation_value_second_line.configure(text=second_line)
        else:
            self.designation_value_first_line.configure(text=first_line)
        self.num_contenant_value.configure(text=data.get('num_contenant', 'N/A'))
        self.qte_value.configure(text=f"{data.get('qte_a_peser', 'N/A')} g")
        self.f_value.configure(text=data.get('F'))

        # Update balance values if shown
        if show_balance:
            balance_data = self.read_balance_file()
            if balance_data:
                self.gross_value.configure(text=f"{balance_data['gross']} g")
                self.net_value.configure(text=f"{balance_data['net']} g")
                self.tare_value.configure(text=f"{balance_data['tare']} g")

    def show_balance_data(self):
        #Show gross, net, tare values and switch to Send button after delay.
        balance_data = self.read_balance_file()
        if balance_data:
            self.gross_value.configure(text=f"{balance_data['gross']} g")
            self.net_value.configure(text=f"{balance_data['net']} g")
            self.tare_value.configure(text=f"{balance_data['tare']} g")
            # Place balance labels
            if self.designation_value_second_line.cget("text"):
                self.gross_label.place(relx=0.04, rely=0.75, anchor="w")
                self.net_label.place(relx=0.402, rely=0.75, anchor="w")
                self.tare_label.place(relx=0.69, rely=0.75, anchor="w")
                self.gross_value.place(relx=0.215, rely=0.75, anchor="w")
                self.net_value.place(relx=0.525, rely=0.75, anchor="w")
                self.tare_value.place(relx=0.83, rely=0.75, anchor="w")
            else:
                self.gross_label.place(relx=0.04, rely=0.65, anchor="w")
                self.net_label.place(relx=0.402, rely=0.65, anchor="w")
                self.tare_label.place(relx=0.69, rely=0.65, anchor="w")
                self.gross_value.place(relx=0.215, rely=0.65, anchor="w")
                self.net_value.place(relx=0.525, rely=0.65, anchor="w")
                self.tare_value.place(relx=0.83, rely=0.65, anchor="w")
            self.action_btn.configure(state="normal", text="Send",command=self.send_weighing_data, fg_color="#A2D5F2")

    def handle_error(self, error_message):
        self.error_state = error_message
        self.clear_screen()
        self.show_error_screen()

    def show_error_screen(self):
        # Preprocess the error message to insert newlines for wrapping
        wrapped_text = self.wrap_text(self.error_state, max_width=400)
        error_label = ctk.CTkLabel(self,
                                   text=wrapped_text,
                                   font=("Arial", 35),
                                   text_color="red", wraplength=400, justify="center")
        error_label.place(relx=0.5, rely=0.5, anchor="center")
        self.action_btn.configure(state="normal", text="Load",
                                 command=self.load_weighing_data, fg_color="#A2D5F2")
        self.action_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def wrap_text(self, text, max_width=400):
        #Manually wrap text to approximate wraplength, inserting newlines for spacing.
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        # Approximate pixels per character for Arial at 35pt
        pixels_per_char = 10 # Adjusted for larger font size

        for word in words:
            word_width = len(word) * pixels_per_char
            if current_width + word_width + pixels_per_char <= max_width:
                current_line.append(word)
                current_width += word_width + pixels_per_char  # Space width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width + pixels_per_char

        if current_line:
            lines.append(" ".join(current_line))

        # Join lines with double newlines for increased spacing
        return "\n\n".join(lines)
    
    def send_weighing_data(self):
        self.action_btn.configure(state="disabled")
        balance_data = self.read_balance_file()

        if not balance_data:
            self.status_label.configure(text="Erreur: Fichier balance non trouvé")
            self.action_btn.configure(state="normal", text="Send",
                                    command=self.send_weighing_data, fg_color="#A2D5F2")
            return

        try:
            # Update displayed weighing values
            self.gross_value.configure(text=f"{balance_data['gross']} g")
            self.net_value.configure(text=f"{balance_data['net']} g")
            self.tare_value.configure(text=f"{balance_data['tare']} g")

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

                if data.get("message") == "Check the weight !":
                    self.clear_screen()
                    self.handle_error("Veuillez vérifier la quantité pesée !")
                    # After 2 seconds, reload initial weighing data
                    self.after(2000, lambda: self.load_weighing_data())
                else:
                    # Success: Keep current UI, update button to Load
                    self.action_btn.configure(state="normal", text="Load",
                                            command=self.load_weighing_data, fg_color="#A2D5F2")
                    
            else:
                self.status_label.configure(text="Veuillez réessayer")
                self.action_btn.configure(state="normal", text="Send",
                                        command=self.send_weighing_data, fg_color="#A2D5F2")

        except requests.exceptions.RequestException:
            self.status_label.configure(text="Veuillez réessayer")
            self.action_btn.configure(state="normal", text="Send",
                                    command=self.send_weighing_data, fg_color="#A2D5F2")
    def read_balance_file(self):
        file_path = (
            "/home/advx/PharMES_python/balance_EXCIPIENT.txt" if self.smartbox_type == "EXCIPIENT"
            else "/home/advx/PharMES_python/balance_PRINCIPE_ACTIF.txt"
        )

        def parse_with_regex(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='cp1252') as f:
                    content = f.read()

            # Date parsing (works for both formats)
            date_match = re.search(
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})',
                content
            )
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
                except ValueError:
                    parsed_date = None

                if parsed_date:
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')

            if self.smartbox_type == "EXCIPIENT":
                # EXCIPIENT parsing
                balance_id_match = re.search(r'Nø r‚f\s+(\w+)', content)
                balance_id = balance_id_match.group(1) if balance_id_match else None

                name_match = re.search(r'Type de balance\s*\n\s*(.+)', content)
                balance_name = name_match.group(1).strip() if name_match else None

                gross_match = re.search(r'[G]\s+([\d.]+)\s*g', content)
                tare_match = re.search(r'[T]\s+([\d.]+)\s*g', content)
                net_match = re.search(r'[N]\s+([\d.]+)\s*g', content)

                gross = float(gross_match.group(1)) if gross_match else None
                tare = float(tare_match.group(1)) if tare_match else None
                net = float(net_match.group(1)) if net_match else None

            elif self.smartbox_type == "PRINCIPE_ACTIF":
                # PRINCIPE_ACTIF parsing - more robust handling
                balance_id = ''
                balance_name = ''

                # Find T (tare) and B (gross) values
                tare_match = re.search(r'T\s+([\d.]+)\s*g', content)
                gross_match = re.search(r'B\s+([\d.]+)\s*g', content)
                
                tare = float(tare_match.group(1)) if tare_match else None
                gross = float(gross_match.group(1)) if gross_match else None

                # Try to find N (net) first
                net_match = re.search(r'N\s+([\d.]+)\s*g', content)
                if net_match:
                    net = float(net_match.group(1))
                else:
                    # If N not found, look for value between T and B
                    lines = content.splitlines()
                    found_t = False
                    net = None
                    
                    for line in lines:
                        if re.search(r'T\s+([\d.]+)\s*g', line):
                            found_t = True
                            continue
                        if re.search(r'B\s+([\d.]+)\s*g', line):
                            break
                        if found_t:
                            # Look for a line with just a number and 'g'
                            value_match = re.search(r'^\s*([\d.]+)\s*g\s*$', line.strip())
                            if value_match:
                                try:
                                    value = float(value_match.group(1))
                                    # Ensure it's not the tare or gross value
                                    if (tare is None or abs(value - tare) > 0.01) and \
                                    (gross is None or abs(value - gross) > 0.01):
                                        net = value
                                        break
                                except ValueError:
                                    pass

            return {
                'date': formatted_date,
                'balance_ID': balance_id,
                'balance_name': balance_name,
                'gross': gross,
                'tare': tare,
                'net': net
            }

        try:
            return parse_with_regex(file_path)
        except Exception as e:
            print(f"Error reading balance file: {e}")
            return None

    def clear_screen(self):
        #Clear all widgets except the close button and action button.
        for widget in self.winfo_children():
            if widget not in [self.close_btn, self.action_btn]:
                widget.destroy()
        # Ensure action button is placed as Load
        self.action_btn.configure(text="Load", command=self.load_weighing_data, fg_color="#A2D5F2")
        self.action_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)