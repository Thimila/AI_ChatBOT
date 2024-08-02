import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from ttkthemes import ThemedTk
from huggingface_hub import InferenceClient
import json

# Constants
MODELS = {
    "Phi-3-mini": "microsoft/Phi-3-mini-4k-instruct",
    "GPT-2": "gpt2",
    "BERT": "bert-base-uncased"
}

class AIChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Enhanced AI Chat Interface")
        self.master.geometry("800x600")
        
        self.style = ttk.Style()
        self.style.theme_use("equilux")
        
        self.create_widgets()
        self.load_settings()
        
        # Initialize Hugging Face client
        self.client = None
        self.initialize_client()

    def create_widgets(self):
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Top frame for query and controls
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="Query:").grid(row=0, column=0, padx=(0, 5))
        self.query_entry = ttk.Entry(top_frame)
        self.query_entry.grid(row=0, column=1, sticky="ew")
        self.query_entry.bind("<Return>", self.get_response)

        send_button = ttk.Button(top_frame, text="Send", command=self.get_response)
        send_button.grid(row=0, column=2, padx=(5, 0))

        # Model selection
        ttk.Label(top_frame, text="Model:").grid(row=0, column=3, padx=(10, 5))
        self.model_var = tk.StringVar(value=list(MODELS.keys())[0])
        model_menu = ttk.OptionMenu(top_frame, self.model_var, list(MODELS.keys())[0], *MODELS.keys())
        model_menu.grid(row=0, column=4)

        # Chat display
        self.response_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.response_display.grid(row=1, column=0, sticky="nsew")

        # Bottom frame for buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        clear_button = ttk.Button(bottom_frame, text="Clear", command=self.clear_conversation)
        clear_button.pack(side=tk.LEFT, padx=(0, 5))

        save_button = ttk.Button(bottom_frame, text="Save", command=self.save_conversation)
        save_button.pack(side=tk.LEFT, padx=5)

        load_button = ttk.Button(bottom_frame, text="Load", command=self.load_conversation)
        load_button.pack(side=tk.LEFT, padx=5)

        settings_button = ttk.Button(bottom_frame, text="Settings", command=self.open_settings)
        settings_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Configure tags for styling
        self.response_display.tag_configure("user", foreground="#4CAF50")
        self.response_display.tag_configure("ai", foreground="#2196F3")

    def get_response(self, event=None):
        user_query = self.query_entry.get()
        if not user_query.strip():
            messagebox.showwarning("Empty Query", "Please enter a query.")
            return

        self.display_message("User", user_query, "user")
        self.query_entry.delete(0, tk.END)

        try:
            response = self.client.chat_completion(
                model=MODELS[self.model_var.get()],
                messages=[{"role": "user", "content": user_query}],
                max_tokens=500,
            )
            ai_response = response.choices[0].message.content
            self.display_message("AI", ai_response, "ai")
        except Exception as e:
            self.display_message("Error", str(e), "ai")

    def display_message(self, sender, message, tag):
        self.response_display.config(state=tk.NORMAL)
        self.response_display.insert(tk.END, f"{sender}: {message}\n\n", tag)
        self.response_display.see(tk.END)
        self.response_display.config(state=tk.DISABLED)

    def clear_conversation(self):
        self.response_display.config(state=tk.NORMAL)
        self.response_display.delete(1.0, tk.END)
        self.response_display.config(state=tk.DISABLED)

    def save_conversation(self):
        conversation = self.response_display.get(1.0, tk.END)
        if not conversation.strip():
            messagebox.showwarning("Empty Conversation", "There is no conversation to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(conversation)
            messagebox.showinfo("Conversation Saved", "The conversation has been saved successfully.")

    def load_conversation(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                conversation = file.read()
            self.clear_conversation()
            self.response_display.config(state=tk.NORMAL)
            self.response_display.insert(tk.END, conversation)
            self.response_display.config(state=tk.DISABLED)

    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("300x150")

        ttk.Label(settings_window, text="Hugging Face Token:").pack(pady=(10, 5))
        token_entry = ttk.Entry(settings_window, show="*")
        token_entry.pack(pady=5)
        token_entry.insert(0, self.settings.get("huggingface_token", ""))

        save_button = ttk.Button(settings_window, text="Save", command=lambda: self.save_settings(token_entry.get()))
        save_button.pack(pady=10)

    def save_settings(self, token):
        self.settings["huggingface_token"] = token
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)
        self.initialize_client()
        messagebox.showinfo("Settings Saved", "Your settings have been saved.")

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}

    def initialize_client(self):
        token = self.settings.get("huggingface_token")
        if token:
            self.client = InferenceClient(token=token)
        else:
            messagebox.showwarning("Missing Token", "Please set your Hugging Face token in the settings.")

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = AIChatApp(root)
    root.mainloop()