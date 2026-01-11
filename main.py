# Unix-Linux-terminal - Main Entry Point

import tkinter as tk
from terminal_ui import TerminalUI


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = TerminalUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()
