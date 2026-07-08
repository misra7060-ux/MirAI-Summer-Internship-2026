import streamlit as st

st.title("Basic Calculator")
st.write("Enter two numbers and select an operation.")

num1 = st.number_input("Enter First Number", value=0.0)
num2 = st.number_input("Enter Second Number", value=0.0)

operation = st.selectbox(
    "Choose Operation",
    ["Addition", "Subtraction", "Multiplication", "Division"]
)

if st.button("Calculate"):
    if operation == "Addition":
        result = num1 + num2
        st.success(f"Result: {result}")

    elif operation == "Subtraction":
        result = num1 - num2
        st.success(f"Result: {result}")

    elif operation == "Multiplication":
        result = num1 * num2
        st.success(f"Result: {result}")

    elif operation == "Division":
        if num2 == 0:
            st.error("Division by zero is not allowed.")
        else:
            result = num1 / num2
            st.success(f"Result: {result}")