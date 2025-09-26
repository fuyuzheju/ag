import tempfile
import subprocess
import os
import sys

env = os.environ.copy()
env["CLICOLOR_FORCE"]="1"

ENTER_ALT_SCREEN = "\033[?1049h"
EXIT_ALT_SCREEN = "\033[?1049l"
CURSOR_HOME = "\033[H"
CLEAR_TO_END = "\033[J"
CLEAR_BUFFER = "\x1b]1337;ClearScrollback\x07"

def check_glow_installed():
    try:
        subprocess.run(['glow', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def clear_screen(clear = False):
    if clear:
        print(f"{CLEAR_BUFFER}", end="")
    else:
        print(f"{CURSOR_HOME}{CLEAR_TO_END}", end="")

def glow(file_path):
    try:
        result = subprocess.run(
            ["glow", "-s", "dark", file_path],
            capture_output=True,
            text=True,
            check=True,
            stdin=subprocess.DEVNULL,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        print("glow:", str(e))
        raise ValueError
    return result.stdout


def output_renderer(temp_file_path):
    """
    A generator
    yields the rendered lines,
    receiving the next chunk of text
    """
    # last_rendered_lines_count = 0
    if os.name == 'nt': # Windows
        os.system('')
    # print(ENTER_ALT_SCREEN, end="")

    try:
        i = 0
        while True:
            i += 1
            new_text_chunk = yield None

            if new_text_chunk == None:
                # quit
                clear_screen(True)
                rendered_output = glow(temp_file_path)
                sys.stdout.write(rendered_output)
                sys.stdout.flush()
                # time.sleep(5)
                break

            with open(temp_file_path, 'a', encoding="utf-8") as f:
                f.write(new_text_chunk)

            
            clear_screen((i%10==0))


            rendered_output = glow(temp_file_path)

            sys.stdout.write(rendered_output)
            sys.stdout.flush()

    finally:
        # print(EXIT_ALT_SCREEN, end="")
        pass

def main():
    if not check_glow_installed():
        print("glow not found. please install it.")
        sys.exit(1)

    temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8")
    temp_file_path = temp_file.name
    temp_file.close()

    try:
        renderer = output_renderer(temp_file_path)
        next(renderer)
        while True:
            try:
                next_text_chunk = input()
            except EOFError:
                break
            
            renderer.send(next_text_chunk + '\n')
        
        try:
            renderer.send(None) # quit
        except StopIteration:
            pass

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

main()

