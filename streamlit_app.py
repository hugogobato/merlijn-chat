import streamlit as st
import requests
# ----------------------------
# Configuration: Models & Info
# ----------------------------


models = {
    "o3-mini": (
        "o3 Mini",
        "Optimized for critical thinking and analysis in math and coding."
    ),
    "o1": (
        "o1",
        "Optimized for critical thinking and analysis."
    ),
    "gpt-4o": (
        "ChatGPT 4o",
        "Powered by ChatGPT 4O, optimized for speed and efficiency."
    )
}

# ----------------------------
# Function to Call the OpenAI API
# ----------------------------
def query_model(api_key, model, conversation):
    """
    Calls OpenAI's chat API with the provided API key, model, and conversation history.
    """
    # Convert conversation history to the format expected by OpenAI API
    messages = []
    for msg in conversation:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({
            "role": role,
            "content": msg["content"]
        })
    
    payload = {
        "model": model,
        "messages": messages
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    api_url = "https://api.openai.com/v1/chat/completions"
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            return "No valid response found in the API response."
        else:
            return f"API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

# ----------------------------
# Initialize Session State
# ----------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ----------------------------
# Layout: Title and Sidebar
# ----------------------------
st.title("OpenAI Chat Interface")

with st.sidebar:
    st.header("Configuration")
    # Ask for the OpenAI API key (hidden for security)
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    
    # Model selection
    model_keys = list(models.keys())
    selected_model_key = st.radio("Select a Model", model_keys)
    
    # Show model name and description
    model_name, model_description = models[selected_model_key]
    st.markdown(f"**{model_name}**")
    st.markdown(model_description)

# ----------------------------
# Main Chat Interface
# ----------------------------
st.header("Chat Interface")

# Display the conversation history
for msg in st.session_state.conversation:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**{models[selected_model_key][0]}:** {msg['content']}")

# Use a form to input a new message.
with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("Your message:", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted:
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not user_message.strip():
            st.warning("Please enter a message.")
        else:
            # Append the user's message to the conversation
            st.session_state.conversation.append({"role": "user", "content": user_message})
            with st.spinner("Waiting for the model's response..."):
                reply = query_model(api_key, selected_model_key, st.session_state.conversation)
            st.session_state.conversation.append({"role": "assistant", "content": reply})
            st.rerun()  # Force a rerun to update the conversation display


# ----------------------------
# Button to Save the Conversation
# ----------------------------
if st.session_state.conversation:
    # Prepare conversation text by concatenating all messages
    conversation_text = ""
    for msg in st.session_state.conversation:
        role = "You" if msg["role"] == "user" else models[selected_model_key][0]
        conversation_text += f"{role}: {msg['content']}\n"
    
    # Provide a download button that lets users save the conversation as a .txt file
    st.download_button(
        label="Download Conversation as .txt",
        data=conversation_text,
        file_name="conversation.txt",
        mime="text/plain"
    )