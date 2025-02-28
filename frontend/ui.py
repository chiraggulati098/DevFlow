from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
import sys

from backend.ai_model import generate_response

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

        # connect enter key to generate output
        self.input_field.returnPressed.connect(self.handle_submit)

        # submit button
        self.submit_button = QPushButton("Generate", self)
        self.submit_button.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_button)

        # output display area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

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
        
        self.output_area.append(f"User: {user_query}")
        results = self.store.query(user_query)
        
        if results:
            response = "\n".join(chunk for chunk in results)
            prompt = self.make_rag_prompt(user_query, response)
            response = generate_response(prompt)
        else:
            response = "No relevant documents found. Please try a different query."

        self.output_area.append(f"DevFlow Bot: {response}")
        self.input_field.clear()

def run_app(store):
    app = QApplication([])
    window = UI(store)
    window.show()
    sys.exit(app.exec_())