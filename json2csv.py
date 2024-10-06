import json, csv, os, sys

def kuro_json_to_csv(json_filename):
    with open(json_filename, 'rb') as f:
        json_dat = json.loads(f.read())
    for block in json_dat['data']:
        with open("{0}_{1}.csv".format(json_filename, block['name']), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, block['data'][0].keys())
            w.writeheader()
            for row in block['data']:
                w.writerow(row)
    return

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # If argument given, attempt to export from file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('json_filename', help="Name of kuro json file to export from (required).")
        args = parser.parse_args()
        if os.path.exists(args.json_filename) and args.json_filename[-5:].lower() == '.json':
            kuro_json_to_csv(args.json_filename)
    else:
        json_files = glob.glob('*.json')
        for i in range(len(json_files)):
            kuro_json_to_csv(json_files[i])
