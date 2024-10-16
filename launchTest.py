import tkinter as tk
from tkinter import messagebox

def on_click():
    messagebox.showinfo("Message", "Hello, World!")

def main():
    root = tk.Tk()
    root.title("My GUI App")
    root.geometry("300x200")
    
    label = tk.Label(root, text="Click the button to see a message:")
    label.pack(pady=10)
    
    button = tk.Button(root, text="Click Me", command=on_click)
    button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
