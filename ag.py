from google import genai
from google.genai import types
from dotenv import load_dotenv
import argparse, gnureadline, subprocess, sys

load_dotenv()

client = genai.Client()
render_mode = False # mark if markdown rendering is enabled
render_stream = sys.stdout

def output_stream(stream):
    thoughts = ""
    answer = ""
    for chunk in stream:
        for part in chunk.candidates[0].content.parts: # type: ignore
            if not part.text:
                continue
            elif part.thought:
                if not thoughts:
                    print("### ----- Thoughts summary -----", flush=True, file=render_stream)
                print(part.text, end="", flush=True, file=render_stream)
                thoughts += part.text
            else:
                if not answer:
                    print("### ----- Answer -----", flush=True, file=render_stream)
                print(part.text, end="", flush=True, file=render_stream)
                answer += part.text
    print(file=render_stream)
    

def ask(prompt, model, thinking):
    print(f"# ======== {model} ========", flush=True, file=render_stream)
    try:
        stream = client.models.generate_content_stream(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(include_thoughts=thinking))
        )
        output_stream(stream)

    except Exception as e:
        print("Error when generating content:", str(e), flush=True, file=sys.stderr)
        return

def interact(model, thinking, addition):
    try:
        chat_session = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(include_thoughts=thinking))
        )
        
        print("# ======== User ========", flush=True, file=render_stream)
        while True:
            print(addition, flush=True, end="", file=render_stream)
            try:
                prompt = input()
                if render_mode:
                    print(prompt, flush=True, file=render_stream) # output to stdout, to let the renderer read it
            except EOFError:
                break

            stream = chat_session.send_message_stream(addition + prompt)
            print(f"\n\n\n# ======== {model} ========", flush=True, file=render_stream)
            output_stream(stream)
            print("\n\n\n# ======== User ========", flush=True, file=render_stream)
    
    except Exception as e:
        print("Error when generating content:", str(e), flush=True, file=sys.stderr)
        return


def main():
    global render_mode, render_process, render_stream

    parser = argparse.ArgumentParser(description="Chat with AI.")
    parser.add_argument("prompt", nargs="?", help="prompt")
    parser.add_argument("-t", "--think", dest="thinking", action="store_true", help="Show thinking budget")
    parser.add_argument("-m", "--model", dest="model", default="gemini-2.5-flash")
    parser.add_argument("-a", "--addition", dest="addition", default="")
    parser.add_argument("-g", "--glow", dest="render", action="store_true")

    args = parser.parse_args()
    if args.render:
        render_mode = True
        render_process = subprocess.Popen(["python", "renderer.py"], stdin=subprocess.PIPE, text=True)
        render_stream = render_process.stdin

    if args.prompt is None:
        interact(args.model, args.thinking, args.addition) 
    else:
        ask(args.addition + args.prompt, args.model, args.thinking)

    if args.render:
        render_process.stdin.close()
        render_process.wait()

main()
