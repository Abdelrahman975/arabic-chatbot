"""
Web application for the Arabic chatbot.
"""

import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from query import QueryEngine
from config import HOST, PORT, DEFAULT_NO_ANSWER_MSG

# Create FastAPI app
app = FastAPI(title="Arabic FAQ Chatbot")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Set up templates
templates = Jinja2Templates(directory="templates")

# Initialize query engine
query_engine = None

class QuestionRequest(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    """Initialize the query engine on startup."""
    global query_engine
    query_engine = QueryEngine()

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask_question(question_request: QuestionRequest):
    """API endpoint to ask a question."""
    question = question_request.question
    
    if not question.strip():
        return {"answer": DEFAULT_NO_ANSWER_MSG}
    
    try:
        answer = query_engine.answer_question(question)
        return {"answer": answer}
    except Exception as e:
        print(f"Error processing question: {e}")
        return {"answer": DEFAULT_NO_ANSWER_MSG}

if __name__ == "__main__":
    import uvicorn
    
    # Create the templates directory
    os.makedirs("templates", exist_ok=True)
    
    # Create a simple HTML template
    html_content = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>الروبوت المحادث للأسئلة الشائعة</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                direction: rtl;
                text-align: right;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .chat-box {
                height: 400px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 20px;
            }
            .message {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 5px;
                max-width: 80%;
            }
            .user-message {
                background-color: #e6f7ff;
                margin-left: auto;
            }
            .bot-message {
                background-color: #f0f0f0;
                margin-right: auto;
            }
            .input-container {
                display: flex;
            }
            #question-input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            #send-button {
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                margin-right: 10px;
                cursor: pointer;
                font-size: 16px;
            }
            #send-button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>روبوت الأسئلة الشائعة للمكتبات الوقفية</h1>
            <div class="chat-box" id="chat-box">
                <div class="message bot-message">مرحبًا! كيف يمكنني مساعدتك اليوم؟</div>
            </div>
            <div class="input-container">
                <button id="send-button">إرسال</button>
                <input type="text" id="question-input" placeholder="اكتب سؤالك هنا...">
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const chatBox = document.getElementById('chat-box');
                const questionInput = document.getElementById('question-input');
                const sendButton = document.getElementById('send-button');

                function sendQuestion() {
                    const question = questionInput.value.trim();
                    if (!question) return;

                    // Add user message to chat
                    addMessage(question, 'user-message');
                    
                    // Clear input
                    questionInput.value = '';
                    
                    // Call API
                    fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Add bot response to chat
                        addMessage(data.answer, 'bot-message');
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        addMessage('عذرًا، حدث خطأ في معالجة سؤالك.', 'bot-message');
                    });
                }

                function addMessage(text, className) {
                    const messageDiv = document.createElement('div');
                    messageDiv.classList.add('message', className);
                    messageDiv.textContent = text;
                    chatBox.appendChild(messageDiv);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                // Event listeners
                sendButton.addEventListener('click', sendQuestion);
                questionInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendQuestion();
                    }
                });
            });
        </script>
    </body>
    </html>
    '''
    
    # Write the HTML template to a file
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Run the server
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)