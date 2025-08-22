API_KEY= "AIzaSyCFu6BynbPsa-kOupAlLZc21uTXCmaqjik"

import json
import google.generativeai as genai
import os

genai.configure(api_key=API_KEY)

# model = genai.GenerativeModel("gemini-1.5-flash")

# response = genai.send_instructions({
#     "instruction": "gives details about songs like name release dates url to play that song , genre etc when song name is given",
#     "model": model  # Replace with the actual model or system setting
# })


model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction="gives details about songs like name release dates url to play that song , genre etc when song name is given in json format ")

response = model.generate_content("Waka Waka")



print(response.text)