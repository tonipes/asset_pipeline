import os

def all_files_in(path):
    files = []
    for r, d, f in os.walk(path):
        files += [os.path.join(r, fi) for fi in f]
    return files

def mkdir(path):
    if path:
        os.makedirs(path, exist_ok=True)

def substitute(inputs=[], **substitutions):
    return [i.format(**substitutions) for i in inputs]

def build_substitutes(input_file, input_root_folder, output_root_folder):
    relative_filepath = os.path.relpath(input_file, input_root_folder)
    relative_folder = os.path.dirname(relative_filepath)

    output_file = os.path.normpath(os.path.join(output_root_folder, relative_filepath))
    input_local_folder = os.path.normpath(os.path.join(input_root_folder, relative_folder))
    output_local_folder = os.path.normpath(os.path.join(output_root_folder, relative_folder))

    return {
        "file_name":            os.path.basename(input_file),
        "file_basename":        os.path.splitext(os.path.basename(input_file))[0],
        "file_extension":       os.path.splitext(os.path.basename(input_file))[1],

        "relative_folder":      relative_folder,
        "relative_filepath":    relative_filepath,

        "input_filepath":       input_file,
        "output_filepath":      output_file,

        "input_local_folder":   input_local_folder,
        "output_local_folder":  output_local_folder,

        "input_root_folder":    input_root_folder,
        "output_root_folder":   output_root_folder,
    }
