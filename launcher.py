import os
import sys
import urllib.request
import subprocess
import argparse

def convert_to_bool(in_bool):
    # Convert the input to string and lower case, then check against true values
    return str(in_bool).lower() in ('true', 'on', '1', 'y', 'yes')

def install_packages_from_requirements(requirements_file):
    try:
        subprocess.run(['pip3', 'install', '-r', requirements_file, '--upgrade'], check=True)
        print("Packages installed successfully using pip3.")
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['pip', 'install', '-r', requirements_file, '--upgrade'], check=True)
            print("Packages installed successfully using pip.")
        except subprocess.CalledProcessError:
            print("Failed to install packages using both pip3 and pip.")

def download_from_github(url, output_file):
    try:
        with urllib.request.urlopen(url) as response, open(output_file, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"File downloaded successfully to {output_file}")
    except urllib.error.HTTPError as e:
        print(f"Failed to download file from {url}. HTTP Error Code: {e.code}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"An error occurred: {e}")

def prompt_and_save_bazarr_env_variables():
    instructions = (
        "You will be prompted for several configuration values.\n"
        "If you wish to use the default value for any of them, simply press Enter without typing anything.\n"
        "The default values are shown in brackets [] next to the prompts.\n"
        "Items can be the value of true, on, 1, y, yes, false, off, 0, n, no, or an appropriate text response.\n"
    )
    print(instructions)
    env_vars = {
        'ASR_MODEL': ('Qwen3-ASR Model', 'Enter the Qwen3-ASR model: Qwen/Qwen3-ASR-0.6B, Qwen/Qwen3-ASR-1.7B', 'Qwen/Qwen3-ASR-0.6B'),
        'WEBHOOKPORT': ('Webhook Port', 'Default listening port for subgen.py', '9000'),
        'TRANSCRIBE_DEVICE': ('Transcribe Device', 'Set as cpu or gpu', 'gpu'),
        'DEBUG': ('Debug', 'Enable debug logging (true/false)', 'False'),
        'CLEAR_VRAM_ON_COMPLETE': ('Clear VRAM', 'Attempt to clear VRAM when complete', 'False'),
        'APPEND': ('Append', 'Append \'Transcribed by Qwen3-ASR\' to generated subtitle (true/false)', 'False'),
    }

    user_input = {}
    with open('subgen.env', 'w') as file:
        for var, (description, prompt, default) in env_vars.items():
            value = input(f"{prompt} [{default}]: ") or default
            file.write(f"{var}={value}\n")
    print("Environment variables have been saved to subgen.env")

def load_env_variables(env_filename='subgen.env'):
    try:
        with open(env_filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    var, value = line.split('=', 1)
                    os.environ[var] = value
        print(f"Environment variables have been loaded from {env_filename}")
    except FileNotFoundError:
        print(f"{env_filename} file not found. Consider running with --setup-bazarr or creating it manually.")

def main():
    if 'python3' in sys.executable:
        python_cmd = 'python3'
    elif 'python' in sys.executable:
        python_cmd = 'python'
    else:
        print("Script started with an unknown command")
        sys.exit(1)
    if sys.version_info[0] < 3:
        print(f"This script requires Python 3 or higher, you are running {sys.version}")
        sys.exit(1)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(prog="python launcher.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', action='store_true', help="Enable console debugging (overrides .env and external ENV)")
    parser.add_argument('-i', '--install', action='store_true', help="Install/update all necessary packages")
    parser.add_argument('-a', '--append', action='store_true', help="Append 'Transcribed by Qwen3-ASR' (overrides .env and external ENV)")
    parser.add_argument('-u', '--update', action='store_true', help="Update Qwen3-Subgen")
    parser.add_argument('-x', '--exit-early', action='store_true', help="Exit without running subgen.py")
    parser.add_argument('-s', '--setup-bazarr', action='store_true', help="Prompt for common Bazarr setup parameters and save them for future runs")
    parser.add_argument('-b', '--branch', type=str, default='main', help='Specify the branch to download from')
    parser.add_argument('-l', '--launcher-update', action='store_true', help="Update launcher.py and re-launch")

    args = parser.parse_args()

    branch_name = args.branch if args.branch != 'main' else os.getenv('BRANCH', 'main')
    script_name_suffix = f"-{branch_name}.py" if branch_name != "main" else ".py"
    subgen_script_to_run = f"subgen{script_name_suffix}"
    language_code_script_to_download = f"language_code{script_name_suffix}"

    if args.launcher_update or convert_to_bool(os.getenv('LAUNCHER_UPDATE')):
        print(f"Updating launcher.py from GitHub branch {branch_name}...")
        download_from_github(f"https://raw.githubusercontent.com/McCloudS/subgen/{branch_name}/launcher.py", f'launcher{script_name_suffix}')
        excluded_args = ['--launcher-update', '-l']
        new_args = [arg for arg in sys.argv[1:] if arg not in excluded_args]
        print(f"Relaunching updated launcher: launcher{script_name_suffix}")
        os.execl(sys.executable, sys.executable, f"launcher{script_name_suffix}", *new_args)

    # --- Environment Variable Handling ---
    if args.setup_bazarr:
        prompt_and_save_bazarr_env_variables()
        load_env_variables()
    else:
        load_env_variables()

    # 2. Override with command-line arguments (highest priority for these specific flags)
    if args.debug:
        os.environ['DEBUG'] = 'True'
        print("Launcher CLI: DEBUG set to True")
    elif 'DEBUG' not in os.environ:
        os.environ['DEBUG'] = 'False'
        print("Launcher: DEBUG defaulted to False (no prior setting)")

    if args.append:
        os.environ['APPEND'] = 'True'
        print("Launcher CLI: APPEND set to True")
    elif 'APPEND' not in os.environ:
        os.environ['APPEND'] = 'False'

    requirements_url = "https://raw.githubusercontent.com/McCloudS/subgen/main/requirements.txt"
    requirements_file = "requirements.txt"

    if args.install:
        download_from_github(requirements_url, requirements_file)
        install_packages_from_requirements(requirements_file)

    if not os.path.exists(subgen_script_to_run) or args.update or convert_to_bool(os.getenv('UPDATE')):
        print(f"Downloading {subgen_script_to_run} from GitHub branch {branch_name}...")
        download_from_github(f"https://raw.githubusercontent.com/McCloudS/subgen/{branch_name}/subgen.py", subgen_script_to_run)
        print(f"Downloading {language_code_script_to_download} from GitHub branch {branch_name}...")
        download_from_github(f"https://raw.githubusercontent.com/McCloudS/subgen/{branch_name}/language_code.py", language_code_script_to_download)
    else:
        print(f"{subgen_script_to_run} exists and UPDATE is set to False, skipping download.")

    if not args.exit_early:
        print(f'Launching {subgen_script_to_run}')
        try:
            subprocess.run([python_cmd, '-u', subgen_script_to_run], check=True)
        except FileNotFoundError:
            print(f"Error: Could not find {subgen_script_to_run}. Make sure it was downloaded correctly.")
        except subprocess.CalledProcessError as e:
            print(f"Error running {subgen_script_to_run}: {e}")
    else:
        print("Not running subgen.py: -x or --exit-early set")

if __name__ == "__main__":
    main()
