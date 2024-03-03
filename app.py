from flask import Flask, render_template, request
import json
from openai import OpenAI  # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os  # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for searchik
import re

app = Flask(__name__)
# app.config['DEBUG'] = True
chat_history = {}
disliked_courses = []
course_texts = []

chatbox_history = {}
# major_requirements = json.load(open("major_requirements.json"))
major_texts = []


# TODO Move all OPENAI calls to a different file
# def strings_ranked_by_relatedness(
#     query: str,
#     df: pd.DataFrame,
#     relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
#     top_n: int = 25,
# ) -> tuple[list[str], list[float]]:
#     """Returns a list of strings and relatednesses, sorted from most related to least."""
#     query_embedding_response = client.embeddings.create(
#         model=EMBEDDING_MODEL,
#         input=query,
#     )
#     query_embedding = query_embedding_response.data[0].embedding
#     strings_and_relatednesses = [
#         (row["text"], relatedness_fn(query_embedding, row["embedding"]))
#         for i, row in df.iterrows()
#     ]
#     strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
#     strings, relatednesses = zip(*strings_and_relatednesses)
#     return strings[:top_n], relatednesses[:top_n]


# with open("chat_intro.md", "r") as f:
#     chat_intro = f.read()

# with open("recommend_intro.md", "r") as f:
#     recommend_intro = f.read()

# GPT_MODEL = "gpt-3.5-turbo"


# def num_tokens(text: str, model: str = GPT_MODEL) -> int:
#     """Return the number of tokens in a string."""
#     encoding = tiktoken.encoding_for_model(model)
#     return len(encoding.encode(text))


# def query_message(
#     query: str, df: pd.DataFrame, model: str, token_budget: int, chat=False
# ) -> str:
#     """Return a message for GPT, with relevant source texts pulled from a dataframe."""
#     strings, _ = strings_ranked_by_relatedness(query, df)
#     question = f"\n\nQuestion: {query}"
#     if chat:  # If chatting, not recommnending
#         message = """Use the following course and major requirement information to identify yourself, and provide context for your date. \n\n"""
#     else:
#         message = """Use the following course and major requirement information to recommend courses relevant to the student. \n\n"""
#     for string in strings:
#         if num_tokens(message + string + question, model=model) > token_budget:
#             break
#         else:
#             message += string
#     return message + question


@app.route("/get_chatbox_history/<course_code>")
def get_chatbox_history(course_code):
    global chatbox_history
    to_return = []
    for i in range(len(chatbox_history)[course_code]):
        if i % 2 == 0:
            to_return.append(f"You: {chatbox_history[course_code][i]}")
        else:
            to_return.append(f"{course_code}: {chatbox_history[course_code][i]}")

    return json.dumps(to_return)


# def chat(

#     course_title,
#     message,
#     model=GPT_MODEL,
#     conversation_histories=chat_history,
#     data=data,
#     chat_intro=chat_intro,
# ):
#     if course_title in conversation_histories:
#         conversation_history = conversation_histories[course_title]
#     else:
#         conversation_history = []

#     chat_intro = (
#         f"{course_title}. You are personifying {course_title} on Tinder."
#         + "\n\n"
#         + chat_intro
#     )

#     messages = [
#         {"role": "system", "content": chat_intro},
#         *conversation_history,  # Unpack the conversation history
#         {"role": "user", "content": message},  # Add the current user message
#     ]
#     conversation_history[course_title][1].append(message)
#     chatbox_history[course_title].append(message)

#     message = query_message(message, df=data, model=model, token_budget=8192, chat=True)

#     response = client.chat.completions.create(
#         model=GPT_MODEL, messages=messages, temperature=0
#     )

#     response_message = response.choices[0].message.content
#     chatbox_history[course_title].append(response_message)

#     # Append the user message and the GPT (assistant) response to the history
#     conversation_history.append({"role": "user", "content": message})
#     conversation_history.append({"role": "assistant", "content": response_message})

#     conversation_histories[course_title] = conversation_history
#     return response_message


# def recommend(message):
#     message = query_message(
#         message, df=data, model=GPT_MODEL, token_budget=8192, chat=False
#     )
#     messages = [
#         {"role": "system", "content": recommend_intro},
#         {"role": "user", "content": message},
#     ]
#     response = client.chat.completions.create(
#         model=GPT_MODEL, messages=messages, temperature=0
#     )
#     response_message = response.choices[0].message.content
#     return response_message


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_majors_and_certs")
def get_majors():
    major_requirements = json.load(open("major_requirements.json"))
    print(list(major_requirements.keys()))
    print("her")
    return json.dumps(list(major_requirements.keys()))


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    course_code, message = data.get("course_code"), data.get("message")
    response = chat(course_code, message)
    return response


@app.route("/get_recommendations/<majors>")
def get_recommendations(majors):
    global disliked_courses
    global chat_history
    majors = majors.split(":")[1:]
    liked_courses = list(chat_history.keys())
    taken_courses = []
    prompt = f"I am a student majoring in {majors}. I am interested in the following courses: {', '.join(liked_courses)}. I like the following courses: {', '.join(taken_courses)}. I dislike the following courses: {', '.join(disliked_courses)}"
    prompt = prompt.lower()
    response = recommend(prompt)
    potential_courses = response.split(", ")
    potential_courses = [course.upper() for course in potential_courses]
    return json.dumps(potential_courses)


@app.route("/save_dislike/<course_code>")
def save_dislike(course_code):
    global disliked_courses
    disliked_courses.append(course_code)
    return ""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
