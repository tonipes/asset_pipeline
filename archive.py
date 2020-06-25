import os
import zipfile

def make_archive(base_name, root_dir):
    save_cwd = os.getcwd()
    
    base_name = os.path.abspath(base_name)

    os.chdir(root_dir)

    base_dir = os.curdir

    zip_filename = base_name
    archive_dir = os.path.dirname(base_name)
    os.makedirs(archive_dir, exist_ok=True)

    with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_STORED) as zf:
        path = os.path.normpath(base_dir)

        for dirpath, dirnames, filenames in os.walk(base_dir):
            for name in filenames:
                path = os.path.normpath(os.path.join(dirpath, name))
                if os.path.isfile(path):
                    zf.write(path, "/" + path)

    os.chdir(save_cwd)
