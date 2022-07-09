import sys
import yaml
from misc.file_util import load_configs, load_languages

def main():
    # load up literal and pragmatic languages
    
    literal_fn = "/Users/nathanielimel/clms/projects/modals-effcomm/outputs/half_credit_literal/languages/artificial.yml"
    pragmatic_fn = "/Users/nathanielimel/clms/projects/modals-effcomm/outputs/half_credit_pragmatic/languages/artificial.yml"

    # dev fn to quickly make sure things run alright
    # literal_fn = "/Users/nathanielimel/clms/projects/modals-effcomm/outputs/dev/languages/artificial.yml"
    # pragmatic_fn = literal_fn

    result = load_languages(literal_fn)
    literal_languages = result["languages"]

    result = load_languages(pragmatic_fn)
    pragmatic_languages = result["languages"]


    # collect languages in a dictionary
    comparison = dict()
    discrepancies = dict()

    # get a str of their hash
    get_key = lambda lang: str(hash(lang))

    for lang in literal_languages:
        key = get_key(lang)
        if key not in comparison:
            comparison[key] = {"literal": None, "pragmatic": None}
        
        comparison[key]["literal"] = lang

    for lang in pragmatic_languages:
        key = get_key(lang)
        if key not in comparison:
            comparison[key] = {"literal": None, "pragmatic": None}
    
        comparison[key]["pragmatic"] = lang


    # Compare matching languages
    matches = 0
    for key in comparison:
        langs_dict = comparison[key]
        if None not in list(langs_dict.values()):
            matches += 1

            literal_lang = langs_dict["literal"]
            pragmatic_lang = langs_dict["pragmatic"]

            literal_complexity = lang.data["complexity"]
            pragmatic_complexity = lang.data["complexity"]

            if literal_complexity != pragmatic_complexity:
                discrepancies[key] = {
                    "literal": literal_lang,
                    "pragmatic": pragmatic_lang,
                }

    # save results
    print(f"found {matches} matching literal and pragmatic languages.")
    print(f"found {len(discrepancies)} discrepancies in complexity.")

    with open("comparison.yml", "w") as outfile:
        yaml.safe_dump(discrepancies, outfile)
    

if __name__ == "__main__":
    main()