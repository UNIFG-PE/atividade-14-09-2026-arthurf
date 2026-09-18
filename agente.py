import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY não encontrada no .env")


client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


MODEL = "openai/gpt-5.6"


WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)


SYSTEM_PROMPT = """
Você é um agente de programação.

Seu objetivo é ajudar o usuário a programar e modificar projetos.

Você pode pedir ao sistema para:
- ler arquivos;
- escrever arquivos;
- executar comandos.

Quando precisar fazer alguma dessas coisas, responda usando EXATAMENTE
um bloco no seguinte formato:

<tool>
{"name": "nome_da_ferramenta", "args": {...}}
</tool>

Ferramentas disponíveis:

read_file:
{"path": "caminho"}

write_file:
{"path": "caminho", "content": "conteúdo completo"}

run_command:
{"command": "comando"}

Se não precisar usar uma ferramenta, responda normalmente.

Todos os caminhos são relativos ao workspace.
"""


def read_file(path):
    file_path = WORKSPACE / path

    if not file_path.exists():
        return f"Arquivo não encontrado: {path}"

    if not file_path.is_file():
        return f"Não é um arquivo: {path}"

    return file_path.read_text(encoding="utf-8")


def write_file(path, content):
    file_path = WORKSPACE / path

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")

    return f"Arquivo escrito com sucesso: {path}"


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return (
            f"Exit code: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    except subprocess.TimeoutExpired:
        return "Comando cancelado: excedeu 30 segundos."


def execute_tool(tool_call):
    name = tool_call["name"]
    args = tool_call.get("args", {})

    if name == "read_file":
        return read_file(args["path"])

    if name == "write_file":
        return write_file(
            args["path"],
            args["content"],
        )

    if name == "run_command":
        return run_command(args["command"])

    return f"Ferramenta desconhecida: {name}"


def ask_model(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return response.choices[0].message.content


def main():
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    print("Agente de programação iniciado.")
    print("Digite 'exit' para sair.\n")

    while True:
        user_input = input("Você > ")

        if user_input.lower() == "exit":
            break

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        while True:
            response = ask_model(messages)

            print(f"\nAgente > {response}\n")

            # Verifica se o modelo pediu uma ferramenta
            if "<tool>" not in response:
                break

            try:
                import json

                tool_text = response.split(
                    "<tool>",
                    1,
                )[1].split(
                    "</tool>",
                    1,
                )[0].strip()

                tool_call = json.loads(tool_text)

                result = execute_tool(tool_call)

                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Resultado da ferramenta:\n"
                            + result
                        ),
                    }
                )

            except Exception as e:
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Erro ao executar ferramenta: {e}"
                        ),
                    }
                )

    print("Agente encerrado.")


if __name__ == "__main__":
    main()