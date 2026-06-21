from langchain.text_splitter import RecursiveCharacterTextSplitter

class Chunker:

    @staticmethod
    def split(text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        return splitter.split_text(text)