from openai import OpenAI
from pathlib import Path
import json
import os

client = OpenAI()
string="/Users/lingalarahul/Documents/Nivi/"
folder = Path(string)
files = [str(p) for p in folder.rglob("*.py") if p.is_file()]

count = 0
LIMIT = 10

for path in files:
    old_path=path
    split_path=path.split("/")
    old_name = split_path[-1]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": f'Convert this to snake_case: "{old_name}" while retaining .py as it is python script. json format should have only one key and the key name is "new_name" while value is the new name for the python file'
            }
        ],
    )
    raw_json = completion.choices[0].message.content
    new_name = json.loads(raw_json)['new_name']
    new_path = str(Path(path).with_name(new_name))
    os.rename(old_path, new_path)
    count+=1
    if count == LIMIT:
        break
