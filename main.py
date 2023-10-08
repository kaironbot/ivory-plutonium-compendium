import argparse
import json
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", help="Generated File version")
args, unknown = parser.parse_known_args()

def generate_template_upload(folder: str, version: str) -> None:
    base = json.load(open("{}/template_base.json".format(os.path.dirname(os.path.abspath(__file__))), 'r'))
    base["_meta"]["dateLastModified"] = int(time.time())
    base["_meta"]["sources"][0]["version"] = version
    base_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
    # Add races
    for j in os.listdir(os.path.join(base_folder, "races")):
        race = json.load(open(os.path.join(base_folder, "races", j), 'r'))
        race["source"] = "Tales from Ivory"
        base["race"].append(race)
    if False:
        for j in os.listdir(os.path.join(base_folder, "subraces")):
            subrace = json.load(open(os.path.join(base_folder, "subraces", j), 'r'))
            subrace["source"] = "Tales from Ivory"
            subrace["raceSource"] = "Tales from Ivory"
            base["subrace"].append(subrace)
    # Add subclasses (TODO)
    for j in os.listdir(os.path.join(base_folder, "subclasses")):
        subclass = json.load(open(os.path.join(base_folder, "subclasses", j), 'r'))
        base["subclass"].append(subclass["subclass"])
        base["subclassFeature"] += subclass["features"]
    for j in os.listdir(os.path.join(base_folder, "subclass_features")):
        feature = json.load(open(os.path.join(base_folder, "subclass_features", j), 'r'))
        base["subclassFeature"].append(feature)
    # Add feats
    for j in os.listdir(os.path.join(base_folder, "feats")):
        feat = json.load(open(os.path.join(base_folder, "feats", j), 'r'))
        feat["source"] = "iRdW"
        base["feat"].append(feat)
    if False:
        for j in os.listdir(os.path.join(base_folder, "spells")):
            feat = json.load(open(os.path.join(base_folder, "spells", j), 'r'))
            feat["source"] = "iRdW"
            base["spell"].append(feat)
    json.dump(base, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ivory_compendium.json"), 'w', encoding='utf-8'), ensure_ascii=False)

if __name__ == "__main__":
    generate_template_upload('en', args.version)
