import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from huggingface_hub import InferenceClient
import time

# Replace 'hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' with your actual Hugging Face token
huggingface_token = "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"

client = InferenceClient(
    model="microsoft/Phi-3-mini-4k-instruct",
    token=huggingface_token,
)

def get_response():
    user_query = query_entry.get()
    if not user_query.strip():
        messagebox.showwarning("Empty Query", "Please enter a query.")
        return

    messages = [{"role": "user", "content": user_query}]
    response_text = ""

    try:
        for message in client.chat_completion(
            messages=messages,
            max_tokens=500,
            stream=True,
        ):
            response_text += message.choices[0].delta.content
    except Exception as e:
        response_text = f"Error: {str(e)}"

    display_response(user_query, response_text)
    query_entry.delete(0, tk.END)

def display_response(user_query, response_text):
    response_display.config(state=tk.NORMAL)
    response_display.insert(tk.END, f"User: {user_query}\n(((T))) AI: ", "user")
    response_display.config(state=tk.DISABLED)

    window.after(100, type_response, response_text, 0)

def type_response(response_text, index):
    if index < len(response_text):
        response_display.config(state=tk.NORMAL)
        response_display.insert(tk.END, response_text[index], "ai")
        response_display.config(state=tk.DISABLED)
        index += 1
        window.after(30, type_response, response_text, index)
    else:
        response_display.insert(tk.END, "\n\n")
        response_display.config(state=tk.DISABLED)

def clear_conversation():
    response_display.config(state=tk.NORMAL)
    response_display.delete(1.0, tk.END)
    response_display.config(state=tk.DISABLED)

def save_conversation():
    conversation = response_display.get(1.0, tk.END)
    if not conversation.strip():
        messagebox.showwarning("Empty Conversation", "There is no conversation to save.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"),
                                                        ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(conversation)
        messagebox.showinfo("Conversation Saved", "The conversation has been saved successfully.")

# Set up the tkinter window
window = tk.Tk()
window.title("(((T))) AI Chat Interface")
window.geometry("600x400")

# Apply some styling
style = {
    "font": ("Helvetica", 12),
    "bg": "#f0f0f0",
    "padx": 5,
    "pady": 5
}

# Create and place the widgets
frame = tk.Frame(window, bg=style["bg"])
frame.pack(pady=10)

query_label = tk.Label(frame, text="Enter your query:", **style)
query_label.grid(row=0, column=0, padx=5)

query_entry = tk.Entry(frame, width=50, font=style["font"])
query_entry.grid(row=0, column=1, padx=5)

send_button = tk.Button(frame, text="Send", command=get_response, font=style["font"], bg="#4CAF50", fg="white")
send_button.grid(row=0, column=2, padx=5)

response_display = scrolledtext.ScrolledText(window, width=70, height=20, state=tk.DISABLED, font=style["font"], bg="white")
response_display.pack(pady=10)

button_frame = tk.Frame(window, bg=style["bg"])
button_frame.pack(pady=5)

clear_button = tk.Button(button_frame, text="Clear", command=clear_conversation, font=style["font"], bg="#f44336", fg="white")
clear_button.grid(row=0, column=0, padx=10)

save_button = tk.Button(button_frame, text="Save", command=save_conversation, font=style["font"], bg="#008CBA", fg="white")
save_button.grid(row=0, column=1, padx=10)

# Add tags for styling
response_display.tag_configure("user", foreground="blue")
response_display.tag_configure("ai", foreground="green")

# Start the tkinter main loop
window.mainloop()
