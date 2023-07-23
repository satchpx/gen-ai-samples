import os
from re import template
from tabnanny import verbose
from apikey import apikey

import streamlit as sl
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper

os.environ['OPENAI_API_KEY'] = apikey

sl.title('🦜️🔗 My Blog GPT')
prompt = sl.text_input('This tool takes a topic for a blog and outputs the Title and Body. Enter your topic here')

title_template = PromptTemplate(
    input_variables = ['topic'],
    template = 'write me a blog title about {topic}'
)

body_template = PromptTemplate(
    input_variables = ['title', 'wikipedia_research'],
    template = 'write a blog content based on title: {title} by also using Wikipedia as a research source: {wikipedia_research}'
)

# Memory
title_memory = ConversationBufferMemory(input_key='topic' , memory_key='chat_history')
body_memory = ConversationBufferMemory(input_key='title' , memory_key='chat_history')

# Create an instance of OpenAI/ LLM
llm = OpenAI(temperature=0.9)
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
body_chain = LLMChain(llm=llm, prompt=body_template, verbose=True, output_key='body', memory=body_memory)

#sequential_chain = SimpleSequentialChain(chains=[title_chain, body_chain], verbose=True)
#sequential_chain = SequentialChain(chains=[title_chain, body_chain], input_variables=['topic'], output_variables=['title', 'body'], verbose=True)

wiki = WikipediaAPIWrapper()

# Invoke the LLM if there is a prompt
if prompt:
    #response = llm(prompt)
    #response = title_chain.run(topic=prompt)
    #response = sequential_chain.run(prompt)
    #response = sequential_chain({'topic':prompt})

    title = title_chain.run(prompt)
    wiki_research = wiki.run(prompt)
    body = body_chain.run(title=title, wikipedia_research=wiki_research)

    sl.write(title)
    sl.write(body)

    with sl.expander('Title History'): 
        sl.info(title_memory.buffer)
    
    with sl.expander('Body History'): 
        sl.info(body_memory.buffer)

    with sl.expander('Wikipedia Research History'): 
        sl.info(wiki_research)