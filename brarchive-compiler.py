import zipfile
import os
import subprocess
import sys
import json
import shutil
import time

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color=Colors.END, bold=False):
    bold_code = Colors.BOLD if bold else ''
    print(f"{bold_code}{color}{text}{Colors.END}")

def create_pack(pack_folders, output_filepath, root_structure=False):
    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name, folder_path in pack_folders:
            if root_structure:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)
            else:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, os.path.dirname(folder_path))
                        zipf.write(file_path, relative_path)
    return output_filepath

def validate_manifest(folder_path, expected_type):
    manifest_path = os.path.join(folder_path, 'manifest.json')
    if not os.path.exists(manifest_path):
        return False
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        modules = data.get('modules', [])
        for mod in modules:
            if mod.get('type') == expected_type:
                return True
        return False
    except:
        return False

def find_valid_pack_folders(base_path):
    found = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and item.upper() in ['RP', 'BP']:
            expected_type = 'resources' if item.upper() == 'RP' else 'data'
            if validate_manifest(item_path, expected_type):
                found.append((item.upper(), item_path))
    return found

def fix_filename(filename, extension):
    if filename.endswith(extension):
        return filename
    if filename.endswith('.mcaddon') or filename.endswith('.mcpack'):
        base = os.path.splitext(filename)[0]
        return base + extension
    return filename + extension

def clean_dist_folder(dist_dir):
    if os.path.exists(dist_dir):
        try:
            shutil.rmtree(dist_dir)
        except:
            pass

def delete_config(config_path):
    if os.path.exists(config_path):
        try:
            os.remove(config_path)
        except:
            pass

def ensure_config(script_dir):
    config_path = os.path.join(script_dir, "pack_optimizer_config.json")
    dist_dir = os.path.join(script_dir, "dist")
    
    # Garantir que a pasta dist seja removida antes de qualquer coisa
    clean_dist_folder(dist_dir)
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config_path, config
    
    src_dir = os.path.join(script_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)
    
    config = {
        "input_directory": src_dir.replace('\\', '/'),
        "output_directory": dist_dir.replace('\\', '/'),
        "verbose_logging": True
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_path, config

def run_compilation(server_dir, config_path, output_dir):
    print_colored("Compiling packs to brarchive...", Colors.CYAN)
    
    if not os.path.exists(server_dir):
        print_colored("Error: Server directory not found", Colors.RED, bold=True)
        return False
    
    server_exe = os.path.join(server_dir, "bedrock_server.exe")
    if not os.path.exists(server_exe):
        print_colored("Error: bedrock_server.exe not found", Colors.RED, bold=True)
        return False
    
    cmd = f'"{server_exe}" "PackOptimizerConfigPath={config_path}"'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=server_dir,
            capture_output=True,
            text=True
        )
        
        time.sleep(2)
        
        if not os.path.exists(output_dir):
            print_colored("Error: Output directory was not created", Colors.RED, bold=True)
            return False
        
        items = os.listdir(output_dir)
        has_pack = any(item.upper() in ['RP', 'BP'] for item in items)
        
        if not has_pack:
            print_colored("Error: No RP or BP folders found in output", Colors.RED, bold=True)
            return False
        
        valid_folders = find_valid_pack_folders(output_dir)
        if not valid_folders:
            print_colored("Error: Pack validation failed (missing manifest or wrong module type)", Colors.RED, bold=True)
            return False
        
        if result.returncode != 0:
            print_colored("Error: Compilation process failed", Colors.RED, bold=True)
            return False
        
        print_colored("Compilation successful!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"Error: {e}", Colors.RED, bold=True)
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(script_dir, "bedrock_server")
    
    print_colored("=" * 60, Colors.CYAN, bold=True)
    print_colored("  Brarchive Compiler", Colors.CYAN, bold=True)
    print_colored("=" * 60, Colors.CYAN, bold=True)
    
    config_path, config = ensure_config(script_dir)
    output_dir = config["output_directory"]
    
    if not run_compilation(server_dir, config_path, output_dir):
        print_colored("Compilation failed. Exiting.", Colors.RED, bold=True)
        delete_config(config_path)
        return
    
    pack_folders = find_valid_pack_folders(output_dir)
    
    if not pack_folders:
        print_colored("Error: No valid packs found", Colors.RED, bold=True)
        delete_config(config_path)
        return
    
    found_names = [name for name, _ in pack_folders]
    has_rp = 'RP' in found_names
    has_bp = 'BP' in found_names
    
    if has_rp and not has_bp:
        extension = ".mcpack"
        pack_type = "Resource Pack"
        root_structure = True
    elif has_bp and not has_rp:
        extension = ".mcaddon"
        pack_type = "Behavior Pack"
        root_structure = False
    else:
        extension = ".mcaddon"
        pack_type = "Addon (Resource + Behavior)"
        root_structure = False
    
    print_colored(f"\nPack type: {pack_type} ({extension})", Colors.YELLOW)
    
    print(f"\nEnter the name for the output file (must end with {extension})")
    filename = input("Filename: ").strip()
    
    if not filename:
        print_colored("\nError: Filename cannot be empty!", Colors.RED, bold=True)
        delete_config(config_path)
        return
    
    filename = fix_filename(filename, extension)
    output_path = os.path.join(output_dir, filename)
    
    # Garantir caminho com barras normais
    output_path = output_path.replace('\\', '/')
    
    try:
        print_colored(f"\nCreating {filename}...", Colors.CYAN)
        create_pack(pack_folders, output_path, root_structure)
        
        print_colored(f"\nSuccess! {pack_type} created!", Colors.GREEN, bold=True)
        print(f"   {output_path}")
        print_colored(f"   Size: {os.path.getsize(output_path) / 1024:.2f} KB", Colors.BLUE)
        
    except Exception as e:
        print_colored(f"\nError creating pack: {e}", Colors.RED, bold=True)
    
    delete_config(config_path)
    
    print_colored("\n" + "=" * 60, Colors.CYAN, bold=True)
    print_colored("  Created by Italo Amorim", Colors.GREEN, bold=True)
    print_colored("  https://github.com/iamorimm", Colors.BLUE)
    print_colored("=" * 60, Colors.CYAN, bold=True)

if __name__ == "__main__":
    main()