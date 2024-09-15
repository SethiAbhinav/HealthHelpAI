# from openai import OpenAI 
# import base64
import ast
import requests
import together


# client = OpenAI(
#     api_key="up_X0eMHEuvQ2adWZHewcmbzZOliKVN2",
#     base_url="https://api.upstage.ai/v1/solar"
# )

# def read_presc(encoded_string):
        
#     response = client.chat.completions.create(
#         model="solar-docvision",
#     messages=[
#         {
#           "role": "user",
#           "content": [
#               {
#                   "type": "image_url",
#                   "image_url": {
#                       "url": f"data:image/png;base64,{encoded_string}"
#                   },
#               },
#               {
#                   "type": "text",
#                   "text": """Extract the information about the prescribed medicine names in the following format:
#                   Example: 
#                   {'medication_names': ['Medication 1', 'Medication 2'],
#                   'dosage': ['1 Morning, 1 Night', '1 Morning'],
#                   'total_dose_per_day': [2, 1],
#                   'before/after meal':['after meal', 'before meal'],
#                   'duration': ['10 days', '2 months']
#                   }
#                   """
#               },
#           ]
#         }
#     ],
# )
#     return ast.literal_eval(response.choices[0].message.content)
 
api_key = "up_X0eMHEuvQ2adWZHewcmbzZOliKVN2"
# filename = "/Users/livdea/Downloads/sample_presc1.png"
url = "https://api.upstage.ai/v1/document-ai/document-parse"

together_client = together.Together(api_key='63f7c168bb7791313bf41a29c742dbf3ca9d5930ff1bab9ba4f3b9a7aeb25c10')

def read_presc(image):

    headers = {"Authorization": f"Bearer {api_key}"}
    # files = {"document": open(image, "rb")}
    files = {"document": image}

    # files = {"document": image}

    response = requests.post(url, headers=headers, files=files)


    prompt = f"""
    You will be provided a context parsed from a physician's prescription. 
    CONTEXT: {response.json()}
    """ +"""
    TASK: Extract the information about the prescribed medicine names in the following JSON format:
    Example: 
    {'medication_names': ['Medication 1', 'Medication 2'],
    'dosage': ['1 Morning, 1 Night', '1 Morning'],
'dose_time':[['10:00', '21:00'], ['14:00']], # Time of the day when the dose is taken as per dosage; keep 10:00 for morning, 14:00 for afternoon, 21:00 for night
    'total_dose_per_day': [2, 1], # Sum up the dosage
    'before/after meal':['after meal', 'before meal'],
    'duration': ['10 days', '2 months']}
    Provide the output in the exact format as shown in the example. Do not include any additional text, explanations, or code.
    """

    output = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}]
        )

    print(output.choices[0].message.content)
    prescription_dict = ast.literal_eval(output.choices[0].message.content)

    return prescription_dict