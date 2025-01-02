import streamlit as st
import openai
import base64
import io
from PIL import Image
import easyocr
import os

api_key = os.environ.get("API_KEY")
if api_key:
    print(f"API Key: {api_key}")
    # Use the API key
else:
    print("API Key not found!")

# Initialize OpenAI API key
openai.api_key =api_key

def generate_response(image_data,user_input):
    """Generate a response from OpenAI's API using the image data."""
    try:
        # Encode image data to base64
        img_b64 = base64.b64encode(image_data).decode('utf-8')
        img_type = 'image/png'  # Adjust based on your image type

        # Create the prompt with the image embedded
        prompt = f"""
                      Analyze the following image:\n![Image](data:{img_type};base64,{img_b64})
                      based on the user's message: {user_input}
                      """

        # Call OpenAI's API with the prompt
        response = openai.chat.completions.create(
          model="gpt-4o-mini",
          messages=[
              {
                  "role": "user",
                  "content": [
                      {"type": "text", "text": prompt},
                      {
                          "type": "image_url",
                          "image_url": {"url": f"data:{img_type};base64,{img_b64}"},
                      },
                  ],
              }
          ],
        )
        return response.choices[0].message.content 
    except Exception as e:
        return f"An error occurred: {str(e)}"


def main():
    st.title("ChatGPT Image Analysis with Chat Interface")
    st.write("Upload an image (JPG, PNG) and engage in a chat for analysis!")

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Image upload section
    uploaded_file = st.file_uploader("Upload an image file:", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Convert image to bytes
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_data = buffered.getvalue()

        # Chat interface
        user_input = st.chat_input("Enter your message here...")
        if user_input:
            # Display user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # Analyze the image with the user's message
            with st.spinner("Analyzing image..."):
                response = generate_response(image_data, user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.write(response)

    else:
        st.warning("Please upload an image file.")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    main()
