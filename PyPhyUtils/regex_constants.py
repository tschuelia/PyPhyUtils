# define some regex stuff
blanks = r"\s+"  # matches >=1  subsequent whitespace characters
sign = r"[-+]?"  # contains either a '-' or a '+' symbol or none of both
# matches ints or floats of forms '1.105' or '1.105e-5' or '1.105e5' or '1.105e+5'
float_re = r"\d+(?:[\.]?\d+)?(?:[e][-+]?\d+)?"

tree_id_re = r"\d+"  # tree ID is an int
llh_re = rf"{sign}{float_re}"  # likelihood is a signed floating point
deltaL_re = rf"{sign}{float_re}"  # deltaL is a signed floating point
# test result entry is of form '0.123 +'
test_result_re = rf"{float_re}{blanks}{sign}"

stat_test_name = r"[a-zA-Z-]+"