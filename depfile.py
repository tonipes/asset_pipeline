target_line_format = "{target} : \\\n"
dep_line_format = " {dep} \\\n"

def gen_depfile(target, deps):
    res = ""
    res += target_line_format.format(target=target)

    for dep in deps:
        res += dep_line_format.format(dep=dep)
    
    res = res[:-2] + "\n" # remove last slash

    return res
