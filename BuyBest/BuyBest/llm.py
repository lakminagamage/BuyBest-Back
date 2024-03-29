from scrape import findAllUrls, get_body_content

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import pickle
import os
from langchain.chat_models import ChatOpenAI

load_dotenv()
url = 'https://www.laptop.lk/index.php/product-category/laptops-desktops/'

url_arr = findAllUrls(url)

websitedata = []

def save_web_data():
    for pagedata in url_arr:
        websitedata.append(get_body_content(pagedata).strip())
    print(websitedata)
    return websitedata






def save_website_data_to_pickle(webcontent):
    text_split = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    text_list = []
    for element in webcontent:
        if isinstance(element, bytes):
            text = element.decode('utf-8')
        else:
            text = bytes(element, 'utf-8').decode('utf-8')
        text_list.append(text)
    chunks = text_split.split_text(text=text_list[0])

    #chunks = text_split.split_text(text=webcontent[0].encode("utf-8"))
    embeddings = OpenAIEmbeddings()
    vs = FAISS.from_texts(chunks,embedding=embeddings)
    try:
        with open(f"{url}.pkl", "wb") as f:
            pickle.dump(vs, f)
            print(f"Saved {url} to disk.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def get_recommendations():
    try:
        if os.path.exists(f"{url}.pkl"):
            with open(f"{url}.pkl", "rb") as f:
                vs = pickle.load(f)
                print(f"Loaded {url} from disk.")
        else:
            print("No data found.")

        user_query = input("Enter your query: ")
        docs = vs.similarity_search(query=user_query)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo")
        chain = load_qa_chain(llm=llm, chain_type="stuff")
        with get_openai_callback() as callback:
            response = chain.run(input_documents=docs, question=user_query)
            print(response)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


save_website_data_to_pickle(save_web_data())