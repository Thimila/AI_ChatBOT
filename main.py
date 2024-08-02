import tkinter as tk
from tkinter import scrolledtext
from huggingface_hub import InferenceClient

# Replace 'your_huggingface_token' with your actual Hugging Face token
huggingface_token = "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"

client = InferenceClient(
    model="microsoft/Phi-3-mini-4k-instruct",
    token=huggingface_token,
)

def get_response():
    user_query = query_entry.get()
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

    response_display.config(state=tk.NORMAL)
    response_display.insert(tk.END, f"User: {user_query}\nBot: {response_text}\n\n")
    response_display.config(state=tk.DISABLED)

# Set up the tkinter window
window = tk.Tk()
window.title("Chatbot Interface")

# Create and place the widgets
query_label = tk.Label(window, text="Enter your query:")
query_label.pack()

query_entry = tk.Entry(window, width=50)
query_entry.pack()

send_button = tk.Button(window, text="Send", command=get_response)
send_button.pack()

response_display = scrolledtext.ScrolledText(window, width=60, height=20, state=tk.DISABLED)
response_display.pack()

# Start the tkinter main loop
window.mainloop()
