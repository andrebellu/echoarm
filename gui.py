import customtkinter as ctk
import socket
import threading
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EchoArmGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pannello Controllo Camera")
        self.geometry("550x650")
        self.resizable(False, False)

        self.HOST = '127.0.0.1'
        self.PORT = 65432

        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=20, pady=(20, 0))

        self.conn_status_label = ctk.CTkLabel(
            self.top_bar, 
            text="CONNESSIONE: VERIFICA...", 
            text_color="gray", 
            font=("Roboto", 12, "bold")
        )
        self.conn_status_label.pack(side="right")

        self.title_label = ctk.CTkLabel(self.top_bar, text="ECHOARM TEST GUI", font=("Roboto Medium", 24))
        self.title_label.pack(side="left")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=30)

        self.create_button("TESTA", "TESTA", 0, 1)

        self.create_button("Braccio\nSinistro", "BRACCIO_SX", 1, 0)
        self.create_button("TORACE", "TORACE", 1, 1)
        self.create_button("Braccio\nDestro", "BRACCIO_DX", 1, 2)

        self.create_button("ADDOME", "ADDOME", 2, 1)

        self.create_button("GAMBE", "GAMBE", 3, 1)

        self.separator = ctk.CTkProgressBar(self, width=450, height=2)
        self.separator.set(1)
        self.separator.pack(pady=10, side="bottom")

        self.log_label = ctk.CTkLabel(self, text="Attesa comandi...", font=("Roboto", 12), text_color="gray")
        self.log_label.pack(pady=(0, 10), side="bottom")

        self.check_connection_loop()

    def create_button(self, display_text, command_text, r, c):
        btn = ctk.CTkButton(
            self.main_frame, 
            text=display_text, 
            width=150, 
            height=60, 
            font=("Roboto", 14),
            command=lambda: self.send_command(display_text, command_text)
        )
        btn.grid(row=r, column=c, padx=10, pady=10)

    def check_connection_loop(self):
        threading.Thread(target=self._check_socket, daemon=True).start()
        self.after(3000, self.check_connection_loop)

    def _check_socket(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                result = s.connect_ex((self.HOST, self.PORT))
                if result == 0:
                    self.after(0, lambda: self.conn_status_label.configure(text="● CONNESSO", text_color="#32CD32"))
                else:
                    self.after(0, lambda: self.conn_status_label.configure(text="● DISCONNESSO", text_color="#CD5C5C"))
        except:
            self.after(0, lambda: self.conn_status_label.configure(text="● ERRORE", text_color="#CD5C5C"))

    def send_command(self, display_text, command_to_send):
        body_part_clean = display_text.replace("\n", " ") 
        self.log_label.configure(text=f"Invio richiesta: {body_part_clean}...", text_color="orange")
        self.update()
        
        threading.Thread(target=self._socket_worker, args=(command_to_send,)).start()

    def _socket_worker(self, command_to_send):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((self.HOST, self.PORT))
                s.sendall(command_to_send.encode('utf-8'))
                
                self.after(0, lambda: self.log_label.configure(
                    text=f"✅ Target inviato: {command_to_send}", text_color="#32CD32"
                ))
                
        except (ConnectionRefusedError, socket.timeout):
            self.after(0, lambda: self.log_label.configure(
                text="❌ Errore connessione", text_color="#CD5C5C"
            ))
        except Exception as e:
            self.after(0, lambda: self.log_label.configure(
                text=f"❌ Errore: {str(e)}", text_color="#CD5C5C"
            ))

if __name__ == "__main__":
    app = EchoArmGUI()
    app.mainloop()