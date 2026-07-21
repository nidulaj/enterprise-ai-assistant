RAG_QA_PROMPT = """Use ONLY the context below to answer the question.

If the answer is not present in the context, say:
"I could not find that information in the uploaded documents."

Context:
{context}

Question:
{question}
"""
