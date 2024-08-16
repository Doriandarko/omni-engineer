import os
import sys
import argparse
from litellm import completion
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style
import difflib
import asyncio
from duckduckgo_search import AsyncDDGS
import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from rich.console import Console
from rich.table import Table
import base64  # Add this to your imports!
from urllib.parse import urlparse
import requests   # Add this too!
from PIL import Image
from io import BytesIO
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.application.current import get_app



is_diff_on = True  

init(autoreset=True)
load_dotenv()
# LiteLLM doesn't require a client initialization

DEFAULT_MODEL = "claude-3-sonnet-20240229"
EDITOR_MODEL = "gemini-pro-1.5"
BASE_URL = None
API_KEY = None
# Other common models:
# "gpt-4"
# "llama-2-70b-chat"
# "claude-3-haiku-20240307"
# "mistral-large-latest"

SYSTEM_PROMPT = """You are an incredible developer assistant. You have the following traits:
- You write clean, efficient code
- You explain concepts with clarity
- You think through problems step-by-step
- You're passionate about helping developers improve

When given an /edit instruction:
- First After completing the code review, construct a plan for the change
- Then provide specific line-by-line edit instructions
- Format your response as edit instructions
- Do NOT execute changes yourself"""

EDITOR_PROMPT = """You are a code-editing AI. Your mission:

ULTRA IMPORTANT:
- YOU NEVER!!! add the type of file at the beginning of the file like ```python etq.
- YOU NEVER!!! add ``` at the start or end of the file meaning you never add anything that is not the code at the start or end of the file.

- Execute line-by-line edit instructions safely
- If a line doesn't need to be changed, output the line as is.
- NEVER add or delete lines, unless explicitly instructed
- YOU ONLY OUTPUT THE CODE.
- NEVER!!! add the type of file at the beginning of the file like ```python etq.
- ULTRA IMPORTANT you NEVER!!! add ``` at the start or end of the file meaning you never add anything that is not the code at the start or end of the file.
- Never change imports or function definitions unless explicitly instructed"""

added_files = []  
stored_searches = {}  
file_templates = {
    "python": "def main():\n    pass\n\nif __name__ == \"__main__\":\n    main()",
    "html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Document</title>\n</head>\n<body>\n    \n</body>\n</html>",
    "javascript": "// Your JavaScript code here"
}
undo_history = {}
stored_images = {}  # Add with your other globals!
command_history = FileHistory('.aiconsole_history.txt')
commands = WordCompleter(['/add', '/edit', '/new', '/search', '/image', '/clear', '/reset', '/diff', '/history', '/save', '/load', '/undo', 'exit'], ignore_case=True)
session = PromptSession(history=command_history)

async def get_input_async(message):
    session = PromptSession()
    result = await session.prompt_async(HTML(f"<ansired>{message}</ansired> "), 
        auto_suggest=AutoSuggestFromHistory(),
        completer=commands,
        refresh_interval=0.5)
    return result.strip()

def encode_image(image_path):
    """Turn a local image into base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None
    except IOError:
        return None

def validate_image_url(url):
    try:
        response = requests.get(
            url, 
            stream=True, 
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.28 Safari/537.36'}
        )
        response.raise_for_status() 
        
        # Check Content-Type
        content_type = response.headers.get('Content-Type', '').lower()
        if content_type.startswith(('image/', 'application/octet-stream')):  
            return True

        # Force load it as an image
        image = Image.open(BytesIO(response.content))
        image.verify()
        
        return True

    except requests.exceptions.RequestException as e:
        print_colored(f"Network error: {e}", Fore.RED)
        return False
    except Image.UnidentifiedImageError:
        print_colored(f"The URL doesn't point to a valid image.", Fore.RED)
        return False
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Fore.RED)
        return False

def is_url(string):
    """Check if a string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


async def handle_image_command(filepaths_or_urls, default_chat_history):
    """Add local images & URLs to memory and chat history"""
    if not filepaths_or_urls:
        print_colored("❌ No images or URLs provided.", Fore.RED)
        return default_chat_history
    
    processed_images = 0
    success_images = 0

    for idx, image_path in enumerate(filepaths_or_urls, 1):
        try:
            if is_url(image_path):  # URL-based
                if validate_image_url(image_path):
                    stored_images[f"image_{len(stored_images) + 1}"] = {
                        "type": "image", 
                        "source": "url", 
                        "content": image_path
                    }
                    default_chat_history.append({
                        "role": "user", 
                        "content": [{"type": "image_url", "image_url": {"url": image_path}}]
                    })
                    print_colored(f"✅ URL-based image {idx} added successfully!", Fore.GREEN)
                    success_images += 1
                else:
                    print_colored(f"❌ {image_path} isn't a valid image URL. Skipping.", Fore.RED)
            
            else:  # Local filepath
                image_content = encode_image(image_path)
                if image_content:
                    try:
                        # Detect if it's actually an image
                        with Image.open(image_path) as img:
                            img_format = img.format.lower()
                            if img_format not in ['jpeg', 'jpg', 'png', 'webp', 'gif']:
                                raise ValueError("Unsupported image format")
                            
                            data_uri = f"data:image/{img_format};base64,{image_content}"
                            
                            stored_images[f"image_{len(stored_images) + 1}"] = {
                                "type": "image", 
                                "source": "local", 
                                "content": data_uri
                            }
                            default_chat_history.append({
                                "role": "user", 
                                "content": [{
                                    "type": "image_url",
                                    "image_url": {"url": data_uri}
                                }]
                            })
                            print_colored(f"✅ Local image {idx} added successfully!", Fore.GREEN)
                            success_images += 1
                    except (IOError, ValueError) as e:
                        print_colored(f"❌ {image_path} isn't a valid image. Error: {e}. Skipping.", Fore.RED)
                else:
                    print_colored(f"❌ Failed loading: {image_path}", Fore.RED)
        
        except Exception as e:
            print_colored(f"❌ Unexpected error processing {image_path}: {e}. Skipping.", Fore.RED)

        processed_images += 1  # Always increment, even if we skip

    print_colored(f"🖼️ {processed_images} images processed. {success_images} added successfully. {len(stored_images)} total images in memory!", Fore.CYAN)
    
    return default_chat_history

async def aget_results(word):
    results = await AsyncDDGS(proxy=None).atext(word, max_results=100)
    return results


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_colored(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)


def get_streaming_response(messages, model):
    stream = completion(
        model=model,
        messages=messages,
        stream=True,
        base_url=BASE_URL,
        api_key=API_KEY,
    )
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print_colored(chunk.choices[0].delta.content, end="")
            full_response += chunk.choices[0].delta.content

    return full_response.strip()


def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"❌ Error: File not found: {filepath}"
    except IOError as e:
        return f"❌ Error reading {filepath}: {e}"


def write_file_content(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError:
        return False
    
def is_text_file(file_path, sample_size=8192, text_characters=set(bytes(range(32,127)) + b'\n\r\t\b')):
    """Determine whether a file is text or binary."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(sample_size)

        if not chunk:  # Empty files are considered text
            return True

        if b'\x00' in chunk:  # Null bytes usually indicate binary
            return False

        # If >30% of chars are non-text, probably binary
        text_chars = sum(byte in text_characters for byte in chunk)
        return text_chars / len(chunk) > 0.7

    except IOError:
        return False


async def handle_add_command(chat_history, *paths):
    global added_files
    contents = []
    new_context = ""

    for path in paths:
        if os.path.isfile(path):  # File handling
            content = read_file_content(path)
            if not content.startswith("❌"):
                contents.append((path, content))
                added_files.append(path)

        elif os.path.isdir(path):  # Directory handling
            print_colored(f"📁 Processing folder: {path}", Fore.CYAN)
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and is_text_file(item_path):
                    content = read_file_content(item_path)
                    if not content.startswith("❌"):
                        contents.append((item_path, content))
                        added_files.append(item_path)

        else:
            print_colored(f"❌ '{path}' is neither a valid file nor folder.", Fore.RED)

    if contents:
        for fp, content in contents:
            new_context += f"""The following file has been added: {fp}:
\n{content}\n\n"""
            
        chat_history.append({"role": "user", "content": new_context})
        print_colored(f"✅ Added {len(contents)} files to knowledge!", Fore.GREEN)
    else:
        print_colored("❌ No valid files were added to knowledge.", Fore.YELLOW)

    return chat_history

async def handle_edit_command(default_chat_history, editor_chat_history, filepaths):
    all_contents = [read_file_content(fp) for fp in filepaths]
    valid_files, valid_contents = [], []

    for filepath, content in zip(filepaths, all_contents):
        if content.startswith("❌"):
            print_colored(content, Fore.RED)
        else:
            valid_files.append(filepath)
            valid_contents.append(content)

    if not valid_files:
        print_colored("❌ No valid files to edit.", Fore.YELLOW)
        return default_chat_history, editor_chat_history

    user_request = await get_input_async(f"What would you like to change in {', '.join(valid_files)}?")

    instructions_prompt = "For these files:\n"
    instructions_prompt += "\n".join([f"File: {fp}\n```\n{content}\n```\n" for fp, content in zip(valid_files, valid_contents)])
    instructions_prompt += f"User wants: {user_request}\nProvide LINE-BY-LINE edit instructions for ALL files. Number each instruction and specify which file it applies to.\n"

    default_chat_history.append({"role": "user", "content": instructions_prompt})
    default_instructions = get_streaming_response(default_chat_history, DEFAULT_MODEL)
    default_chat_history.append({"role": "assistant", "content": default_instructions})

    print_colored("\n" + "=" * 50, Fore.MAGENTA)

    for idx, (filepath, content) in enumerate(zip(valid_files, valid_contents), 1):
        print_colored(f"📝 EDITING {filepath} ({idx}/{len(valid_files)}):", Fore.BLUE)

        edit_message = f"""
        Original code:

        {content}

        Instructions: {default_instructions}

        Follow only instructions applicable to {filepath}. Output ONLY the new code. No explanations. DO NOT ADD ANYTHING ELSE. no type of file at the beginning of the file like ```python etq. no ``` at the end of the file.
        """

        editor_chat_history.append({"role": "user", "content": edit_message})

        current_content = read_file_content(filepath)  # Read fresh
        if current_content.startswith("❌"):  # Your phenomenal error check
            return default_chat_history, editor_chat_history

        lines = current_content.split('\n')
        buffer = ""
        result = ""
        line_index = 0  

        for chunk in completion(
            model=EDITOR_MODEL,   
            messages=editor_chat_history,
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print_colored(content, end="")  
                buffer += content
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line_index < len(lines):  
                        lines[line_index] = line   
                        write_file_content(filepath, '\n'.join(lines))  
                        print_colored(f"✏️ Updated Line {line_index+1}: {line[:50]}...", Fore.CYAN)  # Show debug
                        line_index += 1
                    else:
                        lines.append(line)  
                        write_file_content(filepath, '\n'.join(lines)) 
                        print_colored(f"➕ NEW Line {line_index+1}: {line[:50]}...", Fore.YELLOW)  
                        line_index += 1

        result = '\n'.join(lines)
        undo_history[filepath] = current_content   # Store undo 
        editor_chat_history.append({"role": "assistant", "content": result})

        if is_diff_on:  
            display_diff(current_content, result)  # Show final diff if it's on

        print_colored(f"✅ {filepath} successfully edited!", Fore.GREEN)
        print_colored("=" * 50, Fore.MAGENTA)

    return default_chat_history, editor_chat_history

async def handle_new_command(default_chat_history, editor_chat_history, filepaths):
    print_colored(f"🆕 Creating new files: {', '.join(filepaths)}", Fore.BLUE)
    created_files = []
    for filepath in filepaths:
        file_ext = os.path.splitext(filepath)[1][1:]  
        template = file_templates.get(file_ext, "")  
        try:
            with open(filepath, 'x') as f:  
                f.write(template)
            print_colored(f"✅ Created {filepath} with template", Fore.GREEN)
            created_files.append(filepath)
        except FileExistsError:
            print_colored(f"⚠️ {filepath} already exists. It will be edited, not overwritten.", Fore.YELLOW)
            created_files.append(filepath)
        except IOError as e:
            print_colored(f"❌ Could not create {filepath}: {e}", Fore.RED)

    if created_files:
        user_input = (await get_input_async(f"Do you want to edit the newly created files? (y/n):")).lower()  # Fixed line!
        if user_input == 'y':
            default_chat_history, editor_chat_history = await handle_edit_command(
                default_chat_history, editor_chat_history, created_files
            )

    return default_chat_history, editor_chat_history


async def handle_clear_command():
    global added_files, stored_searches, stored_images  # Add stored_images!
    cleared_something = False

    if added_files:
        added_files.clear()
        cleared_something = True
        print_colored("✅ Cleared memory of added files.", Fore.GREEN)
    
    if stored_searches:
        stored_searches.clear()
        cleared_something = True
        print_colored("✅ Cleared stored searches.", Fore.GREEN)
    
    if stored_images:  # New!
        image_count = len(stored_images)
        stored_images.clear()
        cleared_something = True
        print_colored(f"✅ Cleared {image_count} images from memory.", Fore.GREEN)

    if not cleared_something:
        print_colored("ℹ️ No files, searches or images in memory to clear.", Fore.YELLOW)


async def handle_reset_command(default_chat_history, editor_chat_history):
    """Clears all chat history and added files memory."""
    global added_files, stored_searches, stored_images
    default_chat_history.clear()
    editor_chat_history.clear()
    added_files.clear()
    stored_searches.clear()
    stored_images.clear()

    # Re-initialize:
    default_chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    editor_chat_history = [{"role": "system", "content": EDITOR_PROMPT}]

    print_colored(
        "✅ All chat history, memory of added files, stored searches, and images have been reset.",
        Fore.GREEN,
    )

    return default_chat_history, editor_chat_history  # Return the resetted histories


def toggle_diff():
    global is_diff_on
    is_diff_on = not is_diff_on
    status = "on" if is_diff_on else "off"
    print_colored(
        f"Diff is now {status} 🚀" if is_diff_on else f"Diff is now {status} 🚫",
        Fore.YELLOW,
    )


def handle_history_command(chat_history):
    print_colored("\n📜 Chat History:", Fore.BLUE)
    for idx, message in enumerate(chat_history[1:], 1):  # Skip system message
        role = message['role'].capitalize()
        content = message['content'][:100] + "..." if len(message['content']) > 100 else message['content']
        print_colored(f"{idx}. {role}: {content}", Fore.CYAN)

async def handle_save_command(chat_history):
    filename = await get_input_async("Enter filename to save chat history:")
    try:
        with open(filename, 'w') as f:
            json.dump(chat_history, f)
        print_colored(f"✅ Chat history saved to {filename}", Fore.GREEN)
    except IOError as e:
        print_colored(f"❌ Error saving chat history: {e}", Fore.RED)

async def handle_load_command():
    filename = await get_input_async("Enter filename to load chat history:")
    try:
        with open(filename, 'r') as f:
            loaded_history = json.load(f)
        print_colored(f"✅ Chat history loaded from {filename}", Fore.GREEN)
        return loaded_history
    except IOError as e:
        print_colored(f"❌ Error loading chat history: {e}", Fore.RED)
        return None

async def handle_undo_command(filepath):
    if filepath in undo_history:
        content = undo_history[filepath]
        if write_file_content(filepath, content):
            print_colored(f"✅ Undid last edit for {filepath}", Fore.GREEN)
        else:
            print_colored(f"❌ Failed to undo edit for {filepath}", Fore.RED)
    else:
        print_colored(f"❌ No undo history for {filepath}", Fore.RED)

def syntax_highlight(code, language):
    lexer = get_lexer_by_name(language)
    return highlight(code, lexer, TerminalFormatter())


def print_welcome_message():
    print_colored(
        "🔮 Welcome to the OpenAI Developer Console! 🔮", Fore.MAGENTA, Style.BRIGHT
    )
    print_colored("\nAvailable commands:", Fore.GREEN)
    print_colored("/add", Fore.CYAN, end="")
    print_colored(" <filepath1> <filepath2> ...", Style.DIM)
    print_colored("Add one or more files to the AI's knowledge base")
    print_colored("/edit", Fore.CYAN, end="")
    print_colored(" <filepath1> <filepath2> ...", Style.DIM)
    print_colored("Edit one or more existing files")
    print_colored("/new", Fore.CYAN, end="")
    print_colored(" <filepath1> <filepath2> ...", Style.DIM)
    print_colored("Create one or more new files")
    print_colored("/search", Fore.CYAN)
    print_colored("Perform a DuckDuckGo search and store the results")
    print_colored("/clear", Fore.CYAN)
    print_colored("Clear all files from the AI's memory that were added with /add command")
    print_colored("/reset", Fore.CYAN)
    print_colored(
        "Reset the entire chat and file memory to start fresh without restarting the script"
    )
    print_colored("/diff", Fore.CYAN)
    print_colored("Toggle the display of diffs on or off")
    print_colored("/history", Fore.CYAN)
    print_colored("View chat history")
    print_colored("/save", Fore.CYAN)
    print_colored("Save chat history to a file")
    print_colored("/load", Fore.CYAN)
    print_colored("Load chat history from a file")
    print_colored("/undo", Fore.CYAN)
    print_colored(" <filepath>", Style.DIM)
    print_colored("Undo last edit for a specific file")
    print_colored("exit", Fore.CYAN)
    print_colored("Exit the application")
    print_colored(
        "\nFor any other input, the AI will respond to your query or command.",
        Fore.YELLOW,
    )


def print_files_and_searches_in_memory():
    if added_files:
        file_list = ', '.join(added_files)
        print_colored(
            f"📂 Files currently in memory: {file_list}", Fore.CYAN, Style.BRIGHT
        )
    if stored_searches:
        search_list = ', '.join(stored_searches.keys())
        print_colored(
            f"🔍 Searches currently in memory: {search_list}", Fore.CYAN, Style.BRIGHT
        )


def display_diff(original, edited):
    diff = difflib.unified_diff(
        original.splitlines(), edited.splitlines(), lineterm='', n=0
    )
    for line in diff:
        if line.startswith('+'):
            print_colored(line, Fore.GREEN)
        elif line.startswith('-'):
            print_colored(line, Fore.RED)
        else:
            print_colored(line, Fore.BLUE)


async def handle_search_command(default_chat_history):
    search_query = await get_input_async("What would you like to search?")
    print_colored(f"\n🔍 Searching for: {search_query}", Fore.BLUE)

    try:
        results = await aget_results(search_query)
        search_name = search_query[:10].strip()  # Truncate to first 10 characters
        stored_searches[search_name] = results
        print_colored(f"✅ Search results for '{search_name}' stored in memory.", Fore.GREEN)

        # Add search results to chat history
        search_content = f"Search results for '{search_query}':\n"
        for idx, result in enumerate(results[:8], 1):  # Limit to first 5 results for brevity
            search_content += f"{idx}. {result['title']}: {result['body'][:100]}...\n"
        default_chat_history.append({"role": "user", "content": search_content})

    except Exception as e:
        print_colored(f"❌ Error performing search: {e}", Fore.RED)

    return default_chat_history


from textwrap import dedent

def print_welcome_message():
    print_colored(
        "🔮 Welcome to the Assistant Developer Console! 🔮", Fore.MAGENTA, Style.BRIGHT
    )
    

    console = Console()
    table = Table()
    
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description")
    
    table.add_row("/add", "Add files to AI's knowledge base")
    table.add_row("/edit", "Edit existing files")
    table.add_row("/new", "Create new files")
    table.add_row("/search", "Perform a DuckDuckGo search")
    table.add_row("/image", "Add image(s) to AI's knowledge base")
    table.add_row("/clear", "Clear added files, searches, and images from AI's memory")
    table.add_row("/reset", "Reset entire chat and file memory")
    table.add_row("/diff", "Toggle display of diffs")
    table.add_row("/history", "View chat history")
    table.add_row("/save", "Save chat history to a file")
    table.add_row("/load", "Load chat history from a file")
    table.add_row("/undo", "Undo last edit for a specific file")
    table.add_row("exit", "Exit the application")
    
    console.print(table)
    
    print_colored(
        "For any other input, the AI will respond to your query or command.",
        Fore.YELLOW,
    )
    print_colored(
        "Use '<command> help' for more information on a specific command.",
        Fore.YELLOW,
    )



def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Developer Console")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use for completion")
    parser.add_argument("--openai-api-base", help="Base URL for the OpenAI API")
    parser.add_argument("--openai-api-key", help="API key for OpenAI")
    return parser.parse_args()

async def main():
    args = parse_arguments()
    global DEFAULT_MODEL, BASE_URL, API_KEY
    DEFAULT_MODEL = args.model
    BASE_URL = args.openai_api_base
    API_KEY = args.openai_api_key

    default_chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    editor_chat_history = [{"role": "system", "content": EDITOR_PROMPT}]
    clear_console()
    print_welcome_message()
    print_files_and_searches_in_memory()

    while True:
        prompt = await get_input_async(f"\n\nYou:")

        print_files_and_searches_in_memory()

        if prompt.lower() == "exit":
            print_colored(
                "Thank you for using the OpenAI Developer Console. Goodbye!", Fore.MAGENTA
            )
            break

    

        if prompt.startswith("/add "):
            filepaths = prompt.split("/add ", 1)[1].strip().split()
            default_chat_history = await handle_add_command(default_chat_history, *filepaths)
            continue

        if prompt.startswith("/edit "):
            filepaths = prompt.split("/edit ", 1)[1].strip().split()
            default_chat_history, editor_chat_history = await handle_edit_command(  # Add "await" here
                default_chat_history, editor_chat_history, filepaths
            )
            continue

        if prompt.startswith("/new "):
            filepaths = prompt.split("/new ", 1)[1].strip().split()
            default_chat_history, editor_chat_history = await handle_new_command(   # Add "await" here
                default_chat_history, editor_chat_history, filepaths
            )
            continue

        if prompt.startswith("/search"):
            default_chat_history = await handle_search_command(default_chat_history)
            continue

        if prompt.startswith("/clear"):
            await handle_clear_command()   # Add await here
            continue

        if prompt.startswith("/reset"):
            default_chat_history, editor_chat_history = await handle_reset_command(  # Add await here
                default_chat_history, editor_chat_history
            )
            default_chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]  
            editor_chat_history = [{"role": "system", "content": EDITOR_PROMPT}]
            continue

        if prompt.startswith("/diff"):
            toggle_diff()
            continue

        if prompt.startswith("/history"):
            handle_history_command(default_chat_history)
            continue

        if prompt.startswith("/save"):
            await handle_save_command(default_chat_history)
            continue

        if prompt.startswith("/image "):
            image_paths = prompt.split("/image ", 1)[1].strip().split()
            default_chat_history = await handle_image_command(image_paths, default_chat_history)
            continue

        if prompt.startswith("/load"):
            loaded_history = await handle_load_command()   # Add await here
            if loaded_history:
                default_chat_history = loaded_history
            continue

        if prompt.startswith("/undo "):
            filepath = prompt.split("/undo ", 1)[1].strip()
            await handle_undo_command(filepath)
            continue

        print_colored("\n🤖 Assistant:", Fore.BLUE)
        try:
            default_chat_history.append({"role": "user", "content": prompt})
            response = get_streaming_response(default_chat_history, DEFAULT_MODEL)
            default_chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            print_colored(f"Error: {e}. Please try again.", Fore.RED)


if __name__ == "__main__":
    asyncio.run(main())
