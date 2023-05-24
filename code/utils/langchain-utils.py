
import sys

learning_langchain_path = '/home/kruall/learn-langchain'

if learning_langchain_path not in sys.path:
    sys.path.insert(1, learning_langchain_path)


from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter

def make_docs(text):
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(text)
    docs = [Document(page_content=t) for t in texts]
    return docs


def read_lines(file, line_count):
    lines = []
    for idx, line in enumerate(file):
        if idx < line_count:
            lines.append(line)
        else:
            break
    return lines


def split_to_chunks(lines, chunk_size):
    chunks = [[]]
    chunk_idx = 0
    for idx, line in enumerate(lines):
        if idx and idx % chunk_size == 0:
            chunk_idx += 1
            chunks.append([])
        chunks[-1].append(line)
    return chunks


def run_repeated_summarization(chain, lines, chunk_size):
    result = [lines]
    while len(lines) > 1:
        summaries = []
        chunks = split_to_chunks(lines, chunk_size)
        for chunk in chunks:
            text = '\n'.join(chunk)
            docs = make_docs(text)
            output = chain.run(docs)
            summaries.append(output)
        result.append(summaries)
        lines = summaries
    return result












