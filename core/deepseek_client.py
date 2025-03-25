import re
import requests
import json
import logging


logger = logging.getLogger(__name__)

class DeepseekClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434/v1/completions",
                 model: str = "deepseek-r1:14b", temperature: float = 0.2):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature

    def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature
        }
        try:
            response = requests.post(self.base_url, json=payload)
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
            logger.error("Ошибка при запросе к Deepseek: %s", e)
            return ""

    def build_system_prompt(self, user_text: str) -> str:
        from nlp.prompts import COMMAND_PROMPTS  # импортируем наш шаблон
        examples = []
        for command, data in COMMAND_PROMPTS.items():
            for phrase in data["examples"]:
                examples.append(f'Пользователь: "{phrase}"\nОтвет: {{"command": "{command}", "arguments": {{}}}}')
        examples_text = "\n\n".join(examples)
        prompt = (
            "Ты голосовой ассистент, понимающий запросы на русском языке. "
            "Твоя задача — определить команду, которую хочет выполнить пользователь, и вернуть ответ строго в формате JSON с двумя ключами: \"command\" и \"arguments\".\n\n"
            "Примеры запросов и соответствующих ответов:\n"
            f"{examples_text}\n\n"
            "Теперь пользователь сказал:\n"
            f"\"{user_text}\"\n\n"
            "Проанализируй запрос и верни только JSON."
        )
        return prompt

    def parse_command(self, user_text: str) -> dict:
        system_prompt = self.build_system_prompt(user_text)
        response = self.ask(system_prompt)
        logger.debug("Ответ от Deepseek: %s", response)
        json_candidates = []

        # Попытка извлечь JSON из блока с ```json ... ```
        if "```json" in response:
            try:
                json_block = re.search(r"```json(.*?)```", response, re.DOTALL)
                if json_block:
                    json_text = json_block.group(1).strip()
                    data = json.loads(json_text)
                    json_candidates.append(data)
            except Exception as e:
                logger.error("Ошибка при разборе JSON из блока: %s", e)

        # Если не нашли через блок, ищем все объекты JSON в ответе
        if not json_candidates:
            matches = re.findall(r'(\{.*?\})', response, re.DOTALL)
            for candidate in matches:
                try:
                    data = json.loads(candidate)
                    if "command" in data:
                        json_candidates.append(data)
                except json.JSONDecodeError:
                    continue

        selected_command = None
        for cand in json_candidates:
            if cand.get("command") != "unknown":
                selected_command = cand
                break

        if not selected_command:
            selected_command = {"command": "unknown", "arguments": {}}

        # Если команда unknown, или если команда get_contact_info, но contact_name недостаточно полное – выполняем фолбэк.
        if selected_command.get("command") == "unknown" or (
                selected_command.get("command") == "get_contact_info" and
                len(selected_command.get("arguments", {}).get("contact_name", "").split()) < 2
        ):
            lower_text = user_text.lower()
            # Удаляем знаки препинания
            lower_text_clean = re.sub(r"[^\w\s]", "", lower_text)
            # Пытаемся извлечь полное имя (минимум два слова) после ключевых слов "номер", "телефон" или "контакт"
            multi_name_match = re.search(
                r"\b(?:номер|телефон|контакт)\s+((?:[а-яё]+\s+){1,}[а-яё]+)",
                lower_text_clean
            )
            if multi_name_match:
                full_name = multi_name_match.group(1).strip()
            else:
                # Если не нашли полное имя, попробуем одно слово
                single_name_match = re.search(r"(?:номер|телефон|контакт)\s+([а-яё]+)", lower_text_clean)
                full_name = single_name_match.group(1).strip() if single_name_match else ""
            # Также пытаемся извлечь метку (например, "из" или "по")
            label_match = re.search(r"(?:из|по)\s+([а-яё]+)", lower_text_clean)
            label = label_match.group(1).strip() if label_match else ""
            selected_command = {
                "command": "get_contact_info",
                "arguments": {
                    "contact_name": full_name,
                    "field": "phone",
                    "label": label,
                    "multiple": False
                }
            }
        return selected_command