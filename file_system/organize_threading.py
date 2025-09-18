# Use ThreadPoolExecutor with max workers of 3
# python3 organize.py  1.27s user 0.41s system 11% cpu 15.227 total
# organize_threading.py  1.49s user 0.36s system 24% cpu 7.459 total - threadcount=3
# organize_threading.py  1.69s user 0.57s system 51% cpu 4.400 total - threadcount=10


from pathlib import Path
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os

def convert_filenames(old_path):
    old_name=old_path.split("/")
    old_name=old_name[-1]
    client = OpenAI()  # Create client inside function
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
    return raw_json,old_name,old_path

folder="/Users/lingalarahul/Documents/Nivi/"
folder=Path(folder)
files = [str(p) for p in folder.rglob("*.py") if p.is_file()]

LIMIT = 10
old_path=files[:LIMIT]

THREAD_COUNT=10

with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
    futures = [executor.submit(convert_filenames, k) for k in old_path]
    for fut in as_completed(futures):
        raw_json,old_name,old_path=fut.result()
        new_name=json.loads(raw_json)['new_name']
        print(f"{new_name}->{old_name}")
        new_path=Path(old_path).with_name(new_name)
        os.rename(old_path, str(new_path))
    



