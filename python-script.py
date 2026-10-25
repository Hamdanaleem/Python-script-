#!/usr/bin/env python3

import os
import http.server
import socketserver
import argparse
import socket
import io
from urllib.parse import unquote
import mimetypes
import html


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with enhanced directory listing"""

    def list_directory(self, path):
        """Enhanced directory listing with file sizes and better formatting"""
        try:
            list_dir = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        list_dir.sort(key=lambda a: a.lower())

        # HTML template for directory listing
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Directory listing for {html.escape(self.path)}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                a {{ text-decoration: none; color: #0066cc; }}
                a:hover {{ text-decoration: underline; }}
                .file {{ color: #333; }}
                .dir {{ color: #0066cc; font-weight: bold; }}
                .size {{ text-align: right; }}
            </style>
        </head>
        <body>
            <h1>Directory listing for {html.escape(self.path)}</h1>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Size</th>
                </tr>
        """

        # Add parent directory link if not at root
        if self.path != '/':
            html_content += '<tr><td><a href="../">ðŸ“ Parent Directory</a></td><td>Directory</td><td>-</td></tr>\n'

        # Add files and directories
        for name in list_dir:
            # Skip hidden files and certain files from .gitignore
            if name.startswith('.') and name not in ['.gitignore']:
                continue

            fullname = os.path.join(path, name)
            displayname = linkname = name

            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
                file_type = "Directory"
                size = "-"
                icon = "ðŸ“"
                css_class = "dir"
            elif os.path.islink(fullname):
                displayname = name + "@"
                file_type = "Link"
                size = "-"
                icon = "ðŸ”—"
                css_class = "file"
            else:
                file_type = "File"
                try:
                    size = self.format_size(os.path.getsize(fullname))
                except OSError:
                    size = "Unknown"

                # Get file icon based on extension
                _, ext = os.path.splitext(name.lower())
                icon = self.get_file_icon(ext)
                css_class = "file"

            html_content += f'''
                <tr>
                    <td><a href="{html.escape(linkname)}" class="{css_class}">{icon} {html.escape(displayname)}</a></td>
                    <td>{file_type}</td>
                    <td class="size">{size}</td>
                </tr>
            '''

        html_content += """
            </table>
            <hr>
            <p><em>Python File Server</em></p>
        </body>
        </html>
        """

        # Convert to bytes and send
        encoded = html_content.encode('utf-8', 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def get_file_icon(self, ext):
        """Get emoji icon for file type"""
        icons = {
            '.txt': 'ðŸ“„', '.md': 'ðŸ“„', '.pdf': 'ðŸ“„',
            '.jpg': 'ðŸ–¼ï¸', '.jpeg': 'ðŸ–¼ï¸', '.png': 'ðŸ–¼ï¸', '.gif': 'ðŸ–¼ï¸', '.svg': 'ðŸ–¼ï¸',
            '.mp4': 'ðŸŽ¥', '.avi': 'ðŸŽ¥', '.mov': 'ðŸŽ¥',
            '.mp3': 'ðŸŽµ', '.wav': 'ðŸŽµ', '.flac': 'ðŸŽµ',
            '.zip': 'ðŸ“¦', '.tar': 'ðŸ“¦', '.gz': 'ðŸ“¦', '.rar': 'ðŸ“¦',
            '.py': 'ðŸ', '.js': 'ðŸ“„', '.html': 'ðŸŒ', '.css': 'ðŸŽ¨',
            '.json': 'ðŸ“„', '.xml': 'ðŸ“„', '.log': 'ðŸ“‹'
        }
        return icons.get(ext, 'ðŸ“„')


def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"


def start_server(port=7000, directory=None):
    """Start the HTTP file server"""
    if directory:
        os.chdir(directory)

    # Get local IP address
    local_ip = get_local_ip()

    # Create server
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        print(f"ðŸš€ File Server Started!")
        print(f"ðŸ“ Serving directory: {os.getcwd()}")
        print(f"ðŸŒ Local access: http://localhost:{port}")
        print(f"ðŸŒ Network access: http://{local_ip}:{port}")
        print(f"â¹ï¸  Press Ctrl+C to stop the server")
        print("-" * 50)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nðŸ›‘ Server stopped by user")
            httpd.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple HTTP File Server")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Port to serve on (default: 8000)")
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Directory to serve (default: current directory)")

    args = parser.parse_args()

    try:
        start_server(args.port, args.directory)
    except PermissionError:
        print(f"âŒ Permission denied: Cannot bind to port {args.port}")
        print("ðŸ’¡ Try using a port number higher than 1024")
    except OSError as e:
        print(f"âŒ Error: {e}")
        print("ðŸ’¡ Port might already be in use. Try a different port with -p option")