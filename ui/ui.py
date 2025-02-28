from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.ai_model import generate_response

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("DevFlow")
        self.setGeometry(100, 100, 600, 400)    # window size

        layout = QVBoxLayout()

        # label
        self.label = QLabel("Enter development query: ")
        layout.addWidget(self.label)

        # text input
        self.input_field = QLineEdit(self)
        layout.addWidget(self.input_field)

        # submit button
        self.submit_buttom = QPushButton("Generate", self)
        self.submit_buttom.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_buttom)

        # output display area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def handle_submit(self):
        user_query = self.input_field.text()
        if user_query:
            self.output_area.append(f"User: {user_query}")

            ai_response = generate_response(user_query)
            self.output_area.append(f"DevFlow Bot: {ai_response}")

            self.input_field.clear()

def run_app():
    app = QApplication([])
    window = UI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()