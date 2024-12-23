from dspipe import Pipe
import pandas as pd
import yaml

df = pd.read_csv("data/cleaned_OMB_inventory.csv")

def compute(name, f1, key):
    output = []
    output.append(f"# {name}")

    dx = df[df[key] == name]

    output.append(f"| Use Case ID | Title |")
    output.append(f"|:----------- |:----- |")
    
    for _, row in dx.iterrows():
        name = ' '.join(row['2_use_case_name'].split())
        useID = row['1_use_case_id']
        link = f'../individual/{useID}.md'
        output.append(f"| [{useID}](<{link}>) | {name} |")
        
    output = "\n".join(output)
    with open(f1, "w") as FOUT:
        FOUT.write(output)

key = '3_agency'
P = Pipe(df[key].unique(), f'data/project_cards/{key}', output_suffix='.md', prefilter=False)
P(compute, 1, key=key)

########################################################################

f_schema = "data/archive_reports/data_dictionary.yaml"

with open(f_schema) as stream:
    schema = yaml.safe_load(stream)
    schema = schema["fields"]
    schema = pd.DataFrame(schema).set_index("name")

def compute(use_case_ID, f1):
    row = df.loc[use_case_ID]

    output = []
    title = row['2_use_case_name']
    agency = row['3_agency']
    agency_abbr = row['3_abr']
    subagency = row['4_bureau']

    f_agency = f'../3_agency/{agency}.md'
    
    output.append(f"# {title}")
    output.append(f"## {use_case_ID}")
    output.append(f"_[{agency}](<{f_agency}>)_ ({agency_abbr}) / {subagency}")
    skip_rows = ['2_use_case_name', '3_abr', '3_agency', '4_bureau']
    
    output.append("\n")
    

    for k, v in row.items():
        # k = ' '.join(k.split('_')[1:]).title()

        requirements = schema.loc[k]['constraints']

        if not v:
            continue
            if isinstance(requirements, dict) and 'required' not in requirements:
                continue
                #if not requirements['required']:
                #   continue

        if k == "47_timely_resources":
            name = "Has the communication been timely"
        elif k in skip_rows:
            continue
        else:
            name = schema.loc[k]["description"]
            name = name.strip().strip(".")
        output.append(f"+ **{name}**: {v}")

        # Do something special if there is an ENUM
        pass

    output = "\n".join(output)
    with open(f1, "w") as FOUT:
        FOUT.write(output)


key = "1_use_case_id"
df = df.set_index(key).fillna("")
Pipe(df.index, "data/project_cards/individual", output_suffix=".md", prefilter=False)(compute, 1)
# exit()
