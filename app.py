from logging import info
import typing
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from pytube import YouTube
from PIL import Image
import sys, os, requests, time
from pytube.extract import video_id
import pytube

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('YTDownloader.ui', self)
        self.setWindowTitle("YT Downloader")
        self.setFixedSize(614, 450)
        self.setWindowIcon(QIcon('yticon.ico'))
        
        photo = QPixmap('thumbnail.jpeg')
        self.thumbnail_set.setPixmap(photo)
        
        # FIND BUTTON
        self.find_button.clicked.connect(self.find_link)
        
        # DOWNLOAD BUTTON
        self.dl_button.clicked.connect(self.download_start)
        
        # PROGRESS BAR
        self.dl_progress.setValue(0)
        
        # LOCATION BUTTON
        self.loc_button.clicked.connect(self.path_loc)
        self.path_text.setText(f'C:\\Users\\{os.getlogin()}\\Downloads')
        
        self.show()
        
    def find_link(self):
        self.link = self.link_text.text()
        if self.link == "":
            error = QMessageBox.warning(self,
                                        "Kesalahan",
                                        "Masukkan Link terlebih dahulu",
                                        QMessageBox.StandardButton.Ok)
        else:
            try:
                yt = YouTube(self.link)
            except:
                error = QMessageBox.warning(self,
                                        "Kesalahan",
                                        "Link tidak valid atau tidak ada koneksi",
                                        QMessageBox.StandardButton.Ok)
                return None
                
            thumbnail = yt.thumbnail_url
            get_request_img = requests.get(thumbnail)
            images = open("thumbnail.png", 'wb')
            images.write(get_request_img.content)
            images.close()
            
            image = Image.open('thumbnail.png')
            new_image = image.resize((341, 191))
            new_image.save('thumbnail.png')
            
            photo = QPixmap('thumbnail.png')
            self.thumbnail_set.setPixmap(photo)
            
            self.judul.setText(f'{yt.title}')
            self.author.setText(f'{yt.author}')
            self.pub_date.setText(f'{yt.publish_date}')
            self.view.setText(f'{yt.views} view(s)')
            self.durasi.setText(f'{yt.length} sec')
            self.peringkat.setText(f'{yt.rating} / 5.0')
            
            # COMBOBOX
            self.list_res = self.resolution(yt)
            self.cb_res.clear()
            self.cb_res.addItems(self.list_res)
            
    def resolution(self, yt):
        res = []
        for i in yt.streams.filter(progressive=True, file_extension='mp4'):
            get_res = i.resolution
            if get_res not in res and get_res is not None:
                res.append(get_res)
                
        res.sort(reverse=True)
        return res

    def path_loc(self):
        location = QFileDialog.getExistingDirectory()
        
        if location:
            self.path_text.setText(location)
            
    def dl_prep(self):
        self.res = self.cb_res.currentText()
        self.loc = self.path_text.text()
        yt = YouTube(self.link, on_progress_callback=self.progress_bar)
        self.video = yt.streams.filter(progressive=True, file_extension='mp4', resolution=self.res).first()
        self.vid_size = self.video.filesize
        
    def progress_bar(self, chunk, file_handle, bytes_remaining):
        size = self.vid_size
        perc = (float(bytes_remaining) / float(size)) * float(100)
        self.cnt = ("%.2f" % (100-perc))
        self.dl_progress.setValue(float(self.cnt))
        
    def finish_notification(self):
        self.dl_progress.setValue(0)
        self.dl_button.setEnabled(True)
    
    def download_start(self):
        self.dl_prep()
        self.dl_button.setEnabled(False)
        self.thread2 = DownloadBack(self.loc, self.video)
        self.thread2.start()
        
class DownloadBack(QThread):        
    def __init__(self, loc, vid):
        super().__init__()
        self.loc = loc
        self.vid = vid
        
    def run(self):
        self.vid.download(self.loc)
        
def main():
    app = QApplication(sys.argv)
    #app.setStyle('Fusion')
    window = Ui()
    app.exec()

if __name__ == "__main__":
    main()
    