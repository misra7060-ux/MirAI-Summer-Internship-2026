import streamlit as st

st.title("The Identity Echo Interface")
st.write("Enter your name and message below, then click on Transmit")

user_name = st.text_input("Enter your Name")

user_message = st.text_input("Enter your Message")

if st.button("Transmit"):

    if user_name.strip =="":
        st.error("Please provide your name.")

    elif user_message.strip() =="":
        st.error("Please provide your message.")
 
else:
    st.success(
        f"Transmission Successful! Greetings, {user_name}. We received Your message: {user_message}"
    )

character_count = len(user_message)
token_count = character_count/4

st.info(
    f"System check: Your message contains {character_count} characters and will consume approximately {token_count} tokens from our context windows"
)