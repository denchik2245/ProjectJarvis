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
        # Если сервер возвращает формат с ключом "choices"
        if isinstance(data, dict) and "choices" in data:
            text_response = "".join(choice.get("text", "") for choice in data["choices"])
        # Если возвращается список чанков
        elif isinstance(data, list):
            text_response = "".join(chunk.get("content", "") for chunk in data)
        else:
            text_response = data.get("completion", "")
        return text_response.strip()
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе к Ollama:", e)
        return ""

def build_system_prompt(user_text: str) -> str:
    """
    Формирует системный промт, включающий подробные примеры для всех команд.
    """
    examples = []
    for command, phrases in COMMAND_PROMPTS.items():
        for phrase in phrases:
            examples.append(f"Пользователь: \"{phrase}\"\nОтвет: {{\"command\": \"{command}\", \"arguments\": {{}}}}")
    examples_text = "\n\n".join(examples)
    prompt = (
        "Ты являешься высококвалифицированным голосовым ассистентом, специализирующимся на понимании и анализе запросов на русском языке. "
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


def parse_command_from_text(user_text: str) -> dict:
    system_prompt = build_system_prompt(user_text)
    response = ask_ollama(system_prompt)
    print("Ответ от Ollama:", response)  # для отладки

    json_candidates = []
    matches = re.findall(r'(\{.*?\})', response, re.DOTALL)
    for candidate in matches:
        try:
            data = json.loads(candidate)
            if "command" in data:
                json_candidates.append(data)
        except json.JSONDecodeError:
            continue

    # Если есть кандидаты, сначала ищем тот, у которого command != "unknown"
    selected = None
    for cand in json_candidates:
        if cand.get("command", "unknown") != "unknown":
            selected = cand
            break
    if not selected and json_candidates:
        selected = json_candidates[-1]
    if not selected:
        selected = {"command": "unknown", "arguments": {}}

    # Гарантируем наличие ключей
    if "command" not in selected:
        selected["command"] = "unknown"
    if "arguments" not in selected:
        selected["arguments"] = {}
    return selected