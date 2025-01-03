import platform
import subprocess as sp

from rich.console import Console
from rich.padding import Padding
from rich.markup import escape
from rich.progress import Progress
import psutil

from src.schema import ChatState, ChatMessage, Role, ChatMode, CommandOption
from .base import BaseAction

NO_COMMAND = "NO_COMMAND_EXTRACTED"


class ShellAction(BaseAction):

    cmd_options = [
        CommandOption(
            template="\shell",
            description="Toggle shell mode",
            prefix="\shell",
        ),
        CommandOption(
            template="\shell <query>",
            description="Run shell command",
            prefix="\shell",
            example="\shell how much free disk space do I have",
        ),
    ]

    def __init__(self, console: Console, vendor, model_option: str) -> None:
        super().__init__(console)
        self.vendor = vendor
        self.model_option = model_option

    def is_match(self, query_text: str, state: ChatState, cmd_options: list[CommandOption]) -> bool:
        matches_other_cmd = self.matches_other_cmd(query_text, state, cmd_options)
        if matches_other_cmd:
            return False
        elif state.mode == ChatMode.Shell:
            return bool(query_text)
        else:
            return query_text.startswith(r"\shell")

    def run(self, query_text: str, state: ChatState) -> ChatState:
        if state.mode == ChatMode.Shell and query_text == "\shell":
            state.mode = ChatMode.Chat
            self.con.print(f"[bold yellow]Shell mode disabled[/bold yellow]\n")
            return state
        elif state.mode != ChatMode.Shell and query_text == "\shell":
            state.mode = ChatMode.Shell
            self.con.print(f"[bold yellow]Shell mode enabled[/bold yellow]\n")
            return state
        elif state.mode == ChatMode.Shell and not query_text.startswith(r"\shell "):
            goal = query_text.strip()
        elif query_text.startswith(r"\shell "):
            goal = query_text[7:].strip()
        else:
            self.con.print(f"\n[bold yellow]Shell command not recognised[/bold yellow]\n")

        system_info = get_system_info()
        shell_instruction = f"""
        Write a single shell command to help the user achieve this goal in the context of this chat: {goal}
        Do not suggest shell commands that require interactive or TTY mode: these commands get run in a non-interactive subprocess.
        Include a brief explanation (1-2 sentences) of why you chose this shell command, but keep the explanation clearly separated from the command.
        Structure your response so that you start with the explanation and emit the shell command at the end.
        System info (take this into consideration):
        {system_info}
        """
        shell_msg = ChatMessage(role=Role.User, content=shell_instruction)
        state.messages.append(shell_msg)
        model = self.vendor.MODEL_OPTIONS[self.model_option]
        with Progress(transient=True) as progress:
            progress.add_task(
                f"[red]Generating shell command {self.vendor.MODEL_NAME} ({self.model_option})...",
                start=False,
                total=None,
            )
            message = self.vendor.chat(state.messages, model)

        state.messages.append(message)
        self.con.print(f"\nAssistant:")
        formatted_text = Padding(escape(message.content), (1, 2))
        self.con.print(formatted_text, width=80)
        command_str = extract_shell_command(message.content, self.vendor, self.model_option)
        if command_str == NO_COMMAND:
            no_extract_msg = "No command could be extracted"
            self.con.print(f"\n[bold yellow]{no_extract_msg}[/bold yellow]")
            state.messages.append(ChatMessage(role=Role.User, content=no_extract_msg))
            return state

        self.con.print(f"\n[bold yellow]Execute this command?[/bold yellow]")
        self.con.print(f"[bold cyan]{command_str}[/bold cyan]")
        user_input = input("Enter Y/n: ").strip().lower()

        if user_input == "y" or user_input == "":
            try:
                result = sp.run(command_str, shell=True, text=True, capture_output=True)
                output = f"Command: {command_str}\n\nExit Code: {result.returncode}"
                if result.stdout:
                    output += f"\n\nStdout:\n{result.stdout}"
                if result.stderr:
                    output += f"\n\nStderr:\n{result.stderr}"
                self.con.print(f"\n[bold blue]Shell Command Output:[/bold blue]")
                formatted_output = Padding(escape(output), (1, 2))
                self.con.print(formatted_output)
                state.messages.append(
                    ChatMessage(role=Role.User, content=f"Shell command executed:\n\n{output}")
                )
            except Exception as e:
                error_message = f"Error executing shell command: {str(e)}"
                self.con.print(f"\n[bold red]{error_message}[/bold red]")
                state.messages.append(ChatMessage(role=Role.User, content=error_message))

            # FIXME: Shell output is using a lot of tokens, could we swap it for just the followup message?
            followup_instruction = f"""
            Write a brief (1 sentence) followup commentary on the result of the execution of the command: {command_str}
            based on the user's original request: {goal}
            """
            followup_msg = ChatMessage(role=Role.User, content=followup_instruction)
            state.messages.append(followup_msg)

            with Progress(transient=True) as progress:
                progress.add_task(
                    f"[red]Analysing shell output {self.vendor.MODEL_NAME} ({self.model_option})...",
                    start=False,
                    total=None,
                )
                message = self.vendor.chat(state.messages, model)

            state.messages.append(message)
            self.con.print(f"\nAssistant:")
            formatted_text = Padding(escape(message.content), (1, 2))
            self.con.print(formatted_text, width=80)
            return state
        else:
            self.con.print("\n[bold yellow]Command execution cancelled.[/bold yellow]")
            cancel_message = f"Command execution cancelled by user."
            state.messages.append(ChatMessage(role=Role.User, content=cancel_message))
            return state


def extract_shell_command(assistant_message: str, vendor, model_option: str) -> str:
    """
    Extract a shell command to be executed from the assistant's message
    """
    model = vendor.MODEL_OPTIONS[model_option]
    query_text = f"""
    Extract the proprosed shell command from this chat log.
    Return only a single shell command and nothing else.
    This is the chat log:
    {assistant_message}

    If there is not any command to extract then return only the exact string {NO_COMMAND}
    """
    return vendor.answer_query(query_text, model)


def get_system_info() -> str:
    system = platform.system()
    if system == "Windows":
        os_info = f"Windows {platform.release()}"
        additional_info = platform.win32_ver()
    elif system == "Darwin":
        mac_ver = platform.mac_ver()
        os_info = f"macOS {mac_ver[0]}"
        arch = platform.machine()
        additional_info = f"Arch: {arch}"
    elif system == "Linux":
        os_info = f"Linux {platform.release()}"
        try:
            with open("/etc/os-release") as f:
                distro_info = dict(line.strip().split("=") for line in f if "=" in line)
            additional_info = distro_info.get("PRETTY_NAME", "").strip('"')
        except:
            additional_info = "Distribution information unavailable"
    else:
        os_info = f"Unknown OS: {system}"
        additional_info = "No additional information available"

    cpu_info = f"CPU: {platform.processor()}"
    ram = psutil.virtual_memory()
    ram_info = f"RAM: {ram.total // (1024**3)}GB total, {ram.percent}% used"
    disk = psutil.disk_usage("/")
    disk_info = f"Disk: {disk.total // (1024**3)}GB total, {disk.percent}% used"

    return f"{os_info}\n{additional_info}\n{cpu_info}\n{ram_info}\n{disk_info}"
