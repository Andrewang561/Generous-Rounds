from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OpenAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = OpenAI_API_KEY)

tags =[
    "Animal Welfare",
    "Social Services - At-Risk Youth",
    "Education",
    "Environment",
    "Social Services - Food Bank (Distributor)",
    "Social Services - Food Bank (Multi-Service Agency)",
    "Social Services - Youth",
    "Social Services - First Nations",
    "Social Services - Women",
    "Veterans",
    "International Aid",
]


def funnel_response(prompt):
    "takes a prompt and funnels the prompt into a tag in the database"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"The user will provide a prompt. summarize the prompt with one or more tag(s) from {tags} or respond with \"N/A\" if it doesn't match with any prompts. Respond with only the tag. For example if the promt is \"I enjoy donating to animals\" the response would be \"Animal Welfare\". For example if the promt could be described using more than on prompt like \"I enjoy donating to animals and helping the environment\" the response would be \"Animal Welfare, Environment\". If the prompt doesn't match any of the tags, respond with \"N/A\"."}, 
            {"role": "user", "content": prompt}
        ] 
    )
    return response.choices[0].message.content

def main():
    prompt = input("Enter a prompt: ")
    vr = funnel_response(prompt)
    
    vr.split(", ") # -> ["Animal Welfare", "Environment"]

    print(vr)

    # send vr back to frontend
    # frontend will filter and display the tags in a list

if __name__ == "__main__":
    main()