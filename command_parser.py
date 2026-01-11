# Enhanced Command Parser Implementation with Local Filesystem Support
import tkinter as tk
from tkinter import filedialog, messagebox
import datetime
import re
import os
import shutil
import calendar
import zlib


class CommandParser:
    def __init__(self, terminal_ui):
        self.terminal_ui = terminal_ui
        self.filesystem = terminal_ui.filesystem
        
        # Simple process table
        self.process_table = [
            {'pid': 101, 'user': self.terminal_ui.username, 'cmd': 'bash', 'cpu': 0.1, 'mem': 0.5},
            {'pid': 202, 'user': self.terminal_ui.username, 'cmd': 'python', 'cpu': 1.2, 'mem': 2.1},
            {'pid': 303, 'user': 'root', 'cmd': 'sshd', 'cpu': 0.0, 'mem': 0.3},
        ]
        
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
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'cp': self.cmd_cp,
            'mv': self.cmd_mv,
            'head': self.cmd_head,
            'tail': self.cmd_tail,
            'wc': self.cmd_wc,
            'grep': self.cmd_grep,
            'egrep': self.cmd_grep,
            'fgrep': self.cmd_grep,
            'uname': self.cmd_uname,
            'hostname': self.cmd_hostname,
            'history': self.cmd_history,
            'env': self.cmd_env,
            'chmod': self.cmd_chmod,
            'du': self.cmd_du,
            'df': self.cmd_df,
            'file': self.cmd_filetype,
            'find': self.cmd_find,
                'ln': self.cmd_ln,
                'locate': self.cmd_locate,
                'whereis': self.cmd_whereis,
                'whatis': self.cmd_whatis,
                'lsof': self.cmd_lsof,
            'which': self.cmd_which,
            'strings': self.cmd_strings,
            'kill': self.cmd_kill,
            'killall': self.cmd_killall,
            'pgrep': self.cmd_pgrep,
            'pidof': self.cmd_pidof,
            'pkill': self.cmd_pkill,
            'ps': self.cmd_ps,
            'top': self.cmd_top,
            'finger': self.cmd_finger,
            'id': self.cmd_id,
            'who': self.cmd_who,
            'w': self.cmd_w,
            'cut': self.cmd_cut,
            'diff': self.cmd_diff,
            'less': self.cmd_less,
            'more': self.cmd_less,
            'sort': self.cmd_sort,
            'tr': self.cmd_tr,
            'uniq': self.cmd_uniq,
            'cmp': self.cmd_cmp,
            'cksum': self.cmd_cksum,
            'fold': self.cmd_fold,
            'tee': self.cmd_tee,
                'iconv': self.cmd_iconv,
                'join': self.cmd_join,
                'paste': self.cmd_paste,
                'ex': self.cmd_ex,
            'banner': self.cmd_banner,
            'cal': self.cmd_cal,
            'yes': self.cmd_yes,
            'dirname': self.cmd_dirname,
            'basename': self.cmd_basename,
            'seq': self.cmd_seq,
            'download': self.cmd_download,
            'inputmode': self.cmd_inputmode,
            'man': self.cmd_man,
            # Stubs
            'sleep': self.cmd_stub,
            'time': self.cmd_stub,
            'passwd': self.cmd_stub,
            'su': self.cmd_stub,
            'sudo': self.cmd_stub,
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
    rm file1 file2      remove multiple files""",

            'mkdir': """NAME
    mkdir - make directories

SYNOPSIS
    mkdir [-p] DIRECTORY...

DESCRIPTION
    Create the DIRECTORY(ies), if they do not already exist.

OPTIONS
    -p     no error if existing, make parent directories as needed

EXAMPLES
    mkdir newdir            create 'newdir'
    mkdir -p a/b/c          create nested directories
    mkdir dir1 dir2         create multiple directories""",

            'rmdir': """NAME
    rmdir - remove empty directories

SYNOPSIS
    rmdir DIRECTORY...

DESCRIPTION
    Remove the DIRECTORY(ies), if they are empty.""",

            'cp': """NAME
    cp - copy files and directories

SYNOPSIS
    cp [-r] SOURCE DEST

DESCRIPTION
    Copy SOURCE to DEST. When copying directories, use -r.""",

            'mv': """NAME
    mv - move (rename) files

SYNOPSIS
    mv SOURCE DEST

DESCRIPTION
    Move SOURCE to DEST (rename or move into directory).""",

            'head': """NAME
    head - output the first part of files

SYNOPSIS
    head [-n NUM] FILE

DESCRIPTION
    Print the first NUM lines (default 10) of FILE.""",

            'tail': """NAME
    tail - output the last part of files

SYNOPSIS
    tail [-n NUM] FILE

DESCRIPTION
    Print the last NUM lines (default 10) of FILE.""",

            'wc': """NAME
    wc - print newline, word, and byte counts for each file

SYNOPSIS
    wc FILE...

DESCRIPTION
    Print line, word, and byte counts for each FILE.""",

            'grep': """NAME
    grep - print lines matching a pattern

SYNOPSIS
    grep [-n] PATTERN FILE

DESCRIPTION
    Search for PATTERN in FILE and print matching lines.""",

            'uname': """NAME
    uname - print system information

SYNOPSIS
    uname [-a]

DESCRIPTION
    Print kernel name or all information with -a.""",

            'hostname': """NAME
    hostname - show or set the system's host name

SYNOPSIS
    hostname

DESCRIPTION
    Print the name of the current host.""",

            'history': """NAME
    history - display command history

SYNOPSIS
    history

DESCRIPTION
    List the commands entered in this session.""",

            'env': """NAME
    env - show environment variables

SYNOPSIS
    env

DESCRIPTION
    Print a list of environment variables.""",

            'du': """NAME
    du - estimate file space usage

SYNOPSIS
    du [PATH]

DESCRIPTION
    Show total size of PATH (defaults to current directory).""",

            'df': """NAME
    df - report file system disk space usage

SYNOPSIS
    df

DESCRIPTION
    Show filesystem disk space usage with total/used/available space.""",

            'file': """NAME
    file - determine file type

SYNOPSIS
    file FILE

DESCRIPTION
    Determines and prints file type. Prints 'directory' for directories, 'ASCII text' for text files, otherwise 'data'.""",

            'ln': """NAME
    ln - link files

SYNOPSIS
    ln [-s] SOURCE TARGET

DESCRIPTION
    Create hard or symbolic links. Use -s for symbolic links.""",

            'which': """NAME
    which - locate a command

SYNOPSIS
    which COMMAND

DESCRIPTION
    Prints path if COMMAND is available.""",

            'locate': """NAME
    locate - find files by name

SYNOPSIS
    locate PATTERN

DESCRIPTION
    Searches the filesystem for names containing PATTERN.""",

            'strings': """NAME
    strings - print text strings from files

SYNOPSIS
    strings FILE

DESCRIPTION
    Prints sequences of printable characters of length >= 4.""",

            'find': """NAME
    find - search for files in a directory hierarchy

SYNOPSIS
    find [PATH] -name PATTERN

DESCRIPTION
    Search for files matching PATTERN in PATH (defaults to current directory). Supports simple wildcard matching.""",

            'ps': """NAME
    ps - report process status

SYNOPSIS
    ps

DESCRIPTION
    Shows a list of processes.""",

            'kill': """NAME
    kill - send signals to processes

SYNOPSIS
    kill PID...

DESCRIPTION
    Terminates processes by process ID.""",

            'killall': """NAME
    killall - kill processes by name

SYNOPSIS
    killall NAME

DESCRIPTION
    Terminates processes whose command contains NAME.""",

            'pgrep': """NAME
    pgrep - list PIDs matching a pattern

SYNOPSIS
    pgrep NAME

DESCRIPTION
    Prints PIDs whose command contains NAME.""",

            'pidof': """NAME
    pidof - find the process ID of a running program

SYNOPSIS
    pidof NAME

DESCRIPTION
    Prints PIDs for NAME.""",

            'pkill': """NAME
    pkill - kill processes by pattern

SYNOPSIS
    pkill NAME

DESCRIPTION
    Terminates processes whose command contains NAME.""",

            'top': """NAME
    top - display Linux processes

SYNOPSIS
    top

DESCRIPTION
    Prints a snapshot list of processes and CPU/MEM usage.""",

            'time': """NAME
    time - time a simple command

SYNOPSIS
    time COMMAND

DESCRIPTION
    Measures execution time of a command.""",

            'sleep': """NAME
    sleep - delay for a specified amount of time

SYNOPSIS
    sleep N

DESCRIPTION
    Delays execution for N seconds.""",

            'sort': """NAME
    sort - sort lines of text files

SYNOPSIS
    sort FILE

DESCRIPTION
    Sorts all lines in memory and prints the result.""",

            'cut': """NAME
    cut - remove sections from each line

SYNOPSIS
    cut -d DELIM -f LIST FILE

DESCRIPTION
    Prints the selected 1-based field numbers using the delimiter.""",

            'diff': """NAME
    diff - compare files line by line (simple)

SYNOPSIS
    diff FILE1 FILE2

DESCRIPTION
    Prints differing lines prefixed with '<' and '>' (no context).""",

            'less': """NAME
    less - view file contents

SYNOPSIS
    less FILE

DESCRIPTION
    Displays file contents to the terminal.""",

            'uniq': """NAME
    uniq - report or omit repeated lines

SYNOPSIS
    uniq FILE

DESCRIPTION
    Removes adjacent duplicate lines and prints result.""",

            'tr': """NAME
    tr - translate characters

SYNOPSIS
    tr SET1 SET2 FILE

DESCRIPTION
    One-to-one character mapping up to min(len(SET1), len(SET2)).""",

            'cksum': """NAME
    cksum - checksum and count the bytes of a file

SYNOPSIS
    cksum FILE...

DESCRIPTION
    Prints CRC32 and byte length for each FILE.""",

            'cmp': """NAME
    cmp - compare two files (simple)

SYNOPSIS
    cmp FILE1 FILE2

DESCRIPTION
    Prints 'files differ' if content differs; silent otherwise.""",

            'fold': """NAME
    fold - wrap each input line to fit in specified width

SYNOPSIS
    fold [-w WIDTH] FILE

DESCRIPTION
    Prints lines wrapped at WIDTH (default 80).""",

            'tee': """NAME
    tee - read from standard input and write to files

SYNOPSIS
    tee FILE...

DESCRIPTION
    Writes to FILE(s).""",

            'download': """NAME
    download - save session transcript

SYNOPSIS
    download [PATH] | download --local

DESCRIPTION
    Saves session transcript to PATH (defaults to /session_TIMESTAMP.txt) or opens Save dialog with --local.

EXAMPLES
    download              Save to default location
    download /log.txt      Save to /log.txt
    download --local       Open file save dialog""",


            'inputmode': """NAME
    inputmode - switch terminal input mode

SYNOPSIS
    inputmode [inline|bottom]

DESCRIPTION
    Toggle or set typing mode: inline (inside terminal) or bottom input box.

EXAMPLES
    inputmode inline     Switch to inline input mode
    inputmode bottom     Switch to bottom input box""",

            'awk': """NAME
    awk - pattern scanning and processing

SYNOPSIS
    awk '{print $N}' FILE

DESCRIPTION
    Simple awk-like support. Only '{print $N}' pattern is supported.

EXAMPLES
    awk '{print $1}' file.txt    Print first field of each line""",

            'sed': """NAME
    sed - stream editor

SYNOPSIS
    sed 's/old/new/g' FILE

DESCRIPTION
    Basic sed substitution. Only simple s/old/new/g pattern is supported.

EXAMPLES
    sed 's/old/new/g' file.txt    Replace 'old' with 'new' in file""",

            'join': """NAME
    join - join lines of two files

SYNOPSIS
    join FILE1 FILE2

DESCRIPTION
    Join lines of two files on the first field.

EXAMPLES
    join file1.txt file2.txt    Join files on first field""",

            'paste': """NAME
    paste - merge lines of files

SYNOPSIS
    paste FILE1 FILE2

DESCRIPTION
    Merge lines of files horizontally.

EXAMPLES
    paste file1.txt file2.txt    Merge files horizontally""",

            'ex': """NAME
    ex - line editor

SYNOPSIS
    ex -p FILE

DESCRIPTION
    Very basic ex mode. Only '-p FILE' option is supported.

EXAMPLES
    ex -p file.txt    Print file contents""",

            'whoami': """NAME
    whoami - display current username

SYNOPSIS
    whoami

DESCRIPTION
    Print the current username.""",

            'date': """NAME
    date - display current date and time

SYNOPSIS
    date

DESCRIPTION
    Display the current date and time.""",

            'echo': """NAME
    echo - display a line of text

SYNOPSIS
    echo [TEXT]...

DESCRIPTION
    Display TEXT to standard output.

EXAMPLES
    echo Hello World    Print "Hello World"
    echo $USER         Print value of USER variable""",

            'finger': """NAME
    finger - display user information

SYNOPSIS
    finger [USER]

DESCRIPTION
    Display user information.""",

            'id': """NAME
    id - print user identity

SYNOPSIS
    id

DESCRIPTION
    Print user and group IDs.""",

            'who': """NAME
    who - show logged-in users

SYNOPSIS
    who

DESCRIPTION
    Display information about logged-in users.""",

            'w': """NAME
    w - show who is logged in and activity

SYNOPSIS
    w

DESCRIPTION
    Display information about logged-in users and their activity.""",

            'last': """NAME
    last - show last logged in users

SYNOPSIS
    last

DESCRIPTION
    Show last logged in users.""",

            'lastlog': """NAME
    lastlog - report most recent login

SYNOPSIS
    lastlog

DESCRIPTION
    Report most recent login of all users.""",

            'logname': """NAME
    logname - print user's login name

SYNOPSIS
    logname

DESCRIPTION
    Print the user's login name.""",

            'locale': """NAME
    locale - display locale information

SYNOPSIS
    locale

DESCRIPTION
    Display locale-specific information.""",

            'localedef': """NAME
    localedef - define locale

SYNOPSIS
    localedef NAME

DESCRIPTION
    Define a locale by creating a marker file.""",

            'chown': """NAME
    chown - change file owner and group

SYNOPSIS
    chown [OWNER][:GROUP] FILE...

DESCRIPTION
    Change the owner and/or group of FILE(s).

EXAMPLES
    chown user file.txt          Change owner to user
    chown user:group file.txt    Change owner and group""",

            'chgrp': """NAME
    chgrp - change group ownership

SYNOPSIS
    chgrp GROUP FILE...

DESCRIPTION
    Change the group ownership of FILE(s).

EXAMPLES
    chgrp group file.txt    Change group to 'group'""",

            'chmod': """NAME
    chmod - change file permissions

SYNOPSIS
    chmod MODE FILE...

DESCRIPTION
    Change the permissions of FILE(s). MODE is an octal number.

EXAMPLES
    chmod 755 file.txt    Set permissions to rwxr-xr-x
    chmod 644 file.txt    Set permissions to rw-r--r--""",

            'whereis': """NAME
    whereis - locate binary, source, and manual pages

SYNOPSIS
    whereis COMMAND

DESCRIPTION
    Locate binary, source, and manual pages for COMMAND.

EXAMPLES
    whereis ls    Find ls binary and manual pages""",

            'whatis': """NAME
    whatis - display one-line manual page descriptions

SYNOPSIS
    whatis COMMAND

DESCRIPTION
    Display a one-line description from the manual page.

EXAMPLES
    whatis ls    Show one-line description of ls command""",

            'lsof': """NAME
    lsof - list open files

SYNOPSIS
    lsof

DESCRIPTION
    List open files.""",

            'banner': """NAME
    banner - display text in large format

SYNOPSIS
    banner TEXT

DESCRIPTION
    Display TEXT in large banner format.

EXAMPLES
    banner Hello    Display "HELLO" in large format""",

            'cal': """NAME
    cal - display calendar

SYNOPSIS
    cal

DESCRIPTION
    Display a calendar for the current month.""",

            'yes': """NAME
    yes - output string repeatedly

SYNOPSIS
    yes [STRING]

DESCRIPTION
    Output STRING repeatedly (default: "y").

EXAMPLES
    yes          Output "y" repeatedly
    yes Hello    Output "Hello" repeatedly""",

            'dirname': """NAME
    dirname - extract directory from pathname

SYNOPSIS
    dirname PATH

DESCRIPTION
    Extract the directory portion of PATH.

EXAMPLES
    dirname /home/user/file.txt    Output: /home/user""",

            'basename': """NAME
    basename - extract filename from pathname

SYNOPSIS
    basename PATH

DESCRIPTION
    Extract the filename portion of PATH.

EXAMPLES
    basename /home/user/file.txt    Output: file.txt""",

            'seq': """NAME
    seq - generate sequence of numbers

SYNOPSIS
    seq [FIRST] [INCREMENT] LAST

DESCRIPTION
    Generate a sequence of numbers.

EXAMPLES
    seq 5           Generate 1 to 5
    seq 2 5         Generate 2 to 5
    seq 1 2 10      Generate 1, 3, 5, 7, 9""",

            'tar': """NAME
    tar - create/extract tar archives

SYNOPSIS
    tar OPERATION ARCHIVE [FILE]...

DESCRIPTION
    Create or extract tar archives. OPERATION can be 'cf' (create) or 'xf' (extract).

EXAMPLES
    tar cf archive.tar file1 file2    Create archive
    tar xf archive.tar                 Extract archive""",

            'nohup': """NAME
    nohup - run command immune to hangups

SYNOPSIS
    nohup COMMAND

DESCRIPTION
    Run COMMAND immune to hangups, with output appended to nohup.out.""",

            'nice': """NAME
    nice - run command with modified priority

SYNOPSIS
    nice COMMAND

DESCRIPTION
    Run COMMAND with modified scheduling priority.""",

            'clear': """NAME
    clear - clear the terminal screen

SYNOPSIS
    clear

DESCRIPTION
    Clear the terminal screen.""",

            'exit': """NAME
    exit - exit the terminal

SYNOPSIS
    exit

DESCRIPTION
    Exit the terminal application.""",

            'help': """NAME
    help - display available commands

SYNOPSIS
    help

DESCRIPTION
    Display a list of available commands and their descriptions.""",

            'man': """NAME
    man - display manual page

SYNOPSIS
    man COMMAND

DESCRIPTION
    Display the manual page for COMMAND.

EXAMPLES
    man ls    Display manual page for ls command"""
        }

    def _human_readable_size(self, size):
        """Convert size to human readable format"""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}P"
    
    # ============ COMMAND PARSER ============
    
    def parse_command(self, command_line):
        """Parse and execute a command"""
        if not command_line.strip():
            return ""
        
        parts = command_line.strip().split()
        if not parts:
            return ""

        redirect = None
        if '>' in parts or '>>' in parts:
            for i in range(len(parts) - 1, -1, -1):
                if parts[i] in ('>', '>>'):
                    if i + 1 >= len(parts):
                        return "bash: syntax error near unexpected token 'newline'"
                    redirect = (parts[i], parts[i + 1])
                    parts = parts[:i]
                    break

        if not parts:
            return ""

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            output = self.commands[command](args)
            
            if redirect and output is not None:
                op, path = redirect
                content = (output + "\n") if output else ""
                if op == '>':
                    self.filesystem.write_file(path, content)
                    return ""
                elif op == '>>':
                    self.filesystem.append_file(path, content)
                    return ""
            return output
        else:
            return f"bash: {command}: command not found"
    
    # ============ FILE SYSTEM COMMANDS ============
    
    def cmd_ls(self, args):
        """List directory contents"""
        show_details = '-l' in args
        show_all = '-a' in args
        
        path_args = [arg for arg in args if not arg.startswith('-')]
        target_path = path_args[0] if path_args else '.'
        
        real_path = self.filesystem._get_real_path(target_path)
        if not real_path or not os.path.exists(real_path):
            return f"ls: cannot access '{target_path}': No such file or directory"
        
        if not os.path.isdir(real_path):
            return target_path
        
        try:
            entries = os.listdir(real_path)
            if not show_all:
                entries = [e for e in entries if not e.startswith('.')]
            
            entries.sort()
            
            if show_details:
                lines = []
                for entry in entries:
                    entry_path = os.path.join(real_path, entry)
                    stat = os.stat(entry_path)
                    
                    perms = 'drwxr-xr-x' if os.path.isdir(entry_path) else '-rw-r--r--'
                    size = stat.st_size
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                    time_str = mtime.strftime('%b %d %H:%M')
                    
                    lines.append(f"{perms} 1 {self.terminal_ui.username} {self.terminal_ui.username} {size:>8} {time_str} {entry}")
                
                return "\n".join(lines)
            else:
                if len(entries) <= 4:
                    return "  ".join(entries)
                else:
                    cols = 3
                    rows = (len(entries) + cols - 1) // cols
                    result = []
                    for row in range(rows):
                        line = []
                        for col in range(cols):
                            idx = col * rows + row
                            if idx < len(entries):
                                line.append(f"{entries[idx]:<20}")
                        result.append("".join(line).rstrip())
                    return "\n".join(result)
        
        except PermissionError:
            return f"ls: cannot open directory '{target_path}': Permission denied"
        except Exception as e:
            return f"ls: error: {e}"
    
    def cmd_cd(self, args):
        """Change directory"""
        if not args:
            target = "/"
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
    
    def cmd_mkdir(self, args):
        """Create directories"""
        if not args:
            return "mkdir: missing operand"
        
        parents = '-p' in args
        path_args = [arg for arg in args if not arg.startswith('-')]
        
        if not path_args:
            return "mkdir: missing operand"
        
        results = []
        for dirpath in path_args:
            success, error = self.filesystem.create_directory(dirpath, parents=parents)
            if not success and error:
                results.append(error)
        
        return "\n".join(results) if results else ""
    
    def cmd_rmdir(self, args):
        """Remove empty directories"""
        if not args:
            return "rmdir: missing operand"
        
        results = []
        for path in args:
            success, error = self.filesystem.remove_directory(path)
            if error:
                results.append(error)
        
        return "\n".join(results) if results else ""
    
    def cmd_rm(self, args):
        """Remove files"""
        if not args:
            return "rm: missing operand"
        
        force_recursive = '-r' in args or '-rf' in args or '-fr' in args
        paths = [arg for arg in args if not arg.startswith('-')]
        
        if not paths:
            return "rm: missing operand"
        
        results = []
        for filename in paths:
            if force_recursive:
                success, error = self.filesystem.remove_recursive(filename)
            else:
                success, error = self.filesystem.remove_file(filename)
            if error:
                results.append(error)
        
        return "\n".join(results) if results else ""
    
    def cmd_cp(self, args):
        """Copy files/directories"""
        if not args or len(args) < 2:
            return "cp: missing file operand"
        
        recursive = '-r' in args or '-R' in args
        filtered = [arg for arg in args if not arg.startswith('-')]
        
        if len(filtered) < 2:
            return "cp: missing destination file operand"
        
        src = filtered[0]
        dst = filtered[1]
        
        success, error = self.filesystem.copy_path(src, dst, recursive=recursive)
        return error if not success else ""
    
    def cmd_mv(self, args):
        """Move/rename files"""
        if not args or len(args) < 2:
            return "mv: missing file operand"
        
        filtered = [arg for arg in args if not arg.startswith('-')]
        
        if len(filtered) < 2:
            return "mv: missing destination file operand"
        
        src = filtered[-2]
        dst = filtered[-1]
        
        success, error = self.filesystem.move_path(src, dst)
        return error if not success else ""
    
    # ============ TEXT PROCESSING ============
    
    def _read_file_lines(self, path):
        """Helper to read file lines"""
        content, error = self.filesystem.read_file(path)
        if error:
            return None, error
        return content.splitlines(), None
    
    def cmd_head(self, args):
        """Show first lines of a file"""
        if not args:
            return "head: missing file operand"
        
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    return "head: invalid number of lines"
                i += 2
            elif args[i].startswith('-n'):
                try:
                    n = int(args[i][2:])
                except ValueError:
                    return "head: invalid number of lines"
                i += 1
            else:
                files.append(args[i])
                i += 1
        
        if not files:
            return "head: missing file operand"
        
        lines, err = self._read_file_lines(files[0])
        if err:
            return f"head: {err}"
        return "\n".join(lines[:n])
    
    def cmd_tail(self, args):
        """Show last lines of a file"""
        if not args:
            return "tail: missing file operand"
        
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    return "tail: invalid number of lines"
                i += 2
            elif args[i].startswith('-n'):
                try:
                    n = int(args[i][2:])
                except ValueError:
                    return "tail: invalid number of lines"
                i += 1
            else:
                files.append(args[i])
                i += 1
        
        if not files:
            return "tail: missing file operand"
        
        lines, err = self._read_file_lines(files[0])
        if err:
            return f"tail: {err}"
        return "\n".join(lines[-n:])
    
    def cmd_wc(self, args):
        """Word/line/byte counts"""
        if not args:
            return "wc: missing file operand"
        
        outputs = []
        total_l = total_w = total_b = 0
        
        for path in args:
            content, error = self.filesystem.read_file(path)
            if error:
                outputs.append(error)
                continue
            
            lines = content.splitlines()
            words = re.findall(r"\S+", content)
            bytes_count = len(content.encode('utf-8'))
            
            outputs.append(f"{len(lines)} {len(words)} {bytes_count} {path}")
            total_l += len(lines)
            total_w += len(words)
            total_b += bytes_count
        
        if len(args) > 1:
            outputs.append(f"{total_l} {total_w} {total_b} total")
        
        return "\n".join(outputs)
    
    def cmd_grep(self, args):
        """Search for pattern in file"""
        if len(args) < 2:
            return "grep: missing operand"
        
        show_numbers = '-n' in args
        filtered = [a for a in args if not a.startswith('-')]
        
        if len(filtered) < 2:
            return "grep: missing operand"
        
        pattern = filtered[0]
        path = filtered[1]
        
        lines, err = self._read_file_lines(path)
        if err:
            return f"grep: {err}"
        
        out_lines = []
        try:
            regex = re.compile(pattern)
            for idx, line in enumerate(lines, 1):
                if regex.search(line):
                    out_lines.append(f"{idx}: {line}" if show_numbers else line)
        except re.error:
            for idx, line in enumerate(lines, 1):
                if pattern in line:
                    out_lines.append(f"{idx}: {line}" if show_numbers else line)
        
        return "\n".join(out_lines)
    
    def cmd_sort(self, args):
        """Sort lines of text files"""
        if not args:
            return "sort: missing file operand"
        
        lines, err = self._read_file_lines(args[0])
        return err if err else "\n".join(sorted(lines))
    
    def cmd_cut(self, args):
        """Remove sections from each line"""
        if '-f' not in args or '-d' not in args:
            return "cut: usage: cut -d DELIM -f LIST FILE"
        
        d_idx = args.index('-d')
        delim = args[d_idx + 1]
        f_idx = args.index('-f')
        fields = args[f_idx + 1]
        file_arg = args[-1]
        
        nums = []
        for part in fields.split(','):
            try:
                nums.append(int(part))
            except ValueError:
                pass
        
        lines, err = self._read_file_lines(file_arg)
        if err:
            return f"cut: {err}"
        
        out = []
        for line in lines:
            cols = line.split(delim)
            picked = [cols[i-1] for i in nums if 0 < i <= len(cols)]
            out.append(delim.join(picked))
        
        return "\n".join(out)
    
    def cmd_diff(self, args):
        """Compare files line by line"""
        if len(args) < 2:
            return "diff: missing file operand"
        
        a, b = args[0], args[1]
        a_lines, e1 = self._read_file_lines(a)
        b_lines, e2 = self._read_file_lines(b)
        
        if e1:
            return f"diff: {e1}"
        if e2:
            return f"diff: {e2}"
        
        out = []
        for i in range(max(len(a_lines), len(b_lines))):
            la = a_lines[i] if i < len(a_lines) else ''
            lb = b_lines[i] if i < len(b_lines) else ''
            if la != lb:
                out.append(f"< {la}")
                out.append(f"> {lb}")
        
        return "\n".join(out) if out else ""
    
    def cmd_less(self, args):
        """View file contents"""
        if not args:
            return "less: missing file operand"
        
        lines, err = self._read_file_lines(args[0])
        return f"less: {err}" if err else "\n".join(lines)
    
    def cmd_tr(self, args):
        """Translate characters"""
        if len(args) < 3:
            return "tr: usage: tr SET1 SET2 FILE"
        
        src, dst, path = args[0], args[1], args[2]
        table = str.maketrans({src[i]: dst[i] for i in range(min(len(src), len(dst)))})
        
        lines, err = self._read_file_lines(path)
        if err:
            return f"tr: {err}"
        
        content = "\n".join(lines)
        return content.translate(table)
    
    def cmd_uniq(self, args):
        """Report or omit repeated lines"""
        if not args:
            return "uniq: missing file operand"
        
        lines, err = self._read_file_lines(args[0])
        if err:
            return f"uniq: {err}"
        
        out = []
        prev = None
        for line in lines:
            if line != prev:
                out.append(line)
            prev = line
        
        return "\n".join(out)

    def cmd_awk(self, args):
        """Very small awk-like support: awk '{print $N}' FILE"""
        if len(args) < 2:
            return "awk: missing operand"
        script = args[0]
        file_arg = args[1]
        m = re.match(r"\{\s*print\s+\$(\d+)\s*\}", script)
        if not m:
            return "awk: only simple '{print $N}' supported"
        field = int(m.group(1))
        lines, err = self._read_file_lines(file_arg)
        if err:
            return f"awk: {err}"
        out = []
        for line in lines:
            parts = re.findall(r"\S+", line)
            out.append(parts[field-1] if 0 < field <= len(parts) else '')
        return "\n".join(out)

    def cmd_sed(self, args):
        """Basic sed substitution: sed 's/old/new/g' FILE"""
        if len(args) < 2:
            return "sed: missing operand"
        expr = args[0]
        file_arg = args[1]
        m = re.match(r"s/(.*?)/(.*?)/g", expr)
        if not m:
            return "sed: only simple s/old/new/g supported"
        old, new = m.group(1), m.group(2)
        lines, err = self._read_file_lines(file_arg)
        if err:
            return f"sed: {err}"
        return "\n".join([re.sub(old, new, l) for l in lines])

    def cmd_iconv(self, args):
        """Convert encoding: iconv -f FROM -t TO FILE"""
        if len(args) < 4:
            return "iconv: usage: iconv -f FROM -t TO FILE"
        try:
            f_idx = args.index('-f')
            t_idx = args.index('-t')
            frm = args[f_idx+1]
            to = args[t_idx+1]
            file_arg = args[-1]
        except Exception:
            return "iconv: invalid arguments"

        content, err = self.filesystem.read_file(file_arg)
        if err:
            return f"iconv: {err}"
        try:
            return content.encode(frm, errors='replace').decode(to, errors='replace')
        except Exception as e:
            return f"iconv: {e}"

    def cmd_join(self, args):
        """Join lines of two files on first field: join FILE1 FILE2"""
        if len(args) < 2:
            return "join: missing operand"
        a, b = args[0], args[1]
        a_lines, e1 = self._read_file_lines(a)
        b_lines, e2 = self._read_file_lines(b)
        if e1:
            return f"join: {e1}"
        if e2:
            return f"join: {e2}"
        a_map = {l.split()[0]: l for l in a_lines if l.split()}
        b_map = {l.split()[0]: l for l in b_lines if l.split()}
        out = []
        for key in sorted(set(a_map.keys()) & set(b_map.keys())):
            out.append(a_map[key] + ' ' + ' '.join(b_map[key].split()[1:]))
        return "\n".join(out)

    def cmd_paste(self, args):
        """Merge lines of files horizontally: paste FILE1 FILE2"""
        if len(args) < 2:
            return "paste: missing operand"
        a, b = args[0], args[1]
        a_lines, e1 = self._read_file_lines(a)
        b_lines, e2 = self._read_file_lines(b)
        if e1:
            return f"paste: {e1}"
        if e2:
            return f"paste: {e2}"
        out = []
        for i in range(max(len(a_lines), len(b_lines))):
            la = a_lines[i] if i < len(a_lines) else ''
            lb = b_lines[i] if i < len(b_lines) else ''
            out.append(la + '\t' + lb)
        return "\n".join(out)

    def cmd_ex(self, args):
        """Very small ex mode: ex -p FILE prints file"""
        if not args:
            return "ex: missing operand"
        if args[0] == '-p' and len(args) > 1:
            lines, err = self._read_file_lines(args[1])
            return f"ex: {err}" if err else "\n".join(lines)
        return "ex: only '-p FILE' supported"

    def cmd_cmp(self, args):
        """Compare two files byte by byte"""
        if len(args) < 2:
            return "cmp: missing file operand"
        
        a, b = args[0], args[1]
        a_lines, e1 = self._read_file_lines(a)
        b_lines, e2 = self._read_file_lines(b)
        
        if e1:
            return f"cmp: {e1}"
        if e2:
            return f"cmp: {e2}"
        
        a_content = "\n".join(a_lines)
        b_content = "\n".join(b_lines)
        
        if a_content == b_content:
            return ""
        return "cmp: files differ"
    
    def cmd_cksum(self, args):
        """Calculate CRC32 checksum and byte count"""
        if not args:
            return "cksum: missing file operand"
        
        out = []
        for path in args:
            content_str, error = self.filesystem.read_file(path)
            if error:
                out.append(error)
                continue
            
            content = content_str.encode('utf-8')
            csum = zlib.crc32(content) & 0xffffffff
            out.append(f"{csum} {len(content)} {path}")
        
        return "\n".join(out)
    
    def cmd_fold(self, args):
        """Wrap each input line to fit in specified width"""
        width = 80
        path = None
        i = 0
        
        while i < len(args):
            if args[i] == '-w' and i + 1 < len(args):
                try:
                    width = int(args[i+1])
                except ValueError:
                    pass
                i += 2
            else:
                path = args[i]
                i += 1
        
        if not path:
            return "fold: missing file operand"
        
        lines, err = self._read_file_lines(path)
        if err:
            return f"fold: {err}"
        
        out = []
        for line in lines:
            for i in range(0, len(line), width):
                out.append(line[i:i+width])
        
        return "\n".join(out)
    
    def cmd_tee(self, args):
        """Read from standard input and write to files"""
        if not args:
            return ""
        
        for path in args:
            self.filesystem.write_file(path, "")
        
        return ""
    
    # ============ SYSTEM INFORMATION ============
    
    def cmd_uname(self, args):
        """Print system information"""
        if args and args[0] == '-a':
            return "Linux terminal 5.10.0 #1 SMP PREEMPT x86_64 GNU/Linux"
        return "Linux"
    
    def cmd_hostname(self, args):
        """Show host name"""
        return self.terminal_ui.hostname
    
    def cmd_whoami(self, args):
        """Display current username"""
        return self.terminal_ui.username
    
    def cmd_date(self, args):
        """Display current date and time"""
        return datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    
    def cmd_uptime(self, args):
        """Show uptime"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"{current_time} up 1:23, 1 user, load average: 0.15, 0.12, 0.08"
    
    def cmd_pwd(self, args):
        """Print working directory"""
        return self.filesystem.current_path
    
    def cmd_echo(self, args):
        """Echo command - display text"""
        if not args:
            return ""
        return " ".join(args)
    
    def cmd_env(self, args):
        """Show environment variables"""
        env_vars = {
            'USER': self.terminal_ui.username,
            'HOME': '/',
            'PWD': self.filesystem.current_path,
            'SHELL': '/bin/bash',
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        }
        return "\n".join(f"{k}={v}" for k, v in env_vars.items())
    
    def cmd_history(self, args):
        """Show command history"""
        lines = []
        for i, cmd in enumerate(self.terminal_ui.command_history, 1):
            lines.append(f"{i}  {cmd}")
        return "\n".join(lines)
    
    # ============ PROCESS MANAGEMENT ============
    
    def cmd_ps(self, args):
        """Report process status"""
        lines = ["  PID TTY          TIME CMD"]
        for p in self.process_table:
            lines.append(f"{p['pid']:>5} pts/0    00:00:00 {p['cmd']}")
        return "\n".join(lines)
    
    def cmd_top(self, args):
        """Display Linux processes"""
        header = "top - 00:00:00 up 1:23, 1 user, load average: 0.15, 0.12, 0.08\n  PID USER      %CPU %MEM COMMAND"
        body = []
        for p in self.process_table:
            body.append(f"{p['pid']:>5} {p['user']:<9} {p['cpu']:>4.1f} {p['mem']:>4.1f} {p['cmd']}")
        return "\n".join([header] + body)
    
    def cmd_kill(self, args):
        """Terminate processes by PID"""
        if not args:
            return "kill: usage: kill [-signal] pid"
        
        msgs = []
        for a in args:
            if a.startswith('-'):
                continue
            try:
                pid = int(a)
                self.process_table = [p for p in self.process_table if p['pid'] != pid]
            except ValueError:
                msgs.append(f"kill: {a}: arguments must be process IDs")
        
        return "\n".join(msgs)
    
    def cmd_killall(self, args):
        """Kill processes by name"""
        if not args:
            return "killall: missing name"
        name = args[0]
        self.process_table = [p for p in self.process_table if name not in p['cmd']]
        return ""
    
    def cmd_pgrep(self, args):
        """List PIDs matching pattern"""
        if not args:
            return "pgrep: missing pattern"
        name = args[0]
        pids = [str(p['pid']) for p in self.process_table if name in p['cmd']]
        return "\n".join(pids)
    
    def cmd_pidof(self, args):
        """Find the process ID of a running program"""
        if not args:
            return "pidof: missing name"
        name = args[0]
        pids = [str(p['pid']) for p in self.process_table if name in p['cmd']]
        return " ".join(pids)
    
    def cmd_pkill(self, args):
        """Kill processes by pattern"""
        if not args:
            return "pkill: missing pattern"
        name = args[0]
        self.process_table = [p for p in self.process_table if name not in p['cmd']]
        return ""
    
    # ============ USER MANAGEMENT ============
    
    def cmd_finger(self, args):
        """Display user information"""
        return f"Login: {self.terminal_ui.username}\t\tName: Student User\nDirectory: /home/{self.terminal_ui.username}  Shell: /bin/bash"
    
    def cmd_id(self, args):
        """Print user identity"""
        return f"uid=1000({self.terminal_ui.username}) gid=1000({self.terminal_ui.username}) groups=1000({self.terminal_ui.username})"
    
    def cmd_who(self, args):
        """Show logged-in users"""
        return f"{self.terminal_ui.username} tty7    {datetime.datetime.now().strftime('%b %d %H:%M')} (:0)"
    
    def cmd_w(self, args):
        """Show who is logged in and activity"""
        return f"{self.terminal_ui.username} tty7    :0               1:23   1:23  0.00s bash"

    def cmd_last(self, args):
        """Show last logged in users"""
        out = []
        for i, entry in enumerate(reversed(self.terminal_ui.session_log[-50:]), 1):
            out.append(f"{self.terminal_ui.username} pts/0   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - session {i}")
        return "\n".join(out)

    def cmd_lastlog(self, args):
        """Report most recent login of all users"""
        # Simulate for single user
        return f"{self.terminal_ui.username} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} +0000"

    def cmd_logname(self, args):
        """Print user's login name"""
        return self.terminal_ui.username

    def cmd_locale(self, args):
        """Display locale-specific information"""
        settings = {
            'LANG': 'en_US.UTF-8',
            'LC_CTYPE': 'en_US.UTF-8',
            'LC_NUMERIC': 'en_US.UTF-8',
            'LC_TIME': 'en_US.UTF-8',
            'LC_COLLATE': 'en_US.UTF-8',
        }
        return "\n".join(f"{k}={v}" for k, v in settings.items())

    def cmd_localedef(self, args):
        """Define locale - creates a simple marker file"""
        if not args:
            return "localedef: missing operand"
        name = args[-1]
        path = f"/usr/lib/locale/{name}"
        real = self.filesystem._get_real_path(path)
        if not real:
            return f"localedef: cannot write to {path}"
        try:
            os.makedirs(os.path.dirname(real), exist_ok=True)
            with open(real, 'w', encoding='utf-8') as f:
                f.write('locale: ' + name)
            return ""
        except Exception as e:
            return f"localedef: {e}"

    def cmd_chown(self, args):
        """Change file owner and group: chown [OWNER][:GROUP] FILE"""
        if len(args) < 2:
            return "chown: missing operand"
        spec = args[0]
        targets = [a for a in args[1:] if not a.startswith('-')]
        owner = None
        group = None
        if ':' in spec:
            owner, group = spec.split(':', 1)
        else:
            owner = spec

        msgs = []
        for t in targets:
            real = self.filesystem._get_real_path(t)
            if not real or not os.path.exists(real):
                msgs.append(f"chown: cannot access '{t}': No such file or directory")
                continue
            try:
                uid = -1
                gid = -1
                # only try if running on Unix
                if hasattr(os, 'chown') and owner:
                    try:
                        uid = os.getuid() if owner == self.terminal_ui.username else -1
                    except Exception:
                        uid = -1
                if hasattr(os, 'chown') and group:
                    try:
                        gid = os.getgid()
                    except Exception:
                        gid = -1
                if uid != -1 or gid != -1:
                    try:
                        os.chown(real, uid if uid != -1 else -1, gid if gid != -1 else -1)
                    except Exception:
                        pass
            except Exception as e:
                msgs.append(f"chown: {e}")

        return "\n".join(msgs) if msgs else ""

    def cmd_chgrp(self, args):
        """Change group ownership: chgrp GROUP FILE"""
        if len(args) < 2:
            return "chgrp: missing operand"
        group = args[0]
        targets = args[1:]
        msgs = []
        for t in targets:
            real = self.filesystem._get_real_path(t)
            if not real or not os.path.exists(real):
                msgs.append(f"chgrp: cannot access '{t}': No such file or directory")
                continue
            try:
                if hasattr(os, 'chown'):
                    gid = -1
                    try:
                        gid = os.getgid()
                    except Exception:
                        gid = -1
                    if gid != -1:
                        try:
                            os.chown(real, -1, gid)
                        except Exception:
                            pass
            except Exception as e:
                msgs.append(f"chgrp: {e}")

        return "\n".join(msgs) if msgs else ""
    
    # ============ FILE UTILITIES ============
    
    def cmd_find(self, args):
        """Search for files in a directory hierarchy"""
        start = '.'
        name_pat = None
        i = 0
        
        if args and not args[0].startswith('-'):
            start = args[0]
            i = 1
        
        while i < len(args):
            if args[i] == '-name' and i + 1 < len(args):
                name_pat = args[i + 1].strip("\"'")
                i += 2
            else:
                i += 1
        
        real_path = self.filesystem._get_real_path(start)
        if not real_path or not os.path.exists(real_path):
            return f"find: '{start}': No such file or directory"
        
        results = []
        try:
            if os.path.isfile(real_path):
                basename = os.path.basename(real_path)
                if name_pat is None or name_pat.replace('*', '') in basename:
                    results.append(start)
            else:
                normalized_start = self.filesystem.normalize_path(start)
                for root, dirs, files in os.walk(real_path):
                    for name in dirs + files:
                        if name_pat is None or name_pat.replace('*', '') in name:
                            full_path = os.path.join(root, name)
                            rel_path = os.path.relpath(full_path, real_path)
                            rel_path_normalized = rel_path.replace('\\', '/')
                            if rel_path == '.':
                                virtual_path = normalized_start
                            else:
                                virtual_path = normalized_start.rstrip('/') + '/' + rel_path_normalized
                            if start == '.':
                                results.append(f"./{rel_path_normalized}")
                            else:
                                results.append(virtual_path)
        except PermissionError:
            return f"find: '{start}': Permission denied"
        except Exception as e:
            return f"find: error: {e}"
        return "\n".join(results) if results else ""
    
    def cmd_which(self, args):
        """Locate a command"""
        if not args:
            return "which: missing argument"
        name = args[0]
        return f"/bin/{name}" if name in self.commands else ""
    
    def cmd_strings(self, args):
        """Print text strings from files"""
        if not args:
            return "strings: missing file operand"
        
        path = args[0]
        lines, err = self._read_file_lines(path)
        if err:
            return f"strings: {err}"
        
        content = "\n".join(lines)
        out = []
        buf = ''
        
        for ch in content:
            if 32 <= ord(ch) <= 126 or ch in '\n\t':
                buf += ch
            else:
                if len(buf) >= 4:
                    out.append(buf)
                buf = ''
        
        if len(buf) >= 4:
            out.append(buf)
        
        return "\n".join(out)
    
    def cmd_du(self, args):
        """Estimate file space usage"""
        path = args[0] if args else self.filesystem.current_path

        real_path = self.filesystem._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return f"du: cannot access '{path}': No such file or directory"

        total = 0
        try:
            if os.path.isfile(real_path):
                total = os.path.getsize(real_path)
            else:
                for root, dirs, files in os.walk(real_path):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            total += os.path.getsize(fp)
                        except Exception:
                            pass
        except Exception:
            return f"du: cannot read directory '{path}'"

        kb_size = (total + 1023) // 1024
        return f"{kb_size}\t{path}"
    
    def cmd_df(self, args):
        """Report file system disk space usage"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(self.filesystem.base_path),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes)
                )
                total = total_bytes.value
                avail = free_bytes.value
                used = total - avail
            else:  # Unix-like
                stat = os.statvfs(self.filesystem.base_path)
                total = stat.f_blocks * stat.f_frsize
                avail = stat.f_bavail * stat.f_frsize
                used = total - avail
        except:
            total = 1024 * 1024 * 10
            used = 5000000
            avail = total - used
    
        usep = int(used * 100 / total) if total else 0
    
        return "Filesystem     1K-blocks    Used Available Use% Mounted on\nfilesystem     {0:>10} {1:>7} {2:>9} {3:>3}% /".format(
            total//1024, used//1024, avail//1024, usep
    )
    
    def cmd_filetype(self, args):
        """Determine file type"""
        if not args:
            return "file: missing file operand"
        
        path = args[0]
        
        real_path = self.filesystem._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return f"file: {path}: cannot open (No such file or directory)"
        
        if os.path.isdir(real_path):
            return f"{path}: directory"
        
        try:
            with open(real_path, 'rb') as f:
                header = f.read(512)
            
            if all(b < 128 for b in header):
                return f"{path}: ASCII text"
            else:
                return f"{path}: data"
        except:
            return f"{path}: cannot open"

    # --- Additional file/system commands ---
    def cmd_ln(self, args):
        """Create hard or symbolic links: ln [-s] SOURCE TARGET"""
        if not args or len([a for a in args if not a.startswith('-')]) < 2:
            return "ln: missing file operand"
        symbolic = '-s' in args
        parts = [a for a in args if not a.startswith('-')]
        src, dst = parts[0], parts[1]

        srcp = self.filesystem._get_real_path(src)
        dstp = self.filesystem._get_real_path(dst)
        if not srcp or not dstp:
            return "ln: Access denied"
        if not os.path.exists(srcp):
            return f"ln: failed to access '{src}': No such file or directory"
        try:
            if symbolic:
                if os.path.exists(dstp):
                    os.remove(dstp)
                os.symlink(srcp, dstp)
            else:
                if os.path.exists(dstp):
                    os.remove(dstp)
                os.link(srcp, dstp)
            return ""
        except Exception as e:
            return f"ln: {e}"

    def cmd_locate(self, args):
        """Locate files by name pattern (simple): locate PATTERN"""
        if not args:
            return "locate: missing operand"
        pattern = args[0]
        needle = pattern.replace('*', '')
        results = []
        for root, dirs, files in os.walk(self.filesystem.base_path):
            for name in dirs + files:
                if needle in name:
                    rel = os.path.relpath(os.path.join(root, name), self.filesystem.base_path)
                    results.append('/' + rel.replace('\\', '/'))
        return "\n".join(results)

    def cmd_whereis(self, args):
        """Locate binary, source, and manual pages for commands"""
        if not args:
            return "whereis: missing operand"
        name = args[0]
        parts = []
        if name in self.commands:
            parts.append(f"/bin/{name}")
        if name in self.manual_pages:
            parts.append(f"/usr/share/man/{name}.1")
        if self.filesystem.get_node(f"/usr/src/{name}"):
            parts.append(f"/usr/src/{name}")
        return " ".join(parts)

    def cmd_whatis(self, args):
        """Display one-line manual page descriptions"""
        if not args:
            return "whatis: missing operand"
        name = args[0]
        if name in self.manual_pages:
            text = self.manual_pages[name]
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if len(lines) >= 2:
                return lines[1]
        return f"{name}: nothing appropriate"

    def cmd_lsof(self, args):
        """List open files"""
        out = ["COMMAND PID USER FD TYPE NAME"]
        files = []
        for root, dirs, fs in os.walk(self.filesystem.base_path):
            for f in fs:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, self.filesystem.base_path)
                files.append('/' + rel_path.replace('\\', '/'))
        i = 0
        for p in self.process_table:
            if files:
                name = files[i % len(files)]
                out.append(f"{p['cmd']} {p['pid']} {p['user']} 3r REG {name}")
                i += 1
            else:
                out.append(f"{p['cmd']} {p['pid']} {p['user']} - ")
        return "\n".join(out)
    
    def cmd_chmod(self, args):
        """Change file permissions"""
        if len(args) < 2:
            return "chmod: missing operand"
        mode = args[0]
        path = args[1]

        real_path = self.filesystem._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return f"chmod: cannot access '{path}': No such file or directory"
        try:
            mode_int = int(mode, 8)
            os.chmod(real_path, mode_int)
            return ""
        except ValueError:
            return f"chmod: invalid mode: '{mode}'"
        except Exception as e:
            return f"chmod: {e}"
    
    # ============ UTILITY COMMANDS ============
    
    def cmd_banner(self, args):
        """Display text in large format"""
        if not args:
            return ""
        
        text = " ".join(args).upper()
        lines = [
            " " + "=" * (len(text) + 2),
            "| " + text + " |",
            " " + "=" * (len(text) + 2)
        ]
        
        return "\n".join(lines)
    
    def cmd_cal(self, args):
        """Display calendar"""
        now = datetime.datetime.now()
        return calendar.month(now.year, now.month)
    
    def cmd_yes(self, args):
        """Output string repeatedly"""
        text = " ".join(args) if args else "y"
        return "\n".join([text] * 20)
    
    def cmd_dirname(self, args):
        """Extract directory from pathname"""
        if not args:
            return "dirname: missing operand"
        
        path = self.filesystem.normalize_path(args[0])
        return '/'.join(path.split('/')[:-1]) or '/'
    
    def cmd_basename(self, args):
        """Extract filename from pathname"""
        if not args:
            return "basename: missing operand"
        
        path = args[0].rstrip('/')
        return path.split('/')[-1] if '/' in path else path
    
    def cmd_seq(self, args):
        """Generate sequence of numbers"""
        if not args:
            return "seq: missing operand"
        
        try:
            if len(args) == 1:
                start, end, step = 1, int(args[0]), 1
            elif len(args) == 2:
                start, end, step = int(args[0]), int(args[1]), 1
            else:
                start, step, end = int(args[0]), int(args[1]), int(args[2])
        except ValueError:
            return "seq: invalid number"
        
        if step == 0:
            return "seq: step must not be zero"
        
        out = []
        i = start
        
        if step > 0:
            while i <= end:
                out.append(str(i))
                i += step
        else:
            while i >= end:
                out.append(str(i))
                i += step
        if len(out) > 1000:
            return "seq: sequence too large (limit: 1000 numbers)"
        return "\n".join(out)
    
    def cmd_tar(self, args):
        """Create/extract tar archives"""
        import tarfile
        if not args or len(args) < 2:
            return "tar: missing operand"
        
        operation = args[0]
        archive = args[1]
        files = args[2:] if len(args) > 2 else []
        
        real_archive = self.filesystem._get_real_path(archive)
        if not real_archive:
            return f"tar: cannot access '{archive}': Access denied"
        
        try:
            if operation == '-cf' or operation == 'cf':
                # Create archive
                if not files:
                    return "tar: missing file operand"
                with tarfile.open(real_archive, 'w') as tar:
                    for f in files:
                        real_file = self.filesystem._get_real_path(f)
                        if real_file and os.path.exists(real_file):
                            tar.add(real_file, arcname=os.path.basename(real_file))
                return ""
            elif operation == '-xf' or operation == 'xf':
                # Extract archive
                if not os.path.exists(real_archive):
                    return f"tar: {archive}: Cannot open: No such file or directory"
                with tarfile.open(real_archive, 'r') as tar:
                    tar.extractall(path=self.filesystem.base_path)
                return ""
            else:
                return f"tar: unknown operation '{operation}'"
        except Exception as e:
            return f"tar: {e}"
    
    def cmd_nohup(self, args):
        """Run command immune to hangups"""
        return "nohup: ignoring input and appending output to 'nohup.out'"
    
    def cmd_nice(self, args):
        """Run command with modified priority"""
        if not args:
            return "nice: missing operand"
        # Note: Actual priority modification requires subprocess execution
        # This is a simplified version
        return ""
    
    # ============ TERMINAL CONTROL ============
    
    def cmd_clear(self, args):
        """Clear the terminal screen"""
        self.terminal_ui.terminal_display.config(state=tk.NORMAL)
        self.terminal_ui.terminal_display.delete(1.0, tk.END)
        self.terminal_ui.terminal_display.config(state=tk.DISABLED)
        return ""
    
    def cmd_exit(self, args):
        """Exit the terminal"""
        self.terminal_ui.root.quit()
        return "Goodbye!"
    
    def cmd_inputmode(self, args):
        """Toggle or set input mode"""
        mode = args[0] if args else None
        if mode not in (None, 'inline', 'bottom'):
            return "inputmode: expected 'inline' or 'bottom'"
        
        prev = 'inline' if self.terminal_ui.inline_input else 'bottom'
        self.terminal_ui.set_input_mode(mode)
        curr = 'inline' if self.terminal_ui.inline_input else 'bottom'
        
        return f"input mode: {prev} -> {curr}"
    
    def cmd_download(self, args):
        """Save the current session transcript"""
        transcript = "\n".join(self.terminal_ui.session_log)
        if not transcript:
            return "download: nothing to save"
        
        if args and args[0] == '--local':
            file_path = filedialog.asksaveasfilename(
                title="Save Session Transcript",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not file_path:
                return "download: canceled"
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(transcript + "\n")
                return f"Saved session to {file_path}"
            except Exception as e:
                return f"download: failed to save locally: {e}"
        
        if args:
            target = args[0]
        else:
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target = f"/session_{ts}.txt"
        
        success, error = self.filesystem.write_file(target, transcript + "\n")
        if not success:
            return f"download: {error}"
        return f"Saved session to {self.filesystem.normalize_path(target)}"
    
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
    
    def cmd_help(self, args):
        """Display available commands"""
        return """Unix Terminal - Command Help

FILE SYSTEM COMMANDS:
  ls          List directory contents (-l for details, -a for all)
  cd          Change directory
  pwd         Print working directory
  cat         Display file contents
  touch       Create empty files
  rm          Remove files/directories (-r for recursive)
  mkdir       Create directories (-p for parents)
  rmdir       Remove empty directories
  cp          Copy files/directories (-r for recursive)
  mv          Move/rename files or directories
  du          Estimate directory space usage
  df          Report filesystem disk usage
  file        Determine file type
  ln          Link files (-s for symbolic)
  find        Search for files (-name support)
  locate      Find paths by name pattern
  which       Show path of a command
  whereis     Locate binary/source/manual for command
  whatis      Display one-line manual page description
  lsof        List open files

TEXT PROCESSING COMMANDS:
  head        Display first lines of file (-n NUM)
  tail        Display last lines of file (-n NUM)
  wc          Count lines, words, and bytes
  grep        Search text patterns (-n for line numbers)
  egrep       Extended grep (alias for grep)
  fgrep       Fixed string grep (alias for grep)
  sort        Sort lines of text files
  cut         Remove sections from lines (-d DELIM -f FIELDS)
  diff        Compare files line by line
  less        View file content (no paging)
  more        View file content (alias for less)
  uniq        Remove adjacent duplicate lines
  tr          Translate or delete characters
  cksum       Calculate CRC checksum and byte count
  cmp         Compare two files byte by byte
  fold        Wrap lines to specified width (-w WIDTH)
  tee         Write to files
  strings     Print text strings from files
  awk         Pattern scanning (basic support)
  sed         Stream editor (basic support)
  iconv       Convert character encoding
  join        Join lines of files
  paste       Merge lines of files
  ex          Line editor (basic support)

PROCESS MANAGEMENT COMMANDS:
  ps          Report process status
  top         Display tasks and resource usage
  kill        Terminate processes by PID
  killall     Kill processes by name
  pgrep       List PIDs matching pattern
  pidof       Find process ID of program
  pkill       Kill processes by pattern
  nice        Run command with modified priority
  sleep       Delay for specified time
  time        Time command execution
  nohup       Run command immune to hangups

USER & SYSTEM INFORMATION:
  whoami      Display current username
  id          Print user identity (uid, gid, groups)
  finger      Display user information
  who         Show logged-in users
  w           Show who is logged in and activity
  last        Show last logins
  lastlog     Show last login information
  logname     Print user's login name
  uname       Print system information (-a for all)
  hostname    Show system hostname
  date        Display current date and time
  uptime      Show system uptime
  env         Show environment variables
  locale      Display locale information
  localedef   Define locale

USER MANAGEMENT COMMANDS:
  passwd      Change password
  su          Switch user
  sudo        Run as superuser
  chsh        Change login shell
  mesg        Control write access to terminal
  wall        Broadcast message to all users
  write       Send message to user

PERMISSION COMMANDS:
  chmod       Change file permissions
  chown       Change file owner
  chgrp       Change group ownership

ARCHIVE COMMANDS:
  tar         Create/extract tar archives

UTILITY COMMANDS:
  echo        Display line of text
  clear       Clear terminal screen
  help        Display this help message
  man         Display manual page for command
  history     Display command history
  cal         Display calendar
  banner      Display text in large format
  yes         Output string repeatedly
  seq         Generate sequence of numbers
  dirname     Extract directory from pathname
  basename    Extract filename from pathname

SPECIAL COMMANDS:
  inputmode   Switch input mode (inline|bottom)
  download [PATH] | download --local  - Save session transcript
  exit        Quit the terminal

TIPS & SHORTCUTS:
  • Tab           Auto-complete filenames
  • Up/Down       Navigate command history
  • Ctrl+C        Clear current input
  • man <cmd>     View detailed manual for any command
  • cmd > file    Redirect output to file
  • cmd >> file   Append output to file

EXAMPLES:
  ls -l documents/          List documents with details
  cd /home/student          Change to student directory
  cat file.txt              Display file contents
  grep "text" file.txt      Search for text in file
  find . -name "*.txt"      Find all .txt files
  ps                        Show running processes
  download --local          Save session to your computer
  man ls                    View manual for ls command
  
Type 'man <command>' for detailed help on specific commands."""
    
    def cmd_stub(self, args):
        """Generic stub for unimplemented commands"""
        return "Command not fully implemented"