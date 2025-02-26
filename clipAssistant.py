import sys
import pyperclip
import win32gui
import win32process
import psutil
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                            QCheckBox, QVBoxLayout, QLabel, QStatusBar)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

class ClipboardThread(QThread):
    update_status = pyqtSignal(str)

    def __init__(self, add_quote, add_newline, target_process=None):
        super().__init__()
        self.running = False
        self.add_quote = add_quote
        self.add_newline = add_newline
        self.last_clip = ""
        self.target_process = target_process

    def run(self):
        self.running = True
        while self.running:
            content = pyperclip.paste()
            if content and content != self.last_clip:
                self.process_content(content)
                self.last_clip = content
            self.msleep(1000)

    def process_content(self, content):
        if self.target_process and not self.is_target_process():
            return
        
        if self.add_quote:
            processed = "> " + content
        else:
            processed = content

        try:
            with open("clips.md", "a", encoding="utf-8") as f:
                f.write(processed)
                if self.add_newline:
                    f.write("\n\n")
                self.update_status.emit(f"已保存到文件: {processed[:20]}...")
        except Exception as e:
            self.update_status.emit(f"保存失败: {str(e)}")

    def is_target_process(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name().lower() == self.target_process.lower()
        except:
            return False

class ClipboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('resource\\app.ico'))
        layout = QVBoxLayout()

        self.quote_check = QCheckBox("添加引用符号（>）", self)
        self.quote_check.setChecked(True)
        self.newline_check = QCheckBox("自动换行", self)
        self.newline_check.setChecked(True)
        layout.addWidget(self.quote_check)
        layout.addWidget(self.newline_check)

        self.process_btn = QPushButton("选择监听进程", self)
        self.process_label = QLabel("当前监听：所有进程")
        layout.insertWidget(2, self.process_label)
        layout.insertWidget(2, self.process_btn)

        self.start_btn = QPushButton("开始监听", self)
        self.exit_btn = QPushButton("退出程序", self)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.exit_btn)

        self.status = QStatusBar()
        layout.addWidget(self.status)

        self.start_btn.clicked.connect(self.toggle_listen)
        self.exit_btn.clicked.connect(self.close)
        self.process_btn.clicked.connect(self.set_target_process)

        self.setLayout(layout)
        self.setWindowTitle('剪贴板助手')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def toggle_listen(self):
        if self.thread and self.thread.isRunning():
            self.thread.running = False
            self.thread.quit()
            self.start_btn.setText("开始监听")
            self.status.showMessage("监听已停止")
        else:
            self.thread = ClipboardThread(
                self.quote_check.isChecked(),
                self.newline_check.isChecked(),
                getattr(self, 'target_process', None)
            )
            self.thread.update_status.connect(self.status.showMessage)
            self.thread.start()
            self.start_btn.setText("停止监听")
            self.status.showMessage("开始监听剪贴板...")

    def set_target_process(self):
        self.status.showMessage("请点击目标窗口...")
        self.initial_hwnd = int(self.winId())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_foreground_window)
        self.timer.start(100)

    def check_foreground_window(self):
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != self.initial_hwnd:
            _, pid = win32process.GetWindowThreadProcessId(current_hwnd)
            process = psutil.Process(pid)
            self.target_process = process.name()
            self.process_label.setText(f"当前监听：{self.target_process}")
            self.status.showMessage(f"已设置监听进程：{self.target_process}")
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ClipboardApp()
    sys.exit(app.exec_())