#!/usr/bin/env python
import os, time, requests

ANONADDY_URL = os.getenv("ANONADDY_URL", "")
ANONADDY_API_KEY = os.getenv("ANONADDY_API_KEY", "")
KEYWORD = os.getenv("KEYWORD", "Sieve")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "anonaddy.sieve")
SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL", "300"))

def get_aliases(url, api_key):
    aliases = {}
    page = 1
    while True:
        response = requests.get(
            f"{url}/api/v1/aliases?page[number]={page}&page[size]=100",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        data = response.json()
        
        for alias in data.get("data", []):
            aliases[alias["local_part"]] = alias.get("description", "")
        
        if data.get("meta", {}).get("last_page") == page:
            break
        page += 1
    return aliases

def parse_descriptions(aliases, keyword=KEYWORD):
    keyword += ":"
    for alias, description in list(aliases.items()):
        if keyword not in description:
            del aliases[alias]
        else:
            pos = description.index(keyword) + len(keyword)
            value = description[pos:].strip()
            if value.startswith('"'):
                end_quote = value.find('"', 1)
                if end_quote != -1:
                    value = value[1:end_quote]
            else:
                value = value.split()[0]
            if value == "":
                del aliases[alias]
            else:
                aliases[alias] = value
    return aliases

def get_folder_structure(aliases):
    folder_structure = {}
    for alias, path in list(aliases.items()):
        parts = path.split(".")
        current_level = folder_structure
        for part in parts:
            if part not in current_level:
                current_level[part] = {"aliases": []}
            current_level = current_level[part]
        current_level["aliases"].append(alias)
    return folder_structure

def generate_sieve_folder_structure(prefix, folder_structure):
    script_lines = []
    if "aliases" in folder_structure and len(folder_structure["aliases"]) > 0:
        aliases = [alias + "+*" for alias in folder_structure["aliases"]]
        aliases = "\"" + "\", \"".join(aliases) + "\""
        script_lines.append(f'}} elsif address :localpart :matches "From" [{aliases}] {{')
        script_lines.append(f'  fileinto :create "{".".join(prefix)}";')
    for subfolder in [folder for folder in sorted(folder_structure.keys()) if folder != "aliases"]:
        script_lines.extend(generate_sieve_folder_structure(prefix + [subfolder], folder_structure[subfolder]))
    return script_lines

def generate_sieve_script(folder_structure, indent=0):
    script_lines = ['require ["mailbox", "subaddress", "fileinto", "variables"];', '']
    for folder in sorted(folder_structure.keys()):
        script_lines.extend(generate_sieve_folder_structure([folder], folder_structure[folder]))
    script_lines.append('}')
    script_lines[2] = script_lines[2].replace('} elsif', 'if')
    return "\n".join(script_lines)

if __name__ == "__main__":
    with open(OUTPUT_FILE, "r") as f:
        cached_sieve_script = f.read()
    while True:
        aliases = get_aliases(ANONADDY_URL, ANONADDY_API_KEY)
        aliases = parse_descriptions(aliases)
        folder_structure = get_folder_structure(aliases)
        sieve_script = generate_sieve_script(folder_structure)
        if sieve_script != cached_sieve_script:
            with open(OUTPUT_FILE, "w") as f:
                f.write(sieve_script)
            cached_sieve_script = sieve_script
            print(f"Sieve script updated and written to {OUTPUT_FILE}")
        time.sleep(SLEEP_INTERVAL)