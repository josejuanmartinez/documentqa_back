import random
import re

from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain


class AnswerGenerator:
    def __init__(self):
        template = "Act as a Summarizer. I will provide you with one Question and some "\
                   "Context. You will summarize the Context into one sentence in such a way that answers " \
                   "to the Question. Remove all the constructions and expressions you find in Context which don't add "\
                   "any relevant data, as conversational expressions or constructions." \
                   "\n"\
                   "{qa}"

        self.prompt = PromptTemplate(template=template, input_variables=["qa"])
        self.llm = OpenAI()

    def generate(self, query: str, context: []) -> str:
        """
        Generates a response using a series of relevant answers from the vector store from previous steps (retrieve)
        Args:\n\n
            query: the query/question formulated by the user
            context: an array of relevant results retrieved before with `retrieve`

        Returns:\n\n
            A string with the answer
        """
        context = "\n- ".join(context)
        qa = f"The Question is the following: {query}.\nThe Context is the following:{context}."
        llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)
        contexted_answer = llm_chain.run(qa)
        contexted_answer = contexted_answer.replace('\n', '').replace('\t', '')
        contexted_answer = re.sub(r' +', ' ', contexted_answer)
        return contexted_answer.strip()

    def generate_mock(self, query: str, context: []) -> str:
        """
        Generates a response using a series of relevant answers from the vector store from previous steps (retrieve)
        Args:\n\n
            query: the query/question formulated by the user
            context: an array of relevant results retrieved before with `retrieve`

        Returns:\n\n
            A string with the answer
        """
        return "A language model is a type of artificial intelligence model trained to generate text that is similar to human language, such as OpenAI's Generative Pre-Trained Transformer (GPT), Google's BERT, and Microsoft's XLNet, which have the ability to generate human-like text for natural language processing tasks, but can also be used to impersonate or deceive others, posing a potential risk to user privacy."
