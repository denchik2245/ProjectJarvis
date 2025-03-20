# В файле ollama.py

import requests
import json
import re
from nlp.prompts import COMMAND_PROMPTS

def ask_ollama(prompt: str) -> str:
    url = "http://127.0.0.1:11434/v1/completions"
    payload = {
        "model": "deepseek-r1:14b",
        "prompt": prompt,
        "temperature": 0.2
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "choices" in data:
            text_response = "".join(choice.get("text", "") for choice in data["choices"])
        elif isinstance(data, list):
            text_response = "".join(chunk.get("content", "") for chunk in data)
        else:
            text_response = data.get("completion", "")

        return text_response.strip()
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе к Ollama:", e)
        return ""

def build_system_prompt(user_text: str) -> str:
    examples = []
    for command, data in COMMAND_PROMPTS.items():
        for phrase in data["examples"]:
            examples.append(f"Пользователь: \"{phrase}\"\nОтвет: {{\"command\": \"{command}\", \"arguments\": {{}}}}")
    examples_text = "\n\n".join(examples)
    prompt = (
        "Ты являешься высококвалифицированным голосовым ассистентом, специализирующимся на понимании запросов на русском языке. "
        "Твоя задача — определить, какую команду хочет выполнить пользователь, и вернуть ответ строго в формате JSON, содержащем два ключа: \"command\" и \"arguments\".\n\n"
        "Важно:\n"
        "1. Ответ должен быть исключительно JSON, без каких-либо пояснений или комментариев.\n"
        "2. Ответ должен начинаться с символа '{' и заканчиваться символом '}'.\n"
        "3. Если команда не распознана или не поддерживается, возвращай: {\"command\": \"unknown\", \"arguments\": {}}.\n\n"
        "Примеры запросов и соответствующих ответов:\n"
        f"{examples_text}\n\n"
        "Теперь пользователь сказал:\n"
        f"\"{user_text}\"\n\n"
        "Проанализируй запрос и верни только JSON."
    )
    return prompt

def parse_command_from_text(user_text: str) -> list:
    system_prompt = build_system_prompt(user_text)
    response = ask_ollama(system_prompt)
    print("Ответ от Ollama:", response)  # для отладки

    json_candidates = []

    # Сначала пытаемся извлечь JSON из блока, обрамленного ```json ... ```
    if "```json" in response:
        try:
            json_block = re.search(r"```json(.*?)```", response, re.DOTALL)
            if json_block:
                json_text = json_block.group(1).strip()
                data = json.loads(json_text)
                json_candidates.append(data)
        except Exception as e:
            print("Ошибка при разборе JSON из блока:", e)

    # Если не нашли через блок, пробуем искать все объекты JSON в ответе
    if not json_candidates:
        matches = re.findall(r'(\{.*?\})', response, re.DOTALL)
        for candidate in matches:
            try:
                data = json.loads(candidate)
                if "command" in data:
                    json_candidates.append(data)
            except json.JSONDecodeError:
                continue

    # Выбираем первый кандидат, у которого команда не "unknown"
    selected_command = None
    for cand in json_candidates:
        if cand.get("command") != "unknown":
            selected_command = cand
            break

    if not selected_command:
        selected_command = {"command": "unknown", "arguments": {}}
    else:
        # Если команда create_event — заполняем недостающие поля
        if selected_command.get("command") == "create_event":
            arguments = selected_command.get("arguments", {})
            if "title" not in arguments:
                arguments["title"] = "Без названия"
            if "start_time" not in arguments:
                arguments["start_time"] = "00:00"
            if "end_time" not in arguments:
                arguments["end_time"] = arguments.get("start_time", "00:00")
            if "description" not in arguments:
                arguments["description"] = ""
            if "reminder" not in arguments:
                arguments["reminder"] = False
            selected_command["arguments"] = arguments

    return [selected_command]