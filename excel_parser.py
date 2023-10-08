from openpyxl import load_workbook
import json
import os

DESC_SHEET = "Descrizione"
FEATURE_SHEET = "Feature Generiche"
SPELL_SHEET = "Incatesimi"
SPELL_PLACEHOLDER = "%SPELLS%"

def parse_resource_by_type(wb, type):
    if type == "Sottoclasse":
        return ["subclasses", parse_class(wb)]
    return ["", {}]

def raw_features_to_feature(raw_feature, spells):
    ret = []
    for el in raw_feature:
        if el == SPELL_PLACEHOLDER:
            ret.append({
                "type": "table",
                "colLabels": [
                    "Class Level",
                    "Spell"
                ],
                "colStyles": [
                    "col-4 text-center",
                    "col-8 text-left"
                ],
                "rows": [[lvl,", ".join(['{' + f"@spell {el.lower()}" + '}' for el in s])] for lvl, s in spells.items()
                ]
        })
        elif type(el) == type('str'):
            ret.append(el)
        elif type(el) == dict:
            ret.append({
                "type": "list",
                "items": [
                    {"type": "entries", "name": k, "entries": v} for k, v in el.items()
                ]
            })
        elif type(el) == list:
            ret.append({
                "type": "list",
                "items": el
            })
    return ret

def parse_features(wb):
    ws = wb[FEATURE_SHEET]
    features = dict()
    row = 2
    while ws.cell(row=row, column=1).value is not None:
        name = ws.cell(row=row, column=2).value
        lvl = int(ws.cell(row=row, column=1).value)
        desc = ws.cell(row=row, column=3).value
        desc_key = ws.cell(row=row, column=4).value
        desc_value = ws.cell(row=row, column=5).value
        
        if name not in features:
            features[name] = {"lvl": lvl, "content": []}

        if desc is not None:
            features[name]["content"] = features[name]["content"] + desc.strip().split("\n")

        if desc_key is not None and desc_value is not None:
            if type(features[name]["content"][-1]) == dict:
                features[name]["content"][-1][desc_key.strip()] = desc_value.strip()
            else:
                features[name]["content"].append({desc_key.strip(): desc_value.strip()})
        elif desc_value is not None:
            if type(features[name]["content"][-1]) == list:
                features[name]["content"][-1].append(desc_value.strip())
            else:
                features[name]["content"].append([desc_value.strip()])

        row += 1
    return features

def parse_subclass_spells(wb):
    spells = dict()
    ws = wb[SPELL_SHEET]
    row = 2
    while ws.cell(row=row, column=1).value is not None:
        lvl = ws.cell(row=row, column=1).value
        spell = ws.cell(row=row, column=2).value
        manual = ws.cell(row=row, column=3).value

        if lvl not in spells:
            spells[lvl] = []

        spells[lvl].append(f"{spell.strip().lower()}" if (manual is None or manual.lower() == "phb") else f"{spell.strip().lower()}|{manual.lower()}")

        row += 1
    return spells


def parse_class_meta(wb, features, spells):
    ws = wb[DESC_SHEET]
    dnd_class = ws.cell(row=2, column=2).value
    dnd_subclass = ws.cell(row=3, column=2).value
    ret = {
        "name": dnd_subclass,
        "source": "TfI",
        "className": dnd_class,
        "classSource": "PHB",
        "shortName": ws.cell(row=4, column=2).value,
        "subclassFeatures": [
            f"{k}|{dnd_class}|PHB|{dnd_subclass}|TfI|{v['lvl']}" for k, v in features.items()
        ] 
    }
    if len(spells) > 0:
        ret["subclassSpells"] = [el for _, v in spells.items() for el in v ]
    return ret

def parse_class(wb):
    spells = parse_subclass_spells(wb)
    raw_features = parse_features(wb)
    meta = parse_class_meta(wb, raw_features, spells)
    template = { "subclass": meta, "features": [] }
    
    for f_name, f_values in raw_features.items():
        feature = {
            "name": f_name,
            "source": "TfI",
            "className": meta["className"],
            "classSource": "PHB",
            "subclassShortName": meta["name"],
            "subclassSource": "TfI",
            "level": f_values["lvl"],
            "entries": raw_features_to_feature(f_values["content"], spells)
        }
        template["features"] = template["features"] + [feature]
    return template

language = 'en'
filenames = [f for f in os.listdir(os.path.join('source', language)) if f.endswith("xlsx")]

for file in filenames:
    wb = load_workbook(os.path.join(os.path.dirname(os.path.abspath(__file__)), "source", language, file))
    resource_type = wb[DESC_SHEET].cell(row=1, column=2).value.strip()
    t, resource = parse_resource_by_type(wb, resource_type)
    json.dump(resource, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), language, t, file.replace('xlsx', 'json')), 'w'))