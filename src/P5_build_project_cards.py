from dspipe import Pipe
import pandas as pd
import yaml

df = pd.read_csv("data/cleaned_OMB_inventory.csv")
f_schema = "data/archive_reports/data_dictionary.yaml"

with open(f_schema) as stream:
    schema = yaml.safe_load(stream)
    schema = schema["fields"]
    schema = pd.DataFrame(schema).set_index("name")


def compute(f0, f1):
    row = df.loc[f0]

    output = []
    output.append(f"## {f0}")
    output.append("\n")

    for k, v in row.items():
        # k = ' '.join(k.split('_')[1:]).title()
        name = schema.loc[k]["description"]
        name = name.strip().strip(".") + ":"

        output.append(f"+ **{name}**: {v}")

        # Do something special if there is an ENUM
        pass

    output = "\n".join(output)
    with open(f1, "w") as FOUT:
        FOUT.write(output)


key = "1_use_case_id"
df = df.set_index(key).fillna("")
Pipe(df.index, "data/project_cards/individual", output_suffix=".md")(compute, -1)
# exit()
