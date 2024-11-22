import streamlit as st
import warnings
warnings.filterwarnings(action='ignore')
import datetime
import random
import string
from time import sleep
import tiktoken
import json
# main: server is listening on http://127.0.0.1:8001/v1 - starting the main loop
from openai import OpenAI

# for counting the tokens in the prompt and in the result
encoding = tiktoken.get_encoding("cl100k_base") 
# GLOBALS
nCTX = 8192
sTOPS = ['<|endoftext|>']
modelname = "NuExtract1.5-smol"
modelfile = 'NuExtract-1.5-smol-Q5_K_L.gguf'
# Set the webpage title
st.set_page_config(
    page_title=f"Your LocalGPT ✨ with {modelname}",
    page_icon="🌟",
    layout="wide")
# SET Session States
if "hf_model" not in st.session_state:
    st.session_state.hf_model = modelname
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "repeat" not in st.session_state:
    st.session_state.repeat = 1.35
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.1
if "maxlength" not in st.session_state:
    st.session_state.maxlength = 500
if "speed" not in st.session_state:
    st.session_state.speed = 0.0
# Defining internal functions
def writehistory(filename,text):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(text)
        f.write('\n')
    f.close()
def genRANstring(n):
    """
    n = int number of char to randomize
    """
    N = n
    res = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    return res
# CACHED RESOURCES
@st.cache_resource 
def create_chat():   
# Set HF API token  and HF repo
    client = OpenAI(base_url="http://localhost:8001/v1", api_key="not-needed", organization=modelname)
    print(f'loading {modelfile} with pure Llama.cpp-server...')
    return client


# create the log file
if "logfilename" not in st.session_state:
    logfile = f'{genRANstring(5)}_log.txt'
    st.session_state.logfilename = logfile
    #Write in the history the first 2 sessions
    writehistory(st.session_state.logfilename,f'{str(datetime.datetime.now())}\n\nYour own LocalGPT with 🌀 {modelname}\n---\n🧠🫡: You are a helpful assistant.')    
    writehistory(st.session_state.logfilename,f'🌀: How may I help you today?')

# INSTANTIATE THE API CLIENT to the LLM
llm = create_chat()

### START STREAMLIT UI
# Create a header element
mytitle = f'## Extract data with {modelname} into `JSON` format'
st.markdown(mytitle, unsafe_allow_html=True)
# CREATE THE SIDEBAR
with st.sidebar:
    st.session_state.temperature = st.slider('Temperature:', min_value=0.0, max_value=1.0, value=0.1, step=0.01)
    st.session_state.maxlength = st.slider('Length reply:', min_value=150, max_value=2000, 
                                           value=500, step=50)
    st.session_state.presence = st.slider('Presence Penalty:', min_value=0.0, max_value=2.0, value=1.11, step=0.02)
    st.markdown(f"**Logfile**: {st.session_state.logfilename}")
    statspeed = st.markdown(f'💫 speed: {st.session_state.speed}  t/s')
    btnClear = st.button("Clear History",type="primary", use_container_width=True)
# MAIN WINDOWN
st.session_state.jsonformat = st.text_area('JSON Schema to be applied', value="", height=150,  
                     placeholder='here your schema', disabled=False, label_visibility="visible")
st.session_state.origintext = st.text_area('Source Document', value="", height=150,  
                     placeholder='here your text', disabled=False, label_visibility="visible")
extract_btn = st.button("Extract Data",type="primary", use_container_width=False)
st.markdown('---')
st.session_state.extractedJSON = st.empty()
st.session_state.onlyJSON = st.empty()

# ACTIONS
if extract_btn:
        prompt = f"""<|input|>\n### Template:
{st.session_state.jsonformat}

### Text:
{st.session_state.origintext}
<|output|>
"""
        print(prompt)
        with st.spinner("Thinking..."):
            start =  datetime.datetime.now()
            # https://platform.openai.com/docs/api-reference/completions/create
            output = llm.completions.create(
                            prompt =prompt,
                            model=modelname,
                            temperature=st.session_state.temperature,
                            presence_penalty=st.session_state.presence,
                            stop=sTOPS,
                            max_tokens=st.session_state.maxlength,              
                            stream=False)

        delta = datetime.datetime.now() -start
        print(output.content)
        result = output.content
        st.write(result)
        adapter = result.replace("'",'"')
        final = json.loads(adapter) 
        totalTokens = len(encoding.encode(prompt))+len(encoding.encode(result))
        totalseconds = delta.total_seconds()
        st.session_state.speed = totalTokens/totalseconds
        statspeed.markdown(f'💫 speed: {st.session_state.speed:.2f}  t/s')
        totalstring = f"""GENERATED STRING

{result}
---

Generated in {delta}

---

JSON FORMAT:
"""   
        #WRITE THE OUTPUT AND THE LOGS
        st.session_state.onlyJSON.json(final)    
        writehistory(st.session_state.logfilename,f'✨: {prompt}')
        writehistory(st.session_state.logfilename,f'🌀: {result}')
        writehistory(st.session_state.logfilename,f'---\n\n')
