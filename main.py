import streamlit as st
from stegano import lsb
from PIL import Image
from cryptography.fernet import Fernet
import io

# Initialize session state variables
if 'secret_image' not in st.session_state:
    st.session_state['secret_image'] = None
if 'encryption_key' not in st.session_state:
    st.session_state['encryption_key'] = ""

def load_image(image_file):
    try:
        return Image.open(image_file)
    except Exception as e:
        st.error("Error loading image: Please ensure the file is an image.")
        return None

def clear_state():
    st.session_state['secret_image'] = None
    st.session_state['encryption_key'] = ""
    
def save_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def display_image(image_data, caption="Image"):
    if image_data:
        st.image(image_data, caption=caption, use_column_width=True)

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    try:
        decrypted_message = f.decrypt(encrypted_message).decode()
        return decrypted_message
    except Exception as e:
        st.error("Failed to decrypt. Ensure the key is correct and the message was encrypted.")
        return None
    
def display_home():
    st.header("Welcome to Stealthify!")    
    
    st.write("""
    Stealthify allows you to securely to securely embed text within images using steganography techniques. Ideal for encrypting and decrypting secret messages, this tool offers robust options for digital communication and security.
    """)

    st.write("""
    **Features:**
    - **Encoding**
    - **Decoding**
    - **Encryption**
    - **Decryption**
    """)
    
    st.write("Start by choosing Encode to hide a message, or Decode to reveal one, from the menu on the side. Explore how you can keep your messages safe and private!")

def display_about():
    st.header("About Stealthify")

    st.markdown("""
    Stealthify is designed to secure digital communications by embedding text invisibly within images. 
    This tool provides an intuitive interface for encoding, decoding, encrypting, and decrypting hidden messages, making it ideal for maintaining privacy in your interactions.

    **Core Features:**

    - **Encode:** Embed text within images invisibly, with an option to encrypt the text for additional security.
    - **Decode:** Retrieve hidden messages from images, with tools to decrypt content if it has been secured.
    - **Encrypt:** Use advanced cryptographic techniques to secure messages, ensuring they can only be accessed by those with the correct decryption key.
    - **Decrypt:** Safely decrypt received messages, ensuring complete privacy and security.

    Stealthify ensures that your communications remain confidential and secure. Whether you're a professional looking for secure ways to transmit sensitive information, or simply curious about digital privacy, Stealthify provides the tools you need.

    **Technologies Used:**
    - **Python:** For robust and flexible programming.
    - **Streamlit:** For creating an intuitive, interactive user interface.
    - **Cryptography:** Ensures secure encryption and decryption of messages.
    - **Stegano library:** A powerful library for steganographic encoding and decoding.

    Developed by Jagrati Jain.
    """)


def encode_text():
    st.subheader('Encode')
    uploaded_image = st.file_uploader("Choose an image to encode text:", type=["jpg", "png", "jpeg"])
    text_to_hide = st.text_input("Enter the text you want to hide:")
    encrypt_text = st.checkbox("Encrypt text before hiding?")

    if st.button('Hide Text in Image'):
        if uploaded_image and text_to_hide:
            image = load_image(uploaded_image)
            if image:
                if encrypt_text:
                    key = generate_key()
                    encrypted_text = encrypt_message(text_to_hide, key)
                    text_to_hide = encrypted_text.decode('utf-8')
                    st.session_state['encryption_key'] = key.decode('utf-8')
                secret = lsb.hide(image, text_to_hide)
                st.session_state['secret_image'] = save_image(secret)
                display_image(st.session_state['secret_image'], 'Image with Hidden Text')
                st.download_button("Download Image", st.session_state['secret_image'], file_name="secret_image.png")
                if encrypt_text:
                    st.success("Text encrypted and hidden in image.")
                    st.text_area("Encryption Key (keep this safe!):", st.session_state['encryption_key'], height=100, key="encryption_key_display")
        else:
            st.error("Please upload an image and enter some text to hide.")
    else:
        # Re-display the image and key if they are in session state
        if st.session_state.secret_image:
            display_image(st.session_state.secret_image, 'Image with Hidden Text')
            st.download_button("Download Image", st.session_state['secret_image'], file_name="secret_image.png")
            
            if encrypt_text:
                st.text_area("Encryption Key (keep this safe!):", st.session_state['encryption_key'], height=100, key="encryption_key_redisplay")

def decode_text():
    st.subheader('Decode')
    uploaded_secret_image = st.file_uploader("Choose an image with hidden text:", type=["jpg", "png", "jpeg"])
    decrypt_text = st.checkbox("Decrypt text after revealing?")
    key_input = st.text_area("Enter the encryption key:", value="", key="decode_key_input") if decrypt_text else None

    if st.button('Reveal Text'):
        if uploaded_secret_image is None:
            st.error("Please upload an image containing hidden text.")
            return

        secret_image = load_image(uploaded_secret_image)
        if secret_image is None:
            st.error("Invalid image format.")
            return

        revealed_text = lsb.reveal(secret_image)
        if not revealed_text:
            st.error("No hidden text found in the image.")
            return

        if decrypt_text:
            if not key_input:
                st.error("Please enter an encryption key to decrypt the text.")
                return

            try:
                key_bytes = key_input.encode('utf-8')
                decrypted_text = decrypt_message(revealed_text.encode('utf-8'), key_bytes)
                if decrypted_text:
                    st.subheader("Decoded and Decrypted Text:")
                    st.write(decrypted_text)
                else:
                    st.error("Decryption failed. Ensure the key is correct.")
            except Exception as e:
                st.error(f"Decryption error: {str(e)}")
        else:
            st.subheader("Decoded Text:")
            st.write(revealed_text)

st.title('Stealthify - Steganography Tool')
st.sidebar.markdown('---')
st.sidebar.title('Dashboard Options')
option = st.sidebar.radio("Choose an action:", ("Home", "About", "Encode", "Decode"), index=0, on_change=clear_state)
st.sidebar.markdown('---')


if option == "Home":
    display_home()
elif option == "About":
    display_about()
elif option == "Encode":
    encode_text()
elif option == "Decode":
    decode_text()
