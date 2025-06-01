import pikepdf
import re

def extract_pdf_javascript(pdf_path):
    """
    Extracts JavaScript code from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        list: A list of strings, where each string is a piece of JavaScript code found.
              Returns an empty list if no JavaScript is found or if an error occurs.
    """
    javascript_code = []
    try:
        with pikepdf.Pdf.open(pdf_path) as pdf:
            for name in pdf.Root.get("/Names", {}).get("/JavaScript", {}).get("/Names", []):
                if isinstance(name, pikepdf.String):
                    obj_ref = name
                    # The JavaScript code is in the /S /JS part of the object
                    # The actual reference can be indirect.
                    # We are looking for objects that are dictionaries and have a /JS entry.
                    try:
                        js_action = pdf.get_object(obj_ref)
                        if js_action and isinstance(js_action, pikepdf.Dictionary) and '/JS' in js_action:
                            js_code = js_action.JS
                            if isinstance(js_code, pikepdf.String):
                                javascript_code.append(str(js_code))
                            elif isinstance(js_code, pikepdf.Stream):
                                javascript_code.append(js_code.read_bytes().decode('utf-8', errors='ignore'))
                    except Exception:
                        # Sometimes names are just that, names, not objects with JS
                        pass

            # JavaScript can also be in document-level actions
            if '/OpenAction' in pdf.Root:
                open_action = pdf.Root.OpenAction
                if open_action and isinstance(open_action, pikepdf.Dictionary) and open_action.get('/S') == '/JavaScript' and '/JS' in open_action:
                    js_code = open_action.JS
                    if isinstance(js_code, pikepdf.String):
                        javascript_code.append(str(js_code))
                    elif isinstance(js_code, pikepdf.Stream):
                        javascript_code.append(js_code.read_bytes().decode('utf-8', errors='ignore'))
            
            # JavaScript can also be embedded in other objects, like annotations or actions.
            # This is a more general search but might be slower on very large files.
            for obj in pdf.objects:
                if isinstance(obj, pikepdf.Dictionary):
                    # Check for /AA (Additional Actions) in various objects
                    if '/AA' in obj:
                        additional_actions = obj.AA
                        if isinstance(additional_actions, pikepdf.Dictionary):
                            for action_type in additional_actions:
                                action_dict = additional_actions.get(action_type)
                                if isinstance(action_dict, pikepdf.Dictionary) and action_dict.get('/S') == '/JavaScript' and '/JS' in action_dict:
                                    js_code = action_dict.JS
                                    if isinstance(js_code, pikepdf.String):
                                        code_str = str(js_code)
                                        if code_str not in javascript_code: # Avoid duplicates
                                            javascript_code.append(code_str)
                                    elif isinstance(js_code, pikepdf.Stream):
                                        code_bytes = js_code.read_bytes().decode('utf-8', errors='ignore')
                                        if code_bytes not in javascript_code: # Avoid duplicates
                                            javascript_code.append(code_bytes)
                    # Check directly for /S /JavaScript entries
                    if obj.get('/S') == '/JavaScript' and '/JS' in obj:
                        js_code = obj.JS
                        if isinstance(js_code, pikepdf.String):
                            code_str = str(js_code)
                            if code_str not in javascript_code: # Avoid duplicates
                                javascript_code.append(code_str)
                        elif isinstance(js_code, pikepdf.Stream):
                            code_bytes = js_code.read_bytes().decode('utf-8', errors='ignore')
                            if code_bytes not in javascript_code: # Avoid duplicates
                                javascript_code.append(code_bytes)

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    # Clean up potential duplicates if different encodings/representations led to them
    # This is a basic deduplication. More sophisticated might be needed if JS is obfuscated.
    unique_javascript_code = []
    seen_code = set()
    for code in javascript_code:
        # A simple normalization step: remove leading/trailing whitespace
        normalized_code = code.strip()
        if normalized_code and normalized_code not in seen_code:
            unique_javascript_code.append(normalized_code)
            seen_code.add(normalized_code)
            
    return unique_javascript_code

if __name__ == "__main__":
    pdf_file_path = input("Enter the path to your PDF file: ")
    extracted_js = extract_pdf_javascript(pdf_file_path)

    if extracted_js:
        print("\n--- Extracted JavaScript ---")
        for i, js in enumerate(extracted_js):
            print(f"\n--- Script {i+1} ---")
            print(js)
        
        # Optionally, save to a file
        save_to_file = input("\nDo you want to save the extracted JavaScript to a file? (yes/no): ").lower()
        if save_to_file == 'yes':
            output_file_path = "extracted_javascript.js"
            with open(output_file_path, "w", encoding="utf-8") as f:
                for i, js in enumerate(extracted_js):
                    f.write(f"// --- Script {i+1} ---\n")
                    f.write(js)
                    f.write("\n\n")
            print(f"JavaScript saved to {output_file_path}")
    else:
        print("No JavaScript found or an error occurred during extraction.")