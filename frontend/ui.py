from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
import sys

class UI(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
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
        self.submit_button = QPushButton("Generate", self)
        self.submit_button.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_button)

        # output display area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def handle_submit(self):
        user_query = self.input_field.text()
        if user_query:
            self.output_area.append(f"User: {user_query}")

            results = self.store.query(user_query)
        
        if results:
            response = "\n".join(chunk for chunk in results)
        else:
            response = "No relevant documents found."

        self.output_area.append(f"DevFlow Bot: {response}")
        self.input_field.clear()

def run_app(store):
    app = QApplication([])
    window = UI(store)
    window.show()
    sys.exit(app.exec_())