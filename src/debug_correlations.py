
import sys
import json
import numpy as np
import pandas as pd
from misc.file_util import load_configs, load_expressions, save_languages, load_space
from modals.modal_language import ModalExpression, ModalLanguage, sav
from modals.modal_language_of_thought import ModalLOT
from modals.modal_meaning import ModalMeaningSpace
from modals.modal_measures import language_complexity
from altk.effcomm.analysis import pearson_analysis

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/debug_correlations.py path_to_config_file")
        raise TypeError(f"Expected {2} arguments but received {len(sys.argv)}.")

    # Load expressions and save path
    config_fn = sys.argv[1]
    configs = load_configs(config_fn)
    expression_save_fn = configs["file_paths"]["expressions"]
    space_fn = configs["file_paths"]["meaning_space"]


    new_langs_fn = "old.yml"

    # load old languages
    old_langs_json = None
    with open("/Users/nathanielimel/clms/projects/modals-effcomm/all.json", 'r') as f:
        old_langs_json = json.load(f)

    # load old lexicon (arrays)
    with open("/Users/nathanielimel/clms/projects/modals-effcomm/lexicon.json", "r") as f:
        old_lexicon = json.load(f)

    space = load_space(space_fn)
    comp_measure = lambda lang: language_complexity(
        language=lang,
        mlot=ModalLOT(space, configs["language_of_thought"])
    )

    # Keep track of the disagreements. Must be JSON readable.
    discrepancies = dict()

    # Construct a map for array_strings to arrays
    string_to_arr = dict()

    for name, lang_struct in old_langs_json.items():
        lang = []
        meanings_dict = lang_struct["meanings"] 
        # keys= number strings as dummy names
        # values=string rep of arrays.
        # for arr_str in meanings_dict.values():
        for meaning_name in meanings_dict:
            meaning_dict = meanings_dict[meaning_name]
            arr_str,  = meaning_dict.keys()

            entry = old_lexicon[arr_str]
            arr = np.array(entry["arr"])
            lang.append(arr_str)

            # update the string_to_arr map
            if arr_str not in string_to_arr:
                string_to_arr[arr_str] = None
            string_to_arr[arr_str] = arr
    

    # Create a map for array_strings to expressions
    expressions = load_expressions(expression_save_fn)
    string_to_expression = dict()
    for arr_str in string_to_arr:
        arr1 = string_to_arr[arr_str]
        # search for the new expression matching the old array
        for e in expressions:
            arr2 = e.meaning.to_array()
            if np.array_equal(arr1, arr2):
                string_to_expression[arr_str] = e
                break
        if arr_str not in string_to_expression:
            raise ValueError(f"Error: the array was not found in the list of expressions. Received {arr1}")

    # Construct the old languages as altk ModalLanguages
    new_langs = []
    # for language_name, language in old_langs_json.items():
    for language_name, lang_struct in old_langs_json.items():

        meanings_dict = lang_struct["meanings"] 
        # construct new expressions        
        new_expressions = []        
        for meaning_name in meanings_dict:
            meaning_dict = meanings_dict[meaning_name]
            arr_str,  = meaning_dict.keys()    

            new_expression = string_to_expression[arr_str]
            new_expressions.append(new_expression)

        lang = ModalLanguage(new_expressions, name=language_name)

        # check complexity hasn't changed
        total_complexity = comp_measure(lang)
        if total_complexity != lang_struct["complexity"]:
            # raise ValueError(f"Old and new complexity of language are not equal. Old= {total_complexity}, New={lang_struct['complexity']},\n old_language={meanings_dict},\n new_language= {lang}")
            key = f"discrepancy_{len(discrepancies)}"
            discrepancies[key] = {
                    "old":lang_struct,
                    "new":lang.yaml_rep(),
                }
            # print("Old and new complexity of language disagree.")

        lang.data["complexity"] = total_complexity

        # check nauze / SAV hasn't changed
        degree_sav = lang.degree_property(sav)
        degree_nauze = lang_struct["nauze"]
        if degree_sav != degree_nauze:
            # raise ValueError(f"Old and new naturalness are not equal. Old= {degree_nauze}, New={degree_sav}")
            print("Old and new naturalness disagree.")
            key = f"discrepancy_{len(discrepancies)}"
            discrepancies[key] = {
                    "old":lang_struct,
                    "new":lang.yaml_rep(),
                }
        
        lang.data["sav"] = degree_sav

        new_langs.append(lang)

    # get dataframes
    old_df = pd.DataFrame(data={
        "name": [name for name in old_langs_json],
        "nauze": [language["nauze"] for language in old_langs_json.values()],
        "complexity": [language["complexity"] for language in old_langs_json.values()],
    })

    new_df = pd.DataFrame(data={
        "name": [lang.data["name"] for lang in new_langs],
        "sav": [lang.data["sav"] for lang in new_langs],
        "complexity": [lang.data["complexity"] for lang in new_langs],
    })

    # check the length is correct
    assert len(old_df) == len(new_df)
    assert len(new_langs) == len(old_langs_json)

    print("total discrepancies: ", len(discrepancies))
    print("total old languages: ", len(old_langs_json))
    # save discrepancies
    with open("discrepancies.json", "w") as f:
        json.dump(discrepancies, f, indent=2)

    # save languages
    save_languages(new_langs_fn, new_langs, id_start=None, kind="old")
    old_df.to_csv("old_langs_df.csv")
    new_df.to_csv("new_langs_df.csv")

    # Measure new langs and new correlations
    # compare with old langs and their correlations
    result = pearson_analysis(
        data=old_df,
        predictor="complexity",
        property="nauze",
    )
    old_pearson = result["rho"]
    result = pearson_analysis(
        data=new_df,
        predictor="complexity",
        property="sav"
    )
    new_pearson = result["rho"]

    pearson_df = pd.DataFrame(
        data={
            "sample": ["new", "old"],
            "pearson": [old_pearson, new_pearson],
        }
    )
    pearson_df.to_csv("pearsons.csv")

if __name__ == "__main__":
    main()
    
