import os
import re
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure the Generative AI model
genai.configure(api_key="AIzaSyDkT5AcdM16RJbKDYxw_kG2GOIr1hvXnrk")  # Replace with your actual API key
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initial system instruction for the chatbot
system_instruction = (
    "Hello, I am Zenify, a virtual support buddy designed to offer empathetic, supportive, and caring responses focused on both mental and physical well-being. "
    "My goal is to provide users with a safe and understanding space where they can express their thoughts and feelings. While I am not a licensed therapist, I am here to listen, guide, and suggest helpful resources or strategies to improve mental and physical health.\n\n"
    "I will always start by introducing myself as a virtual support buddy, and then I will ask the user for their name and age to provide more personalized and relevant support. "
    "Once I have the user’s name and age, I will acknowledge them and encourage a discussion about their feelings, well-being, and any struggles they may be facing.\n\n"
    "I will always prioritize the user’s mental health, offering guidance on managing stress, anxiety, or emotional challenges. If the user mentions suicidal thoughts or self-harm, I will immediately suggest they seek professional help and provide resources such as helpline numbers or online therapy options.\n\n"
    "In addition, I will recognize the connection between physical health and mental health and suggest simple and helpful physical activities (like walking, stretching, or yoga), as well as dietary recommendations that can improve mood and reduce stress (e.g., foods rich in Omega-3s, magnesium, or other mood-boosting nutrients).\n\n"
    "I will tailor my advice based on the user's stage of life (e.g., school, college, or work) and offer strategies that fit their lifestyle. I will avoid being pushy but will always suggest seeking professional support if the user’s emotional well-being requires it.\n\n"
    "In all responses, I will maintain a compassionate and non-judgmental tone, ensuring the user feels heard, supported, and encouraged to take small steps toward better mental and physical health."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# Initialize an empty chat session
chat_session = model.start_chat()

# Store user information
user_data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global user_data
    user_input = request.json.get("message", "").strip()

    # If the user's name and age are not yet collected
    if "name" not in user_data or "age" not in user_data:
        if not user_input:
            # Initial greeting message if no user input
            response_text = (
                "Hello! I'm Zenify, your virtual support buddy. It's great to connect with you. To better understand your needs and provide personalized support, could you tell me your name and age? 😊"
            )
        else:
            # Match name and age even if there are minor variations or mistakes
            name_match = re.search(r"([a-zA-Z]+)\s*(\d{1,3})", user_input, re.IGNORECASE)
            name_variation_match = re.search(r"(i'm|i am|im)\s*([a-zA-Z]+)\s*(and)\s*(i'm|im|i am)\s*(\d+)", user_input, re.IGNORECASE)

            # If the name and age are found in a simplified format (e.g., "Dhivagar 20")
            if name_match:
                user_data["name"] = name_match.group(1).capitalize()  # Capitalize name
                user_data["age"] = int(name_match.group(2))
                response_text = f"Thank you, {user_data['name']}! I’m here to chat about whatever you need—whether it’s handling stress, working through emotions, or building positive habits."

            # If the name and age are provided together in a longer format (e.g., "I'm Dhivagar and I'm 20")
            elif name_variation_match:
                user_data["name"] = name_variation_match.group(2).capitalize()  # Capitalize name
                user_data["age"] = int(name_variation_match.group(5))
                response_text = f"Thank you, {user_data['name']}! I’m here to chat about whatever you need—whether it’s handling stress, working through emotions, or building positive habits."

            else:
                response_text =  "Hello! I'm Zenify, your virtual support buddy. It's great to connect with you. To better understand your needs and provide personalized support, could you tell me your name and age? 😊"

    else:
        # Proceed with normal conversation if name and age are already collected
        chat_response = chat_session.send_message(user_input)
        response_text = chat_response.text

        # Formatting list items if any
        if "*" in response_text:
            response_text = re.sub(r"\*\s+", "<li>", response_text)  # Convert list items to <li> tags
            response_text = "<ul>" + response_text.replace("<li>", "</li><li>").strip("</li>") + "</li></ul>"

    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=True)
