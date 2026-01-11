# Local File System Implementation
import os
import datetime


class LocalFileSystem:
    """Local file system implementation using real filesystem operations"""
    
    def __init__(self, base_path):
        """
        Initialize local filesystem with a base path.
        All operations are restricted to this base path.
        """
        self.base_path = os.path.abspath(base_path)
        self.current_path = "/"
        
        # Ensure base path exists
        if not os.path.exists(self.base_path):
            raise ValueError(f"Base path does not exist: {self.base_path}")
        if not os.path.isdir(self.base_path):
            raise ValueError(f"Base path is not a directory: {self.base_path}")
    
    def _get_real_path(self, virtual_path):
        """Convert virtual path to real filesystem path, ensuring it stays within base_path"""
        if virtual_path.startswith('/'):
            # Absolute virtual path
            path = virtual_path[1:]
        else:
            # Relative path - combine with current_path
            current = self.current_path.strip('/')
            if current:
                path = os.path.join(current, virtual_path)
            else:
                path = virtual_path
        
        # Join with base path
        real_path = os.path.join(self.base_path, path)
        real_path = os.path.abspath(real_path)
        
        # Security check: ensure path is within base_path
        base_abs = os.path.abspath(self.base_path)
        if not real_path.startswith(base_abs):
            return None
        
        return real_path
    
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
    
    def list_directory(self, path=None):
        """List directory contents"""
        if path is None:
            path = self.current_path
        
        real_path = self._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return None
        
        if not os.path.isdir(real_path):
            return None
        
        try:
            return sorted(os.listdir(real_path))
        except PermissionError:
            return None
    
    def change_directory(self, path):
        """Change current directory"""
        if path == '~':
            path = '/'
        
        target_path = self.normalize_path(path)
        real_path = self._get_real_path(target_path)
        
        if not real_path or not os.path.exists(real_path):
            return False, f"cd: {path}: No such file or directory"
        
        if not os.path.isdir(real_path):
            return False, f"cd: {path}: Not a directory"
        
        self.current_path = target_path
        return True, ""
    
    def read_file(self, path):
        """Read file contents"""
        real_path = self._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return None, f"cat: {path}: No such file or directory"
        
        if os.path.isdir(real_path):
            return None, f"cat: {path}: Is a directory"
        
        try:
            with open(real_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(), ""
        except PermissionError:
            return None, f"cat: {path}: Permission denied"
        except Exception as e:
            return None, f"cat: {path}: {e}"
    
    def create_file(self, path, content=""):
        """Create a new file"""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"touch: cannot touch '{path}': Access denied"
        
        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(real_path), exist_ok=True)
            # Touch the file
            with open(real_path, 'a'):
                os.utime(real_path, None)
            return True, ""
        except Exception as e:
            return False, f"touch: {path}: {e}"
    
    def remove_file(self, path):
        """Remove a file"""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"rm: cannot remove '{path}': Access denied"
        
        if not os.path.exists(real_path):
            return False, f"rm: cannot remove '{path}': No such file or directory"
        
        if os.path.isdir(real_path):
            return False, f"rm: cannot remove '{path}': Is a directory"
        
        try:
            os.remove(real_path)
            return True, ""
        except Exception as e:
            return False, f"rm: {path}: {e}"
    
    def get_detailed_listing(self, path=None):
        """Get detailed directory listing (for ls -l)"""
        if path is None:
            path = self.current_path
        
        real_path = self._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return None
        
        if not os.path.isdir(real_path):
            return None
        
        items = []
        try:
            for name in sorted(os.listdir(real_path)):
                entry_path = os.path.join(real_path, name)
                try:
                    stat = os.stat(entry_path)
                    
                    if os.path.isdir(entry_path):
                        permissions = 'drwxr-xr-x'
                        size = '-'
                    else:
                        permissions = '-rw-r--r--'
                        size = str(stat.st_size)
                    
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                    modified = mtime.strftime('%Y-%m-%d %H:%M:%S')
                    
                    items.append({
                        'name': name,
                        'permissions': permissions,
                        'size': size,
                        'modified': modified,
                        'type': 'directory' if os.path.isdir(entry_path) else 'file'
                    })
                except Exception:
                    continue
        except PermissionError:
            return None
        
        return items
    
    def create_directory(self, path, parents=False):
        """Create a new directory. If parents is True, create intermediate directories."""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"mkdir: cannot create directory '{path}': Access denied"
        
        if os.path.exists(real_path):
            if os.path.isdir(real_path):
                return False, f"mkdir: cannot create directory '{path}': File exists"
            else:
                return False, f"mkdir: cannot create directory '{path}': File exists"
        
        try:
            if parents:
                os.makedirs(real_path, exist_ok=True)
            else:
                os.mkdir(real_path)
            return True, ""
        except FileExistsError:
            return False, f"mkdir: cannot create directory '{path}': File exists"
        except Exception as e:
            return False, f"mkdir: {path}: {e}"
    
    def remove_directory(self, path):
        """Remove an empty directory."""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"rmdir: failed to remove '{path}': Access denied"
        
        if not os.path.exists(real_path):
            return False, f"rmdir: failed to remove '{path}': No such file or directory"
        
        if not os.path.isdir(real_path):
            return False, f"rmdir: failed to remove '{path}': Not a directory"
        
        try:
            os.rmdir(real_path)
            return True, ""
        except OSError as e:
            return False, f"rmdir: {path}: {e}"
    
    def remove_recursive(self, path):
        """Remove a file or directory tree recursively."""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"rm: cannot remove '{path}': Access denied"
        
        if not os.path.exists(real_path):
            return False, f"rm: cannot remove '{path}': No such file or directory"
        
        try:
            if os.path.isdir(real_path):
                import shutil
                shutil.rmtree(real_path)
            else:
                os.remove(real_path)
            return True, ""
        except Exception as e:
            return False, f"rm: {path}: {e}"
    
    def write_file(self, path, content):
        """Create or overwrite a file with content."""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"redirect: cannot write to '{path}': Access denied"
        
        try:
            os.makedirs(os.path.dirname(real_path), exist_ok=True)
            with open(real_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, ""
        except Exception as e:
            return False, f"redirect: {path}: {e}"
    
    def append_file(self, path, content):
        """Append content to a file, creating it if missing."""
        real_path = self._get_real_path(path)
        if not real_path:
            return False, f"redirect: cannot write to '{path}': Access denied"
        
        if os.path.exists(real_path) and not os.path.isfile(real_path):
            return False, f"redirect: '{path}': Is a directory"
        
        try:
            os.makedirs(os.path.dirname(real_path), exist_ok=True)
            with open(real_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return True, ""
        except Exception as e:
            return False, f"redirect: {path}: {e}"
    
    def get_node(self, path):
        """Get filesystem node info (for compatibility)"""
        real_path = self._get_real_path(path)
        if not real_path or not os.path.exists(real_path):
            return None
        
        if os.path.isdir(real_path):
            return {'type': 'directory'}
        else:
            return {'type': 'file'}
    
    def copy_path(self, src, dst, recursive=False):
        """Copy file or directory from src to dst. For directories, recursive must be True."""
        import shutil
        
        src_real = self._get_real_path(src)
        dst_real = self._get_real_path(dst)
        
        if not src_real or not dst_real:
            return False, f"cp: Access denied"
        
        if not os.path.exists(src_real):
            return False, f"cp: cannot stat '{src}': No such file or directory"
        
        try:
            if os.path.isdir(src_real):
                if not recursive:
                    return False, f"cp: -r not specified; omitting directory '{src}'"
                if os.path.exists(dst_real) and os.path.isdir(dst_real):
                    dst_real = os.path.join(dst_real, os.path.basename(src_real))
                shutil.copytree(src_real, dst_real, dirs_exist_ok=True)
            else:
                if os.path.isdir(dst_real):
                    dst_real = os.path.join(dst_real, os.path.basename(src_real))
                shutil.copy2(src_real, dst_real)
            return True, ""
        except Exception as e:
            return False, f"cp: {e}"
    
    def move_path(self, src, dst):
        """Move/rename a file or directory."""
        import shutil
        
        src_real = self._get_real_path(src)
        dst_real = self._get_real_path(dst)
        
        if not src_real or not dst_real:
            return False, f"mv: Access denied"
        
        if not os.path.exists(src_real):
            return False, f"mv: cannot stat '{src}': No such file or directory"
        
        try:
            if os.path.isdir(dst_real):
                dst_real = os.path.join(dst_real, os.path.basename(src_real))
            shutil.move(src_real, dst_real)
            return True, ""
        except Exception as e:
            return False, f"mv: {e}"
    
    def walk(self, start_path=None):
        """Yield (path, node) for all nodes under start_path (inclusive)."""
        if start_path is None:
            start_path = self.current_path
        
        real_path = self._get_real_path(start_path)
        if not real_path or not os.path.exists(real_path):
            return
        
        normalized_start = self.normalize_path(start_path)
        
        for root, dirs, files in os.walk(real_path):
            # Calculate relative path from start
            rel_root = os.path.relpath(root, real_path)
            if rel_root == '.':
                virtual_root = normalized_start
            else:
                virtual_root = normalized_start.rstrip('/') + '/' + rel_root.replace('\\', '/')
            
            # Yield directory
            yield virtual_root, {'type': 'directory'}
            
            # Yield files
            for name in files:
                file_path = virtual_root.rstrip('/') + '/' + name
                yield file_path, {'type': 'file'}
    
    def _get_parent_and_name(self, path):
        """Helper to get parent directory and name"""
        normalized = self.normalize_path(path)
        dir_path = '/'.join(normalized.split('/')[:-1]) or '/'
        name = normalized.split('/')[-1] if normalized != '/' else ''
        return dir_path, name
