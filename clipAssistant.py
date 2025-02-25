import sys
import pyperclip
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                            QCheckBox, QVBoxLayout, QLabel, QStatusBar)
from PyQt5.QtCore import QThread, pyqtSignal

class ClipboardThread(QThread):
    update_status = pyqtSignal(str)

    def __init__(self, add_quote, add_newline):
        super().__init__()
        self.running = False
        self.add_quote = add_quote
        self.add_newline = add_newline
        self.last_clip = ""

    def run(self):
        self.running = True
        while self.running:
            content = pyperclip.paste()
            if content and content != self.last_clip:
                self.process_content(content)
                self.last_clip = content
            self.msleep(1000)

    def process_content(self, content):
        # 处理引用符号
        if self.add_quote:
            processed = "> " + content
        else:
            processed = content

        # 写入Markdown文件
        try:
            with open("clipboard_log.md", "a", encoding="utf-8") as f:
                f.write(processed)
                if self.add_newline:
                    f.write("\n\n")  # 添加两个换行
                self.update_status.emit(f"已保存到文件: {processed[:20]}...")
        except Exception as e:
            self.update_status.emit(f"保存失败: {str(e)}")

class ClipboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.initUI()

    def initUI(self):
        # 界面布局
        layout = QVBoxLayout()

        # 设置选项
        self.quote_check = QCheckBox("添加引用符号（>）", self)
        self.newline_check = QCheckBox("自动换行", self)
        layout.addWidget(self.quote_check)
        layout.addWidget(self.newline_check)

        # 控制按钮
        self.start_btn = QPushButton("开始监听", self)
        self.exit_btn = QPushButton("退出程序", self)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.exit_btn)

        # 状态栏
        self.status = QStatusBar()
        layout.addWidget(self.status)

        # 连接信号
        self.start_btn.clicked.connect(self.toggle_listen)
        self.exit_btn.clicked.connect(self.close)

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
                self.newline_check.isChecked()
            )
            self.thread.update_status.connect(self.status.showMessage)
            self.thread.start()
            self.start_btn.setText("停止监听")
            self.status.showMessage("开始监听剪贴板...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ClipboardApp()
    sys.exit(app.exec_())