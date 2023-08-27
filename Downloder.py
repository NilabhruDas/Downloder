import os
import time
import requests
import tkinter as tk
from tkinter import filedialog
from zipfile import ZipFile
from threading import Thread
from tkinter import ttk

class SoftwareDownloaderApp:
    def __init__(self, root):

        self.root = root
        self.root.title("Software Downloader")
        self.root.geometry('350x200')

        self.paused = False
        self.cancelled = False

        self.label = tk.Label(root, text="Enter URL:")
        self.label.pack()

        self.url_entry = tk.Entry(root)
        self.url_entry.pack()

        self.browse_button = tk.Button(root, text="Browse",padx=20, command=self.browse_download_path)
        self.browse_button.pack()

        self.download_button = tk.Button(root, text="Download",padx=12, command=self.download_software)
        self.download_button.pack()

        self.download_path = ""

        self.pause_button = tk.Button(root, text="Pause", padx=23, command=self.pause_download)
        self.pause_button.pack()

        self.cancel_button = tk.Button(root, text="Cancel",padx=21, command=self.cancel_download)
        self.cancel_button.pack()

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()



    def browse_download_path(self):
        self.download_path = filedialog.askdirectory()

    def download_software(self):
        url = self.url_entry.get()
        if url and self.download_path:
            try:
                download_thread = Thread(target=self._download_thread, args=(url,))
                download_thread.start()
            except Exception as e:
                self.show_message(f"Error starting download: {e}")
        else:
            self.show_message("Please enter a URL and select a download path.")

    def pause_download(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")

    def cancel_download(self):
        self.cancelled = True

    def _download_thread(self, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            filename = os.path.basename(url)
            download_file_path = os.path.join(self.download_path, filename)

            with open(download_file_path, 'wb') as file:
                total_length = int(response.headers.get('content-length'))
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if self.cancelled:
                        self.show_message("Download cancelled.")
                        break
                    while self.paused:
                        time.sleep(0.1)  # Sleep while paused
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        self.update_progress(downloaded, total_length)

            if self.cancelled or downloaded < total_length:
                os.remove(download_file_path)  # Remove partially downloaded or incomplete file
                if self.cancelled:
                    self.show_message("Download cancelled.")
                else:
                    self.show_message("Download incomplete. File removed.")
            else:
                self.show_message("Download completed successfully.")
                self.extract_software(download_file_path)
        except requests.exceptions.RequestException as e:
            self.show_message(f"Error downloading software: {e}")
            if os.path.exists(download_file_path):
                os.remove(download_file_path)  # Remove partially downloaded file


    def extract_software(self, file_path):
        with ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_path)
        os.remove(file_path)
        self.show_message("Software extracted successfully.")

    def update_progress(self, downloaded, total_length):
        progress_percent = (downloaded / total_length) * 100
        self.progress_bar["value"] = progress_percent
        self.root.title(f"Downloading... {progress_percent:.2f}%")

    def show_message(self, message):
        self.progress_bar["value"] = 0
        self.root.title("Software Downloader")
        message_box = tk.messagebox.showinfo("Message", message)



if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareDownloaderApp(root)
    root.mainloop()
