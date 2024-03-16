import json
import os
import hashlib
from pathlib import Path
import urllib.parse

jrepo = None
contents = {}
files_registered = []


def init_repo():
    global contents, jrepo
    contents = {}
    jrepo = json.loads(open("dynamicmcpack.repo.json", "r").read())
    for x in jrepo["contents"]:
        contents[x["url"]] = json.loads(open(x["url"], "r").read())
        cont = contents[x["url"]]["content"]
        for file in cont["files"]:
            path = cont["parent"] + "/" + file
            if (len(cont["parent"]) == 0):
                path = file;

            files_registered.append(path)


def save_jrepo():
    global jrepo
    open("dynamicmcpack.repo.json", "w").write(json.dumps(jrepo, indent='\t'))


def add_new_content():
    file = input(" filename -> ");
    j = {
        "url": file,
        "hash": "enterhash",
        "id": input(" content id -> ")
    };
    jrepo["contents"].append(j)
    contents[file] = {
        "formatVersion": 1,
        "content": {
            "parent": "",
            "files": {}
        }
    }
    open(file, "w").write(json.dumps(contents[file], indent='\t'))
    save_jrepo()


def recalculate_hashes():
    for x in contents:
        print("Content: " + x)
        parent = contents[x]["content"]["parent"]
        files = contents[x]["content"]["files"]
        for filePath in files:
            globalFilePath = parent + "/" + filePath
            if len(parent) == 0:
                globalFilePath = filePath;
            fileJson = contents[x]["content"]["files"][filePath]
            fileJson["hash"] = hash(globalFilePath)
            print(f"Set hash of {globalFilePath}")
        open(x, "w").write(json.dumps(contents[x], indent='\t'))

        # Calculate hash for content.json file and write to repo main file
        i = 0
        for x1 in jrepo["contents"]:
            print(f"repo content x1{x1}")
            if x1["url"] == x:
                jrepo["contents"][i]["hash"] = hash(x)
                print(f"hash of {x} in {x1} written")
                break
            i = i + 1

    save_jrepo()


def preview_changes():
    for x in contents:
        parent = contents[x]["content"]["parent"]
        files = contents[x]["content"]["files"]
        for filePath in files:
            globalFilePath = parent + "/" + filePath
            if len(parent) == 0:
                globalFilePath = filePath;
            fileJson = contents[x]["content"]["files"][filePath]
            actialHash = hash(globalFilePath)
            currentHash = fileJson["hash"];
            if (actialHash != currentHash):
                print(f"CHANGES: {globalFilePath}")


def remake_content():
    file = input("content file -> ")
    if not file in contents:
        print("Content pack not exists. Create before...")
        return

    directory = input("subdirectory to scan -> ")
    if directory == "":
        print("ERROR: No, make content from full root is a bad idea. Type 'assets' for use this folder.")
        return

    content = contents[file]["content"]
    cleany = input("Clean oldest content in this file (for example deleted files)\n\t\t[Y/n] -> ")
    if cleany == "y" or cleany == "Y":
        content["files"] = {}
        print("Cleared!")

    content["parent"] = directory
    for e in get_filepaths("./"):
        e = e[2::]
        if not e.startswith(directory):
            continue;

        print(f"File {e} updated!")
        content["files"][e.replace(directory + "/", "").replace(" ", "%20")] = {
            "hash": hash(e)
        }

    open(file, "w").write(json.dumps(contents[file], indent='\t'))


def main():
    global jrepo
    init_repo()
    print("Repos:")
    for x in contents:
        print(" * ", x, contents[x])

    print("REGISTERED FILES", files_registered)

    act = input("Enter action\n * [0] Add new content\n * [1] Recalculate hashes\n * [2] Preview changes (already "
                "existed only)\n * [3] Find unassigned files with content\n * [4] Re-make content(quiz)\n\t\n -> ")
    if act == "0":
        add_new_content()

    if act == "1":
        recalculate_hashes()

    if act == "2":
        preview_changes()

    if act == "3":
        for e in get_filepaths("./"):
            e = e[2::]
            if (not e.startswith(input("dir to check ->"))):
                continue;

            if (not (e in files_registered)):
                print(f"Unassigned file: {e}")

    if act == "4":
        remake_content();


def hash(file):
    if Path(file).exists():
        return hashlib.sha1(open(file, "rb").read()).hexdigest()

    else:
        return ""


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


# Run the above function and store its results in a variable.

if __name__ == '__main__':
    main();
