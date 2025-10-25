from flask import Blueprint, request, jsonify, session, render_template
import google.generativeai as genai
import json
import uuid
import os
from datetime import datetime
import re

ai_chat_bp = Blueprint('ai_chat', __name__)

# ===== CONFIGURATION =====
# PUT YOUR GEMINI API KEY HERE
GEMINI_API_KEY = "AIzaSyD8bqyzh81Tt8x97YA5Lzg3MVANk0-GrRU"  # Replace with your actual API key

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model (using available models)
# Try different models for compatibility
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Using gemini-2.0-flash model")
except Exception as e:
    print(f"⚠️ gemini-2.0-flash not available: {e}")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Using gemini-2.5-flash model")
    except Exception as e2:
        print(f"⚠️ gemini-2.5-flash not available: {e2}")
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            print("✅ Using gemini-flash-latest model")
        except Exception as e3:
            print(f"⚠️ gemini-flash-latest not available: {e3}")
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-001')
                print("✅ Using gemini-2.0-flash-001 model")
            except Exception as e4:
                print(f"⚠️ All models failed: {e4}")
                # Last resort - use the basic model
                model = genai.GenerativeModel('gemini-2.0-flash')
                print("✅ Using fallback model")

# Chat storage (in production, use a database)
chat_storage = {}

def init_app():
    """Initialize the AI chat module"""
    pass

@ai_chat_bp.route('/ai-chat')
def ai_chat_page():
    """Render the AI chat page"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    return render_template('ai_chat.html')

@ai_chat_bp.route('/ai-chat/send', methods=['POST'])
def send_message():
    """Handle AI chat messages"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        chat_id = data.get('chat_id')
        files = data.get('files', [])
        tool = data.get('tool')
        code_mode = data.get('code_mode', False)
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Generate chat ID if new chat
        if not chat_id:
            chat_id = str(uuid.uuid4())
        
        # Prepare context for AI
        context = prepare_ai_context(message, files, tool, code_mode)
        
        # Get AI response
        print(f"🔧 Sending request to Gemini API...")
        print(f"📝 Message: {message[:100]}...")
        print(f"🔑 API Key configured: {bool(GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE')}")
        print(f"💻 Code Mode: {code_mode}")
        print(f"🛠️ Tool: {tool}")
        
        ai_response = get_ai_response(context)
        
        print(f"📥 AI Response: {ai_response[:100]}...")
        
        # Process response for better formatting
        processed_response = process_ai_response(ai_response, code_mode)
        
        # Extract code blocks
        code_blocks = extract_code_blocks(ai_response)
        
        # Store chat in memory (in production, use database)
        store_chat_message(chat_id, session['uid'], message, processed_response)
        
        return jsonify({
            'response': processed_response,
            'chat_id': chat_id,
            'code_blocks': code_blocks
        })
        
    except Exception as e:
        print(f"Error in AI chat: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

def prepare_ai_context(message, files, tool, code_mode):
    """Prepare context for AI based on user input and settings"""
    
    # Base system prompt
    system_prompt = """You are LABMentor AI, an intelligent mentor for university computer lab students. 
    Your role is to help students with:
    - Lab issues and technical problems
    - Coding questions and debugging
    - Academic programming concepts
    - System administration tasks
    - Network and connectivity issues
    
    Always provide solutions in clear bullet points and be encouraging and supportive.
    If the user is asking about code, provide well-commented examples.
    If it's a lab issue, provide step-by-step troubleshooting.
    Be concise but comprehensive in your responses."""
    
    # Add tool-specific instructions
    if tool:
        tool_instructions = get_tool_instructions(tool)
        system_prompt += f"\n\nSpecial focus: {tool_instructions}"
    
    # Add code mode instructions
    if code_mode:
        print("🔧 CODE MODE ENABLED - Adding specialized coding instructions")
        system_prompt += """
        
CODING MODE ENABLED - You are now a specialized coding mentor:
- Provide detailed, well-commented code solutions
- Include error handling and best practices
- Suggest optimizations and performance improvements
- Explain the logic and approach step-by-step
- Provide multiple solution approaches when applicable
- Include testing strategies and debugging tips
- Focus on production-ready, maintainable code
- Always explain WHY you chose a particular approach
- Include edge cases and potential issues to watch for"""
    
    # Add file context if files are uploaded
    file_context = ""
    if files:
        file_context = "\n\nUser has uploaded the following files for context:\n"
        for file in files:
            if file.get('content'):
                file_context += f"File: {file['name']}\nContent: {file['content'][:1000]}...\n\n"
    
    # Combine everything
    full_context = f"{system_prompt}\n\n{file_context}\n\nUser Question: {message}"
    
    return full_context

def get_tool_instructions(tool):
    """Get specific instructions based on selected tool"""
    tool_instructions = {
        'code_generation': "Focus on generating clean, efficient code with proper comments and best practices.",
        'debugging': "Help identify and fix bugs in code, explain common debugging techniques and tools.",
        'explanation': "Provide detailed explanations of concepts, algorithms, and technical topics.",
        'optimization': "Suggest performance improvements and optimization techniques for code and systems.",
        'documentation': "Help create clear documentation, comments, and code documentation.",
        'troubleshooting': "Provide systematic troubleshooting steps for technical issues."
    }
    return tool_instructions.get(tool, "Provide general assistance with the topic.")

def get_ai_response(context):
    """Get response from Gemini AI"""
    try:
        # Check if API key is properly configured
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("Error: Gemini API key not configured")
            return "AI service is not configured. Please contact the administrator."
        
        # Generate content using Gemini
        response = model.generate_content(context)
        
        # Check if response is valid
        if not response or not response.text:
            print("Error: Empty response from Gemini")
            return "I received an empty response. Please try rephrasing your question."
        
        return response.text
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Provide more specific error messages
        if "API_KEY_INVALID" in str(e) or "invalid" in str(e).lower():
            return "AI service authentication failed. Please contact the administrator."
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            return "AI service quota exceeded. Please try again later."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            return "Network connection issue. Please check your internet connection and try again."
        else:
            return f"I encountered an error: {str(e)[:100]}... Please try again or contact support."

def process_ai_response(response, code_mode):
    """Process AI response for better formatting"""
    
    # Ensure bullet points are properly formatted
    response = re.sub(r'^(\d+\.|\*|\-)\s+', '• ', response, flags=re.MULTILINE)
    
    # Add emphasis to important points
    response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)
    response = re.sub(r'\*(.*?)\*', r'<em>\1</em>', response)
    
    # Format code snippets in text
    response = re.sub(r'`([^`]+)`', r'<code>\1</code>', response)
    
    return response

def extract_code_blocks(text):
    """Extract code blocks from AI response"""
    code_blocks = []
    
    # Find code blocks (between ``` or in specific patterns)
    code_pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    for language, code in matches:
        code_blocks.append({
            'language': language or 'text',
            'code': code.strip()
        })
    
    # Also look for inline code that might be code blocks
    lines = text.split('\n')
    current_code = []
    current_language = 'text'
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if current_code:
                    code_blocks.append({
                        'language': current_language,
                        'code': '\n'.join(current_code).strip()
                    })
                current_code = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
                current_language = line.strip()[3:].strip() or 'text'
        elif in_code_block:
            current_code.append(line)
    
    return code_blocks

def store_chat_message(chat_id, user_id, user_message, ai_response):
    """Store chat message in memory (in production, use database)"""
    if chat_id not in chat_storage:
        chat_storage[chat_id] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
    
    chat_storage[chat_id]['messages'].append({
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'ai_response': ai_response
    })

@ai_chat_bp.route('/ai-chat/history')
def get_chat_history():
    """Get chat history for current user"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = session['uid']
    user_chats = []
    
    for chat_id, chat_data in chat_storage.items():
        if chat_data['user_id'] == user_id:
            user_chats.append({
                'chat_id': chat_id,
                'created_at': chat_data['created_at'],
                'message_count': len(chat_data['messages'])
            })
    
    return jsonify({'chats': user_chats})

@ai_chat_bp.route('/ai-chat/history/<chat_id>')
def get_chat_messages(chat_id):
    """Get messages for a specific chat"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    if chat_id not in chat_storage:
        return jsonify({'error': 'Chat not found'}), 404
    
    chat_data = chat_storage[chat_id]
    if chat_data['user_id'] != session['uid']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'messages': chat_data['messages']})

@ai_chat_bp.route('/ai-chat/delete/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a specific chat"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    if chat_id not in chat_storage:
        return jsonify({'error': 'Chat not found'}), 404
    
    chat_data = chat_storage[chat_id]
    if chat_data['user_id'] != session['uid']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete the chat
    del chat_storage[chat_id]
    
    return jsonify({'message': 'Chat deleted successfully'})

@ai_chat_bp.route('/ai-chat/delete-all', methods=['DELETE'])
def delete_all_chats():
    """Delete all chats for the current user"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    # Delete all chats for this user
    user_chats = [chat_id for chat_id, chat_data in chat_storage.items() 
                  if chat_data['user_id'] == session['uid']]
    
    for chat_id in user_chats:
        del chat_storage[chat_id]
    
    return jsonify({'message': f'Deleted {len(user_chats)} chats successfully'})

@ai_chat_bp.route('/ai-chat/test')
def test_ai_connection():
    """Test AI connection"""
    if 'uid' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        # Test with a simple question
        test_context = "Hello, this is a test message. Please respond with 'AI connection successful' if you can read this."
        response = get_ai_response(test_context)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'api_key_configured': bool(GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE")
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'api_key_configured': bool(GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE")
        })

# ===== GEMINI API CONFIGURATION NOTES =====
"""
To use this AI chat system:

1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
2. Replace 'YOUR_GEMINI_API_KEY_HERE' with your actual API key
3. Install required packages:
   pip install google-generativeai

4. The system will automatically:
   - Use Gemini Pro model for responses
   - Format responses with bullet points
   - Extract and highlight code blocks
   - Store chat history per user
   - Handle file uploads for context

5. Available tools in the interface:
   - Code Generation
   - Debugging
   - Explanation
   - Optimization
   - Documentation
   - Troubleshooting

6. Features:
   - Real-time chat with AI mentor
   - File upload for context
   - Code mode for programming help
   - Chat history storage
   - Copy-to-clipboard functionality
   - Responsive design matching LABMentor theme
"""
