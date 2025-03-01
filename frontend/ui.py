from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
import sys

from backend.ai_model import generate_response

class UI(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("DevFlow")
        self.setGeometry(100, 100, 800, 600)    # window size

        layout = QVBoxLayout()

        # chat display area 
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: #121B22;
                border: none;
            }
            QListWidget::item {
                border: none;
                margin: 5px;
            }
            QScrollBar:vertical {
                background-color: #121B22;
                width: 12px;
                margin: 16px 0 16px 0;
                border: 1px solid #121B22;
            }
            QScrollBar::handle:vertical {
                background-color: #888888;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.chat_list.verticalScrollBar().setSingleStep(1)
        layout.addWidget(self.chat_list)

        # input area layout (horizontal for input and button)
        input_layout = QHBoxLayout()
        
        # input field
        self.input_field = QLineEdit(self)
        self.input_field.setStyleSheet("""
            background-color: #2A2F32;
            color: white;
            border: 1px solid #3A3F41;
            border-radius: 20px;
            padding: 10px 15px;
            font-size: 14px;
        """)
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.handle_submit)  # Keep Enter key functionality
        input_layout.addWidget(self.input_field)

        # generate button
        self.submit_button = QPushButton("Generate", self)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #00A884;  
                color: white;
                border-radius: 10px;  
                border: 1px solid #00A884; 
                padding: 5px 10px;  
            }
            QPushButton:hover {
                background-color: #008C74;  
            }
        """)
        self.submit_button.clicked.connect(self.handle_submit)
        input_layout.addWidget(self.submit_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        # Apply window background
        self.setStyleSheet("background-color: #121B22;")

    def add_message(self, sender, message):
        '''
        Add a message to the chat list with styling.
        '''
        item = QListWidgetItem()
        widget = QLabel(message)
        widget.setWordWrap(True)

        # set background color based on sender
        bg_color = '#6495ED' if sender == 'DevFlow Bot' else '#005C4B' 
        widget.setStyleSheet(f"""
            background-color: {bg_color};
            color: white;
            border-radius: 10px;
            padding: 15px;
            max-width: 700px;
        """)
        
        widget.adjustSize()
        size = widget.sizeHint()
        size.setHeight(size.height() + 5)  
        item.setSizeHint(size)

        # align messages (right for user, left for bot)
        if sender == 'User':
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            widget.setStyleSheet(widget.styleSheet() + "margin-left: 180px;")
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            widget.setStyleSheet(widget.styleSheet() + "margin-right: 180px;")

        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, widget)
        self.chat_list.scrollToBottom()

    def make_rag_prompt(self, query, relevant_chunks):
        '''
        Construct a prompt for Gemini to generate a structured output
        '''
        escaped_chunks = " ".join(relevant_chunks).replace("'", "").replace('"', '').replace("\n", " ")
        prompt = f"""You are a helpful and informative bot that answers questions using text from the reference chunks below. Provide a clear and concise response, such as a step-by-step guide or explanation, based on the query. If the chunks are irrelevant, provide a general answer based on your knowledge.
        QUESTION: '{query}'
        REFERENCE CHUNKS: '{escaped_chunks}'
        ANSWER:
        """

        return prompt

    def handle_submit(self):
        user_query = self.input_field.text()
        if not user_query:
            return
        
        self.add_message('User', user_query)
        results = self.store.query(user_query)
        
        if results:
            prompt = self.make_rag_prompt(user_query, results)
            response = generate_response(prompt)
        else:
            response = "No relevant documents found. Please try a different query."

        self.add_message('DevFlow Bot', response)
        self.input_field.clear()

def run_app(store):
    app = QApplication([])
    window = UI(store)
    window.show()
    sys.exit(app.exec_())