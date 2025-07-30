from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def create_text_summarizer():
    """
    Create a chain for summarizing text and tables.
    
    Returns:
        Summarization chain for text content
    """
    prompt_text = """
You are an assistant tasked with summarizing tables and text.
Give a concise summary of the table or text.

Respond only with the summary, no additionnal comment.
Do not start your message by saying "Here is a summary" or anything like that.
Just give the summary as it is.

Table or text chunk: {element}

"""
    prompt = ChatPromptTemplate.from_template(prompt_text)
    model = ChatGroq(temperature=0.5, model="llama-3.1-8b-instant")
    summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()
    return summarize_chain


def create_image_summarizer():
    """
    Create a chain for summarizing images using GPT-4o-mini.
    
    Returns:
        Summarization chain for images
    """
    prompt_template = """Describe the image in detail. For context,
                      the image is part of a research paper explaining the transformers
                      architecture. Be specific about graphs, such as bar plots."""
    
    messages = [
        (
            "user",
            [
                {"type": "text", "text": prompt_template},
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{image}"},
                },
            ],
        )
    ]
    
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
    return chain


def summarize_texts_and_tables(texts, tables):
    """
    Summarize texts and tables using the text summarizer.
    
    Args:
        texts (list): List of text elements
        tables (list): List of table elements
        
    Returns:
        tuple: (text_summaries, table_summaries)
    """
    summarize_chain = create_text_summarizer()
    
    # Process sequentially to avoid rate limits
    text_summaries = []
    for text in texts:
        summary = summarize_chain.invoke(text)
        text_summaries.append(summary)
    
    table_summaries = []
    tables_html = [table.metadata.text_as_html for table in tables]
    for table_html in tables_html:
        summary = summarize_chain.invoke(table_html)
        table_summaries.append(summary)
    
    return text_summaries, table_summaries


def summarize_images(images):
    """
    Summarize images using the image summarizer.
    
    Args:
        images (list): List of base64 encoded images
        
    Returns:
        list: List of image summaries
    """
    chain = create_image_summarizer()
    image_summaries = chain.batch(images)
    return image_summaries

