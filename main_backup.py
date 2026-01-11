# Unix-Linux-terminal

import tkinter as tk
from tkinter import scrolledtext, font
import json
import os
import datetime
from pathlib import Path

class MockFileSystem:
    """Mock file system implementation using JSON structure"""
    
    def __init__(self):
        self.fs_file = "mock_filesystem.json"
        self.current_path = "/home/student"
        self.initialize_filesystem()
    
    def initialize_filesystem(self):
        """Initialize the mock file system structure"""
        default_fs = {
            "/": {
                "type": "directory",
                "contents": {
                    "home": {
                        "type": "directory",
                        "contents": {
                            "student": {
                                "type": "directory",
                                "contents": {
                                    "documents": {
                                        "type": "directory",
                                        "contents": {
                                            "readme.txt": {
                                                "type": "file",
                                                "content": "Welcome to the OS Simulator!\nThis is a sample text file.\nYou can use 'cat' to read files.",
                                                "size": 95,
                                                "modified": "2024-01-15 10:30:00"
                                            },
                                            "notes.txt": {
                                                "type": "file",
                                                "content": "Study notes:\n- CPU Scheduling algorithms\n- Memory management\n- Deadlock prevention",
                                                "size": 85,
                                                "modified": "2024-01-10 14:20:00"
                                            }
                                        }
                                    },
                                    "projects": {
                                        "type": "directory",
                                        "contents": {
                                            "os_assignment.py": {
                                                "type": "file",
                                                "content": "# OS Assignment - CPU Scheduling\n\ndef round_robin(processes, quantum):\n    # Implementation here\n    pass",
                                                "size": 120,
                                                "modified": "2024-01-20 16:45:00"
                                            }
                                        }
                                    },
                                    "welcome.txt": {
                                        "type": "file",
                                        "content": "Hello! Welcome to your home directory.\nFeel free to explore the file system using commands like ls, cd, and cat.",
                                        "size": 108,
                                        "modified": "2024-01-01 12:00:00"
                                    }
                                }
                            }
                        }
                    },
                    "etc": {
                        "type": "directory",
                        "contents": {
                            "hosts": {
                                "type": "file",
                                "content": "127.0.0.1\tlocalhost\n127.0.1.1\tsimulator",
                                "size": 35,
                                "modified": "2024-01-01 10:00:00"
                            }
                        }
                    },
                    "var": {
                        "type": "directory",
                        "contents": {
                            "log": {
                                "type": "directory",
                                "contents": {}
                            }
                        }
                    }
                }
            }
        }
        
        # Load existing filesystem or create default
        if os.path.exists(self.fs_file):
            try:
                with open(self.fs_file, 'r') as f:
                    self.filesystem = json.load(f)
            except:
                self.filesystem = default_fs
                self.save_filesystem()
        else:
            self.filesystem = default_fs
            self.save_filesystem()
    
    def save_filesystem(self):
        """Save the current filesystem state"""
        try:
            with open(self.fs_file, 'w') as f:
                json.dump(self.filesystem, f, indent=2)
        except Exception as e:
            print(f"Error saving filesystem: {e}")
    
    def normalize_path(self, path):
        """Normalize a path (resolve .. and . components)"""
        if not path.startswith('/'):
            # Relative path
            path = self.current_path + '/' + path
        
        # Split path and resolve . and ..
        parts = [p for p in path.split('/') if p]
        normalized = []
        
        for part in parts:
            if part == '.':
                continue
            elif part == '..':
                if normalized:
                    normalized.pop()
            else:
                normalized.append(part)
        
        result = '/' + '/'.join(normalized) if normalized else '/'
        return result
    
    def get_node(self, path):
        """Get a filesystem node by path"""
        path = self.normalize_path(path)
        
        if path == '/':
            return self.filesystem['/']
        
        parts = [p for p in path.split('/') if p]
        current = self.filesystem['/']
        
        try:
            for part in parts:
                if current['type'] != 'directory':
                    return None
                if part not in current['contents']:
                    return None
                current = current['contents'][part]
            return current
        except:
            return None
    
    def list_directory(self, path=None):
        """List directory contents"""
        if path is None:
            path = self.current_path
        
        node = self.get_node(path)
        if not node:
            return None
        
        if node['type'] != 'directory':
            return None
        
        return list(node['contents'].keys())
    
    def change_directory(self, path):
        """Change current directory"""
        if path == '~':
            path = '/home/student'
        
        target_path = self.normalize_path(path)
        node = self.get_node(target_path)
        
        if not node:
            return False, f"cd: {path}: No such file or directory"
        
        if node['type'] != 'directory':
            return False, f"cd: {path}: Not a directory"
        
        self.current_path = target_path
        return True, ""
    
    def read_file(self, path):
        """Read file contents"""
        node = self.get_node(path)
        if not node:
            return None, f"cat: {path}: No such file or directory"
        
        if node['type'] != 'file':
            return None, f"cat: {path}: Is a directory"
        
        return node['content'], ""
    
    def create_file(self, path, content=""):
        """Create a new file"""
        path = self.normalize_path(path)
        dir_path = '/'.join(path.split('/')[:-1]) or '/'
        filename = path.split('/')[-1]
        
        parent_node = self.get_node(dir_path)
        if not parent_node or parent_node['type'] != 'directory':
            return False, f"touch: cannot touch '{path}': No such file or directory"
        
        # Create the file
        parent_node['contents'][filename] = {
            "type": "file",
            "content": content,
            "size": len(content),
            "modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_filesystem()
        return True, ""
    
    def remove_file(self, path):
        """Remove a file or directory"""
        path = self.normalize_path(path)
        dir_path = '/'.join(path.split('/')[:-1]) or '/'
        filename = path.split('/')[-1]
        
        parent_node = self.get_node(dir_path)
        if not parent_node or parent_node['type'] != 'directory':
            return False, f"rm: cannot remove '{path}': No such file or directory"
        
        if filename not in parent_node['contents']:
            return False, f"rm: cannot remove '{path}': No such file or directory"
        
        target_node = parent_node['contents'][filename]
        if target_node['type'] == 'directory' and target_node['contents']:
            return False, f"rm: cannot remove '{path}': Directory not empty"
        
        del parent_node['contents'][filename]
        self.save_filesystem()
        return True, ""
    
    def get_detailed_listing(self, path=None):
        """Get detailed directory listing (for ls -l)"""
        if path is None:
            path = self.current_path
        
        node = self.get_node(path)
        if not node or node['type'] != 'directory':
            return None
        
        items = []
        for name, item in node['contents'].items():
            if item['type'] == 'directory':
                permissions = 'drwxr-xr-x'
                size = '-'
            else:
                permissions = '-rw-r--r--'
                size = str(item.get('size', 0))
            
            modified = item.get('modified', '2024-01-01 12:00:00')
            items.append({
                'name': name,
                'permissions': permissions,
                'size': size,
                'modified': modified,
                'type': item['type']
            })
        
        return items


class TerminalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux OS Simulator")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        # Terminal colors
        self.bg_color = '#1e1e1e'
        self.fg_color = '#ffffff'
        self.prompt_color = '#00ff00'
        self.error_color = '#ff0000'
        self.info_color = '#00aaff'
        
        # Initialize filesystem
        self.filesystem = MockFileSystem()
        
        # Current directory simulation
        self.username = 'student'
        self.hostname = 'simulator'
        
        # Command history
        self.command_history = []
        self.history_index = -1
        
        # Initialize UI
        self.setup_ui()
        self.setup_command_parser()
        
        # Focus on input
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
        welcome_text = f"""Welcome to Linux OS Simulator v2.0
Running on Python with tkinter - Now with File System!

Type 'help' to see available commands.
Type 'ls' to list files, 'cd' to change directory.
Type 'exit' to quit the simulator.

Current directory: {self.filesystem.current_path}

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
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        # Process command
        try:
            output = self.command_parser.parse_command(command)
            if output:
                self.print_to_terminal(f"{output}\n", 'output')
        except Exception as e:
            self.print_to_terminal(f"Error: {str(e)}\n", 'error')
        
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
        self.input_entry.delete(0, tk.END)
    
    def setup_command_parser(self):
        """Initialize the command parser"""
        self.command_parser = CommandParser(self)


class CommandParser:
    def __init__(self, terminal_ui):
        self.terminal_ui = terminal_ui
        self.filesystem = terminal_ui.filesystem
        
        # Available commands
        self.commands = {
            'help': self.cmd_help,
            'echo': self.cmd_echo,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'whoami': self.cmd_whoami,
            'date': self.cmd_date,
            'uptime': self.cmd_uptime,
            'pwd': self.cmd_pwd,
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'cat': self.cmd_cat,
            'touch': self.cmd_touch,
            'rm': self.cmd_rm,
            'man': self.cmd_man
        }
        
        # Manual pages for commands
        self.manual_pages = {
            'ls': """NAME
    ls - list directory contents

SYNOPSIS
    ls [OPTION]... [FILE]...

DESCRIPTION
    List information about the FILEs (the current directory by default).

OPTIONS
    -l     use a long listing format
    -a     do not ignore entries starting with .

EXAMPLES
    ls          list current directory
    ls -l       detailed list with permissions and dates
    ls /home    list /home directory""",

            'cd': """NAME
    cd - change directory

SYNOPSIS
    cd [DIRECTORY]

DESCRIPTION
    Change the current working directory to DIRECTORY.
    If no DIRECTORY is given, change to home directory.

EXAMPLES
    cd          change to home directory
    cd ..       change to parent directory
    cd /etc     change to /etc directory""",

            'cat': """NAME
    cat - display file contents

SYNOPSIS
    cat [FILE]...

DESCRIPTION
    Display the contents of FILE(s) to standard output.

EXAMPLES
    cat file.txt        display contents of file.txt
    cat file1 file2     display contents of multiple files""",

            'pwd': """NAME
    pwd - print working directory

SYNOPSIS
    pwd

DESCRIPTION
    Print the full pathname of the current working directory.""",

            'touch': """NAME
    touch - create empty files

SYNOPSIS
    touch FILE...

DESCRIPTION
    Create empty FILE(s) if they do not exist.

EXAMPLES
    touch newfile.txt       create newfile.txt
    touch file1 file2       create multiple files""",

            'rm': """NAME
    rm - remove files and directories

SYNOPSIS
    rm [FILE]...

DESCRIPTION
    Remove (unlink) the FILE(s).

EXAMPLES
    rm file.txt         remove file.txt
    rm file1 file2      remove multiple files"""
        }
    
    def parse_command(self, command_line):
        """Parse and execute a command"""
        if not command_line.strip():
            return ""
        
        # Split command and arguments
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check if command exists
        if command in self.commands:
            return self.commands[command](args)
        else:
            return f"bash: {command}: command not found"
    
    def cmd_help(self, args):
        """Display available commands"""
        help_text = """Available commands:

File System Commands:
  ls       - List directory contents (use -l for detailed view)
  cd       - Change directory
  pwd      - Print current directory
  cat      - Display file contents
  touch    - Create empty files
  rm       - Remove files

Basic Commands:
  help     - Show this help message
  echo     - Display text (usage: echo <text>)
  clear    - Clear the terminal screen
  whoami   - Display current username
  date     - Show current date and time
  uptime   - Show system uptime simulation
  man      - Show manual page for command (usage: man <command>)
  exit     - Exit the simulator

Navigation:
  Up/Down arrows - Navigate command history
  Tab            - Auto-complete file names
  Ctrl+C         - Clear current input

Examples:
  ls -l documents/
  cd /home/student/documents
  cat welcome.txt
  man ls
"""
        return help_text
    
    def cmd_echo(self, args):
        """Echo command - display text"""
        if not args:
            return ""
        return " ".join(args)
    
    def cmd_clear(self, args):
        """Clear the terminal screen"""
        self.terminal_ui.terminal_display.config(state=tk.NORMAL)
        self.terminal_ui.terminal_display.delete(1.0, tk.END)
        self.terminal_ui.terminal_display.config(state=tk.DISABLED)
        return ""
    
    def cmd_exit(self, args):
        """Exit the simulator"""
        self.terminal_ui.root.quit()
        return "Goodbye!"
    
    def cmd_whoami(self, args):
        """Display current username"""
        return self.terminal_ui.username
    
    def cmd_date(self, args):
        """Display current date and time"""
        return datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    
    def cmd_uptime(self, args):
        """Simulate uptime command"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"{current_time} up 1:23, 1 user, load average: 0.15, 0.12, 0.08"
    
    def cmd_pwd(self, args):
        """Print working directory"""
        return self.filesystem.current_path
    
    def cmd_ls(self, args):
        """List directory contents"""
        show_details = '-l' in args
        show_all = '-a' in args
        
        # Remove flags to get path
        path_args = [arg for arg in args if not arg.startswith('-')]
        target_path = path_args[0] if path_args else None
        
        if show_details:
            items = self.filesystem.get_detailed_listing(target_path)
            if items is None:
                path = target_path or self.filesystem.current_path
                return f"ls: cannot access '{path}': No such file or directory"
            
            if not items:
                return ""
            
            # Format detailed listing
            result = []
            for item in sorted(items, key=lambda x: x['name']):
                result.append(f"{item['permissions']} 1 {self.terminal_ui.username} {self.terminal_ui.username} {item['size']:>8} {item['modified']} {item['name']}")
            
            return "\n".join(result)
        else:
            files = self.filesystem.list_directory(target_path)
            if files is None:
                path = target_path or self.filesystem.current_path
                return f"ls: cannot access '{path}': No such file or directory"
            
            if not files:
                return ""
            
            # Simple listing (columns)
            files.sort()
            if len(files) <= 4:
                return "  ".join(files)
            else:
                # Multi-column display
                cols = 3
                rows = (len(files) + cols - 1) // cols
                result = []
                for row in range(rows):
                    line = []
                    for col in range(cols):
                        idx = col * rows + row
                        if idx < len(files):
                            line.append(f"{files[idx]:<20}")
                    result.append("".join(line).rstrip())
                return "\n".join(result)
    
    def cmd_cd(self, args):
        """Change directory"""
        if not args:
            # Change to home directory
            target = f"/home/{self.terminal_ui.username}"
        else:
            target = args[0]
        
        success, error = self.filesystem.change_directory(target)
        if not success:
            return error
        return ""
    
    def cmd_cat(self, args):
        """Display file contents"""
        if not args:
            return "cat: missing file operand"
        
        results = []
        for filename in args:
            content, error = self.filesystem.read_file(filename)
            if error:
                results.append(error)
            else:
                results.append(content)
        
        return "\n".join(results)
    
    def cmd_touch(self, args):
        """Create empty files"""
        if not args:
            return "touch: missing file operand"
        
        results = []
        for filename in args:
            success, error = self.filesystem.create_file(filename)
            if error:
                results.append(error)
        
        return "\n".join(results) if results else ""
    
    def cmd_rm(self, args):
        """Remove files"""
        if not args:
            return "rm: missing operand"
        
        results = []
        for filename in args:
            success, error = self.filesystem.remove_file(filename)
            if error:
                results.append(error)
        
        return "\n".join(results) if results else ""
    
    def cmd_man(self, args):
        """Display manual page for command"""
        if not args:
            return "What manual page do you want?"
        
        command = args[0].lower()
        if command in self.manual_pages:
            return self.manual_pages[command]
        elif command in self.commands:
            return f"No manual entry for {command}"
        else:
            return f"No manual entry for {command}"


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
