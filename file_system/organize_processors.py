# organize_processors.py
from pathlib import Path 
from openai import OpenAI
from concurrent.futures import ProcessPoolExecutor,as_completed
import json
import os

# python3 organize_processors.py  5.78s user 0.99s system 103% cpu 6.530 total

def convert_files(old_path):
    old_name=old_path.split("/")
    old_name=old_name[-1]
    client=OpenAI()
    completion=client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": f'Convert this to snake_case: "{old_name}" while retaining .py as it is python script. json format should have only one key and the key name is "new_name" while value is the new name for the python file'
            }
        ],
    )
    raw_json=completion.choices[0].message.content
    return raw_json,old_name,old_path


def main():
    folder="/Users/lingalarahul/Documents/Nivi/"
    folder=Path(folder)
    files = [str(p) for p in folder.rglob("*.py") if p.is_file()]

    LIMIT=10
    PROCESSOR_COUNT=4

    old_path=files[:LIMIT]

    with ProcessPoolExecutor(max_workers=PROCESSOR_COUNT) as executor:
        futures=[executor.submit(convert_files,p) for p in old_path]
        for fut in as_completed(futures):
            raw_json,old_name,old_path=fut.result()
            new_name=json.loads(raw_json)['new_name']
            new_path=Path(old_path).with_name(new_name)
            os.rename(old_path,str(new_path))

if __name__ == "__main__":
    main()