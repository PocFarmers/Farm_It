from typing import Optional, List, Literal, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    # Message utilisateur actuel
    message: str

    # Contexte libre : objet, liste ou texte.
    # Il sera intégré proprement au prompt.
    context: Optional[Union[dict, list, str]] = None

    # Historique optionnel au format "messages"
    history: Optional[List[Message]] = None

    # Surcharge optionnelle du "system prompt"
    system: Optional[str] = "Tu es un assistant utile et concis. Réponds en français si possible."

    # Modèle OpenAI
    model: Optional[str] = "gpt-4.1-mini"

class ChatResponse(BaseModel):
    text: str
    model: str
    usage_input_tokens: Optional[int] = None
    usage_output_tokens: Optional[int] = None

def build_input_blocks(system: str,
                       history: Optional[List[Message]],
                       user_message: str,
                       context: Optional[Union[dict, list, str]]) -> List[dict]:
    """
    Construit l'entrée pour le Responses API : une liste de blocs 'input' avec rôles.
    On sérialise le contexte s'il est structuré.
    """
    blocks: List[dict] = []

    # Bloc système
    if system:
        blocks.append({"role": "system", "content": system})

    # Contexte : injecté dans un bloc système supplémentaire pour séparation claire
    if context is not None:
        if isinstance(context, (dict, list)):
            ctx = json.dumps(context, ensure_ascii=False, indent=2)
        else:
            ctx = str(context)
        blocks.append({
            "role": "system",
            "content": f"CONTEXTE À CONSIDÉRER (ne pas répéter tel quel) :\n{ctx}"
        })

    # Historique
    if history:
        for m in history:
            blocks.append({"role": m.role, "content": m.content})

    # Message utilisateur courant
    blocks.append({"role": "user", "content": user_message})

    return blocks