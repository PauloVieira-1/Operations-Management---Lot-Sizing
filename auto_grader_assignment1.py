import subprocess
import sys
import os
from contextlib import contextmanager
import pandas as pd
from pylint import lint
from importlib.metadata import version

HOMEWORK = "RESULTS"
NR_TESTS = 3                

@contextmanager
def suppress_stdout():
    """ Function to suppress output to console."""
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def unit_test(test_module, test_nr):
    """ Unit tester."""
    points = 0
    obj_val = 0
    setups = []
    try:
        if test_nr == 0:        # Given example
            ex1_data = [20, 25, 14, 20, 15, 5.5, 2.5]
            pt_data = [1.0, 2.0, 2.0, 1.5, 1.0, 0.5, 1.0]
            obj_val, setups = test_module.lsp1(2, 50, pt_data, 25, ex1_data)
            corr_setups = [0, 1, 0, 1, 1, 0, 0]
            corr_obj_val = 330
        if test_nr == 1:        # Given example
            ex1_data = [20, 25, 14, 20, 15, 5.5, 2.5]
            obj_val, setups = test_module.lsp2(2, 50, 5, ex1_data)
            corr_setups = [1, 0, 1, 0, 1, 0, 0]
            corr_obj_val = 261
        if test_nr == 2:        # Given example
            ex2_data = [[20, 5], [25, 10], [14, 21], [20, 20],
                        [15, 7.5], [5.5, 11], [2.5, 13]]
            obj_val, setups = test_module.lsp3(2, 50, [25, 25], ex2_data)
            corr_setups = [0, 1, 2, 1, 0, 2, 0]
            corr_obj_val = 461
        if int(obj_val) == corr_obj_val:
            points += 0.5
        if setups == corr_setups:
            points += 0.5
        return points, obj_val, setups, None
    except Exception as test_error:
        return 0, obj_val, setups, str(test_error)

def grade_submissions():
    """ Code to check submitted file with unit tests. """

    print(f"Current pylint version: {version('pylint')}")
    
    def get_glpk_version():
         
        try:
            output = subprocess.run(["glpsol", "--version"], capture_output=True, text=True)
            return output.stdout.strip()
        except FileNotFoundError:
            return "GLPK is not installed or not in PATH."

    print(f"Current GLPK version: {get_glpk_version()}")
    lint.pylinter.MANAGER.astroid_cache = {}
    
    files = []
    for file in os.listdir():
        if file.endswith(".py"):
            if file == 'auto_grader_' + HOMEWORK + '.py':
                continue
            files.append(os.path.splitext(file)[0])

    files.sort(reverse=False)
    print('Files to process:',  len(files))

    df_res = pd.DataFrame(files, columns=['FileName'])
    if len(files) > 10:
        df_res["Group"] = ""
        df_res["ID1"] = ""
        df_res["ID2"] = ""
    df_res["Grade"] = 0
    df_res["Static"] = 0.
    df_res["Dynamic"] = 0
    for test_nr in range(NR_TESTS):
        df_res[f"U{test_nr}_pt"] = 0
        df_res[f"U{test_nr}_return_0"] = ""
        df_res[f"U{test_nr}_return_1"] = ""
        df_res[f"U{test_nr}_error"] = ""

    file_nr = 0
    while file_nr < len(files):
        if len(files) > 10:
            group_data = files[file_nr].split("_")
            df_res.at[file_nr, "Group"] = group_data[0]
            df_res.at[file_nr, "ID1"] = group_data[1]
            df_res.at[file_nr, "ID2"] = group_data[2]

        group_module = __import__(files[file_nr])

        static_score = 0.
        dynamic_score = 0

        with suppress_stdout():
            try:
                results = lint.Run([files[file_nr] + '.py'], do_exit=False)
                static_score = results.linter.stats.global_note
            except UnicodeError:
                static_score = -1.        
        df_res.at[file_nr, "Static"] = static_score

        for test_nr in range(NR_TESTS):
            points, return_0, return_1, error_str = unit_test(group_module, test_nr)
            df_res.at[file_nr, f"U{test_nr}_pt"] = points
            df_res.at[file_nr, f"U{test_nr}_return_0"] = return_0
            df_res.at[file_nr, f"U{test_nr}_return_1"] = return_1
            df_res.at[file_nr, f"U{test_nr}_error"] = error_str
            dynamic_score += points
        
        df_res.at[file_nr, "Dynamic"] = dynamic_score

        df_res.at[file_nr, 'Grade'] = round(0.2*static_score
                                            + 8*(dynamic_score/NR_TESTS), 1)

        file_nr += 1

    df_res.to_excel(HOMEWORK + "_results.xlsx")

if __name__ == '__main__':
    grade_submissions()
