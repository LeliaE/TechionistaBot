from gpt_index import SimpleDirectoryReader, GPTListIndex, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain.chat_models import ChatOpenAI
import gradio as gr
import streamlit as st
import sys
import os
import openai
import toml
import webbrowser
import discord
from discord.ext import commands

os.environ["OPENAI_API_KEY"] = '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'

# STYLE
config = toml.load("config.toml")

st.set_page_config(
    page_title="The Techionista Academy Chatbot",
    page_icon=":robot_face:",  # Change this to your desired icon
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown(
    """
    <style>
    .reportview-container {
        background: url("wallpaper.png");
    }
   </style>
    """,
    unsafe_allow_html=True
)

# DISCORD
intents = discord.Intents.all()
intents.typing = False  # Disable typing events
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Add a command to interact with the bot
@bot.command()
async def chat(ctx, *, prompt: str):
    # Check if the command was issued in a specific channel
    if ctx.channel.id == 1137999474417991720:
        index = GPTSimpleVectorIndex.load_from_disk('index.json')
        
        # Show typing indicator while processing
        async with ctx.typing():
            response = index.query(prompt, response_mode="compact")
        
        await ctx.send(response.response)

    
# Function to run the Discord bot in a separate thread
def run_discord_bot():
    bot.run('MTEzNzk5NjY4MDYxMzA4NTMxNQ.GK34tN.pkv1bBsSQPIiUFqfWVSptomktI7x2Qqxxn-qOk')


# Sidebar content
st.sidebar.image("TechionistaAcademy_Horizontal.png", use_column_width=True)
st.sidebar.markdown("""
                    #  Welcome to the Techionista Academy Chatbot!
                    ## Feel free to ask any questions you have about Techionista Academy.
                    ⚠️**Important Note**⚠️ \\
                    Please use the chatbot responsibly and avoid unnecessary prompts. Keep in mind that every interaction with the chatbot consumes resources and incurs costs. 
                    OpenAI's API pricing is based on usage, so multiple prompts can quickly add up. To make the most of the service, ensure that your prompts are relevant and purposeful. 
                    Thank you for understanding!
                    """)

# Question form button
if st.sidebar.button("Reach the Techionista Team"):
    # Replace with the actual link to your company question form
    url = "http://bit.ly/techionistaquestionform"
    webbrowser.open_new_tab(url)

def construct_index(directory_path):
    max_input_size = 4096
    num_outputs = 1024
    max_chunk_overlap = 20
    chunk_size_limit = 600

    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=1, model_name="gpt-4", max_tokens=num_outputs))
    documents = SimpleDirectoryReader(directory_path).load_data()
    index = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    index.save_to_disk('index.json')

    return index

def load_index_from_disk():
    if os.path.exists('index.json'):
        return GPTSimpleVectorIndex.load_from_disk('index.json')
    else:
        return None

def chatbot(input_text, index):
    if index is None:
        # If the index doesn't exist, create and fine-tune it
        index = construct_index("docs")
    response = index.query(input_text, response_mode="compact")
    return response.response
    
def main():
    index = load_index_from_disk()  # Load the GPT model index from disk

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Use your fine-tuned chatbot model to generate a response
        response = chatbot(prompt, index)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    import threading

    # Start the Discord bot in a separate thread
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()

    # Run the Streamlit app
    main()


