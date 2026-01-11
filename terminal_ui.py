# Terminal User Interface Implementation
import tkinter as tk
from tkinter import scrolledtext, font, filedialog, messagebox
from filesystem import LocalFileSystem
from command_parser import CommandParser


class TerminalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unix Terminal By RXS Studios")
        self.root.geometry("900x700")
        self.root.configure(bg='#000000')

        #Set window icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
            # fallback: continue without icon if file not found
        
        # Terminal colors
        self.bg_color = '#000000'
        self.fg_color = '#ffffff'
        self.prompt_color = '#00ff00'
        self.error_color = '#ff0000'
        self.info_color = '#00aaff'
        
        # Prompt for working directory selection
        messagebox.showinfo(
            "Select Working Directory",
            "Please select a working directory.\n\nAll commands will operate only within this directory."
        )
        
        base_directory = filedialog.askdirectory(title="Select Working Directory")
        if not base_directory:
            # User cancelled - exit
            root.quit()
            return
        
        # Initialize filesystem with selected directory
        try:
            self.filesystem = LocalFileSystem(base_directory)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize filesystem: {e}")
            root.quit()
            return
        
        # Current directory
        self.username = 'user'
        self.hostname = 'terminal'
        
        # Command history
        self.command_history = []
        self.history_index = -1
        # Session transcript (prompt+command and outputs)
        self.session_log = []
        # Inline input mode (type directly in the terminal area)
        self.inline_input = True
        self.input_start_index = None
        # Widgets for bottom input mode (created lazily if needed)
        self.input_frame = None
        self.input_entry = None
        self.prompt_label = None
        
        # Initialize UI
        self.setup_ui()
        self.setup_command_parser()
        
        # Focus on input
        if not self.inline_input:
            self.input_entry.focus_set()
        
        # Display welcome message
        self.display_welcome()
    
    def setup_ui(self):

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Terminal display area
        self.terminal_display = scrolledtext.ScrolledText(
            main_frame,
            height=35,
            width=110,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground='#404040',
            selectforeground=self.fg_color,
            font=('Courier New', 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.terminal_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for different colors
        self.terminal_display.tag_configure('prompt', foreground=self.prompt_color)
        self.terminal_display.tag_configure('error', foreground=self.error_color)
        self.terminal_display.tag_configure('output', foreground=self.fg_color)
        self.terminal_display.tag_configure('info', foreground=self.info_color)
        
        if self.inline_input:
            # Inline input bindings on the text widget
            self.terminal_display.bind('<Return>', self.inline_return)
            self.terminal_display.bind('<BackSpace>', self.inline_backspace)
            self.terminal_display.bind('<Left>', self.inline_left)
            self.terminal_display.bind('<Home>', self.inline_home)
            self.terminal_display.bind('<Button-1>', self.inline_click)
            self.terminal_display.bind('<Up>', self.inline_history_up)
            self.terminal_display.bind('<Down>', self.inline_history_down)
            self.terminal_display.bind('<Tab>', self.inline_tab)
            self.root.bind('<Control-c>', self.clear_input)
        else:
            # Input frame
            input_frame = tk.Frame(main_frame, bg=self.bg_color)
            input_frame.pack(fill=tk.X)
            # Prompt label
            self.prompt_label = tk.Label(
                input_frame,
                text=self.get_prompt(),
                bg=self.bg_color,
                fg=self.prompt_color,
                font=('Courier New', 10)
            )
            self.prompt_label.pack(side=tk.LEFT)
            # Command input entry
            self.input_entry = tk.Entry(
                input_frame,
                bg=self.bg_color,
                fg=self.fg_color,
                insertbackground=self.fg_color,
                font=('Courier New', 10),
                relief=tk.FLAT,
                highlightthickness=0
            )
            self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            # Bind events
            self.input_entry.bind('<Return>', self.process_command)
            self.input_entry.bind('<Up>', self.history_up)
            self.input_entry.bind('<Down>', self.history_down)
            self.input_entry.bind('<Tab>', self.tab_completion)
            self.root.bind('<Control-c>', self.clear_input)
    
    def get_prompt(self):
        current_dir = self.filesystem.current_path
        if current_dir == f"/home/{self.username}":
            current_dir = "~"
        return f"{self.username}@{self.hostname}:{current_dir}$ "
    
    def display_welcome(self):
        welcome_text = f"""Welcome to Unix Terminal v2.0
Running on Python with tkinter

Working directory: {self.filesystem.base_path}
Current directory: {self.filesystem.current_path}

Type 'help' to see available commands.
Type 'ls' to list files, 'cd' to change directory.
Type 'exit' to quit.

"""
        self.print_to_terminal(welcome_text, 'info')
        self.show_prompt()
    
    def print_to_terminal(self, text, tag='output'):
        """Print text to terminal display with specified tag/color"""
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.insert(tk.END, text, tag)
        self.terminal_display.config(state=tk.DISABLED)
        self.terminal_display.see(tk.END)  # Auto-scroll to bottom
    
    def show_prompt(self):
        """Display the command prompt"""
        if self.inline_input:
            prompt = self.get_prompt()
            self.terminal_display.config(state=tk.NORMAL)
            self.terminal_display.insert(tk.END, prompt, 'prompt')
            self.terminal_display.see(tk.END)
            self.input_start_index = self.terminal_display.index(tk.INSERT)
        else:
            prompt = self.get_prompt()
            self.prompt_label.config(text=prompt)
    
    def process_command(self, event):
        """Process the entered command"""
        command = self.input_entry.get().strip()
        
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display the command with prompt
        full_command_line = f"{self.get_prompt()}{command}\n"
        self.print_to_terminal(full_command_line, 'prompt')
        # Record command line in session log
        self.session_log.append(full_command_line.rstrip('\n'))
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        # Execute
        self.execute_command(command)
        
        # Update prompt in case directory changed
        self.show_prompt()
    
    def tab_completion(self, event):
        """Basic tab completion for file/directory names"""
        current_text = self.input_entry.get()
        if not current_text:
            return "break"
        
        parts = current_text.split()
        if len(parts) == 0:
            return "break"
        
        # Get the last part for completion
        last_part = parts[-1] if parts else ""
        
        # Get directory contents for completion
        files = self.filesystem.list_directory()
        if files:
            matches = [f for f in files if f.startswith(last_part)]
            if len(matches) == 1:
                # Single match - complete it
                if len(parts) > 1:
                    completed = " ".join(parts[:-1]) + " " + matches[0]
                else:
                    completed = matches[0]
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, completed)
        
        return "break"
    
    def history_up(self, event):
        """Navigate command history up"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
    
    def history_down(self, event):
        """Navigate command history down"""
        if self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, self.command_history[self.history_index])
            elif self.history_index == len(self.command_history) - 1:
                self.history_index = len(self.command_history)
                self.input_entry.delete(0, tk.END)
    
    def clear_input(self, event):
        """Clear the input field (Ctrl+C)"""
        if self.inline_input:
            # Move cursor to end and clear current input region
            if self.input_start_index is not None:
                self.terminal_display.delete(self.input_start_index, tk.END)
        else:
            self.input_entry.delete(0, tk.END)
    
    def setup_command_parser(self):
        """Initialize the command parser"""
        self.command_parser = CommandParser(self)
        # Expose a toggle command via parser by attaching a method
        # (Implemented in CommandParser; uses this UI's set_input_mode)

    # ---------------- Mode switching ----------------
    def set_input_mode(self, mode=None):
        """Switch between 'inline' and 'bottom' input modes. If mode is None, toggle."""
        target = mode
        if target is None:
            target = 'bottom' if self.inline_input else 'inline'
        if target == 'inline' and not self.inline_input:
            self.enable_inline_mode()
        elif target == 'bottom' and self.inline_input:
            self.enable_bottom_mode()

    def enable_inline_mode(self):
        # Hide bottom input if exists
        if self.input_frame is not None:
            self.input_frame.pack_forget()
        self.inline_input = True
        # Bind inline handlers
        self.terminal_display.bind('<Return>', self.inline_return)
        self.terminal_display.bind('<BackSpace>', self.inline_backspace)
        self.terminal_display.bind('<Left>', self.inline_left)
        self.terminal_display.bind('<Home>', self.inline_home)
        self.terminal_display.bind('<Button-1>', self.inline_click)
        self.terminal_display.bind('<Up>', self.inline_history_up)
        self.terminal_display.bind('<Down>', self.inline_history_down)
        self.terminal_display.bind('<Tab>', self.inline_tab)
        # Show a fresh prompt
        self.show_prompt()

    def enable_bottom_mode(self):
        # Unbind inline handlers
        for seq in ('<Return>','<BackSpace>','<Left>','<Home>','<Button-1>','<Up>','<Down>','<Tab>'):
            try:
                self.terminal_display.unbind(seq)
            except Exception:
                pass
        self.inline_input = False
        # Create input widgets if missing and pack
        if self.input_frame is None:
            # main_frame is parent of text widget; get its master
            main_frame = self.terminal_display.master
            input_frame = tk.Frame(main_frame, bg=self.bg_color)
            input_frame.pack(fill=tk.X)
            self.prompt_label = tk.Label(
                input_frame,
                text=self.get_prompt(),
                bg=self.bg_color,
                fg=self.prompt_color,
                font=('Courier New', 10)
            )
            self.prompt_label.pack(side=tk.LEFT)
            self.input_entry = tk.Entry(
                input_frame,
                bg=self.bg_color,
                fg=self.fg_color,
                insertbackground=self.fg_color,
                font=('Courier New', 10),
                relief=tk.FLAT,
                highlightthickness=0
            )
            self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            self.input_frame = input_frame
            self.input_entry.bind('<Return>', self.process_command)
            self.input_entry.bind('<Up>', self.history_up)
            self.input_entry.bind('<Down>', self.history_down)
            self.input_entry.bind('<Tab>', self.tab_completion)
        else:
            self.input_frame.pack(fill=tk.X)
        self.show_prompt()
        self.input_entry.focus_set()

    # ---------------- Inline input handlers ----------------
    def get_current_inline_input(self):
        if self.input_start_index is None:
            return ""
        return self.terminal_display.get(self.input_start_index, tk.END).rstrip('\n')

    def set_current_inline_input(self, text):
        if self.input_start_index is None:
            return
        self.terminal_display.delete(self.input_start_index, tk.END)
        self.terminal_display.insert(tk.END, text)
        self.terminal_display.see(tk.END)

    def inline_return(self, event):
        command = self.get_current_inline_input().strip()
        # Echo newline
        self.terminal_display.insert(tk.END, "\n")
        # Display echoed command in session log (prompt + command already printed)
        if command:
            pass
        self.execute_command(command)
        # New prompt
        self.show_prompt()
        return "break"

    def inline_backspace(self, event):
        # Prevent deleting before prompt
        if self.input_start_index is None:
            return "break"
        if self.terminal_display.compare(tk.INSERT, "<=", self.input_start_index):
            return "break"
        return None

    def inline_left(self, event):
        if self.input_start_index is None:
            return "break"
        # If moving left would go before prompt, block
        if self.terminal_display.compare(tk.INSERT, "<=", self.input_start_index):
            return "break"
        return None

    def inline_home(self, event):
        if self.input_start_index is not None:
            self.terminal_display.mark_set(tk.INSERT, self.input_start_index)
        return "break"

    def inline_click(self, event):
        # Force cursor to end if clicking above prompt
        if self.input_start_index is not None:
            index = self.terminal_display.index(f"@{event.x},{event.y}")
            if self.terminal_display.compare(index, "<", self.input_start_index):
                self.terminal_display.mark_set(tk.INSERT, tk.END)
                return "break"
        return None

    def inline_history_up(self, event):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.set_current_inline_input(self.command_history[self.history_index])
        return "break"

    def inline_history_down(self, event):
        if self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.set_current_inline_input(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.set_current_inline_input("")
        return "break"

    def inline_tab(self, event):
        # Basic completion using current directory
        partial = self.get_current_inline_input().split()[-1] if self.get_current_inline_input().split() else ""
        files = self.filesystem.list_directory()
        if files:
            matches = [f for f in files if f.startswith(partial)]
            if len(matches) == 1:
                current = self.get_current_inline_input().split()
                if current:
                    current[-1] = matches[0]
                    self.set_current_inline_input(" ".join(current))
                else:
                    self.set_current_inline_input(matches[0])
        return "break"

    def execute_command(self, command):
        if not command:
            return
        # Add history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        # Record command (prompt + command already in text for inline; here add for session log)
        if self.inline_input:
            self.session_log.append(f"{self.get_prompt()}{command}")
        # Run
        try:
            output = self.command_parser.parse_command(command)
            if output:
                self.print_to_terminal(f"{output}\n", 'output')
                self.session_log.append(output)
        except Exception as e:
            self.print_to_terminal(f"Error: {str(e)}\n", 'error')
            self.session_log.append(f"Error: {str(e)}")
