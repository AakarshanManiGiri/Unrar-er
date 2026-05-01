import os
import zipfile
import shutil
from pathlib import Path

def find_zip_in_script_folder():
    """find zip file in same folder"""
    script_dir = Path(__file__).parent
    zip_files = list(script_dir.glob("*.zip"))
    
    if not zip_files:
        print("no zip files found in script folder")
        return None
    
    if len(zip_files) == 1:
        return zip_files[0]
    
    # multiple zips found
    print("\nfound multiple zip files:")
    for i, zf in enumerate(zip_files, 1):
        print(f"  {i}. {zf.name}")
    
    while True:
        try:
            choice = int(input("\nSelect zip file number: "))
            if 1 <= choice <= len(zip_files):
                return zip_files[choice - 1]
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a valid number")

def extract_and_find_nested_zips(main_zip_path):
    """extract main zip and return nested zips"""
    script_dir = Path(__file__).parent
    temp_dir = script_dir / "temp_extract"
    
    # clean up existing temp directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    print(f"\nextracting main zip: {main_zip_path.name}")
    with zipfile.ZipFile(main_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # find nested zips
    nested_zips = list(temp_dir.rglob("*.zip"))
    print(f"found {len(nested_zips)} zip file(s) inside")
    
    return nested_zips, temp_dir

def display_zip_contents(zip_path):
    """display zip contents"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files = zip_ref.namelist()
            return files
    except Exception as e:
        print(f"Error reading zip: {e}")
        return []

def select_items_to_extract(all_items, auto_extract=False):
    """let user select items to extract"""
    if auto_extract:
        return all_items
    
    print("\navailable items:")
    for i, item in enumerate(all_items, 1):
        print(f"  {i}. {item}")
    
    print("\nenter item numbers to extract (comma-separated, or 'all'): ", end="")
    user_input = input().strip().lower()
    
    if user_input == "all":
        return all_items
    
    try:
        selections = [int(x.strip()) - 1 for x in user_input.split(",")]
        selected = [all_items[i] for i in selections if 0 <= i < len(all_items)]
        return selected
    except:
        print("Invalid selection, extracting all items")
        return all_items

def extract_nested_zips(nested_zips, temp_dir, auto_extract=False):
    """extract contents from nested zips"""
    script_dir = Path(__file__).parent
    output_dir = script_dir / "extracted_files"
    output_dir.mkdir(exist_ok=True)
    
    all_extracted = []
    
    for idx, nested_zip in enumerate(nested_zips, 1):
        if auto_extract:
            print(f"\n[{idx}/{len(nested_zips)}] extracting: {nested_zip.name}")
        else:
            print(f"\nprocessing: {nested_zip.name}")
        
        try:
            contents = display_zip_contents(nested_zip)
            
            if not contents:
                print(f"  {nested_zip.name} is empty")
                continue
            
            # select items to extract
            selected = select_items_to_extract(contents, auto_extract=auto_extract)
            
            # Extract selected items
            with zipfile.ZipFile(nested_zip, 'r') as zip_ref:
                for item in selected:
                    if not auto_extract:
                        print(f"  extracting: {item}")
                    zip_ref.extract(item, output_dir)
                    all_extracted.append(item)
        
        except Exception as e:
            print(f"  error processing {nested_zip.name}: {e}")
    
    return output_dir, all_extracted

def main():
    print("=" * 50)
    print("nested zip extractor")
    print("=" * 50)
    
    # Find main zip file
    main_zip = find_zip_in_script_folder()
    if not main_zip:
        return
    
    try:
        # Extract main zip and find nested zips
        nested_zips, temp_dir = extract_and_find_nested_zips(main_zip)
        
        if not nested_zips:
            print("no zip files found inside main zip")
            return
        
        # ask user extraction mode
        print(f"\nfound {len(nested_zips)} nested zip files")
        print("choose extraction mode:")
        print("  1. extract all automatically (no prompts)")
        print("  2. select items for each zip (interactive)")
        
        mode_choice = input("\nselect mode (1 or 2): ").strip()
        auto_extract = mode_choice == "1"
        
        # extract from nested zips
        output_dir, extracted_items = extract_nested_zips(nested_zips, temp_dir, auto_extract=auto_extract)
        
        # cleanup temp directory
        shutil.rmtree(temp_dir)
        
        print("\n" + "=" * 50)
        print("extraction complete")
        print(f"output folder: {output_dir}")
        print(f"files extracted: {len(extracted_items)}")
        print("=" * 50)
        
        # open output folder
        if input("\nopen output folder? (y/n): ").lower() == 'y':
            os.startfile(output_dir)
    
    except Exception as e:
        print(f"\nerror: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
