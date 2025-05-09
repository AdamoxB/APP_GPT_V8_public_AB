# SŁOWNIK SŁOWNIKÓW CENNIKI MODELI
model_pricings = {
    "gpt-4o": {  # NAJBARDZIEJ WSZECHSTRONNY MODEL OFEROWANY OPENAI
        "input_tokens": 2.50 / 1_000_000,  # per token ZERA MOŻNA ROZDZIELAĆ W PYTONIE _
        "output_tokens": 10.00 / 1_000_000,  # per token
    },
    "gpt-4o-mini": {  # SZYBSZA ZNACZNIE TAŃSZA WERSJA MODELU OFEROWANY OPENAI
        "input_tokens": 0.150 / 1_000_000,  # per token
        "output_tokens": 0.600 / 1_000_000,  # per token
    },
    "gpt-4.1-nano": {  # SZYBSZA ZNACZNIE TAŃSZA WERSJA MODELU OFEROWANY OPENAI
        "input_tokens": 0.100 / 1_000_000,  # per token
        "output_tokens": 0.400 / 1_000_000,  # per token
    },
    "gpt-4.1-mini": {  # SZYBSZA ZNACZNIE TAŃSZA WERSJA MODELU OFEROWANY OPENAI
        "input_tokens": 0.400 / 1_000_000,  # per token
        "output_tokens": 1.600 / 1_000_000,  # per token
    },
    "gpt-4.1": {  # SZYBSZA ZNACZNIE TAŃSZA WERSJA MODELU OFEROWANY OPENAI
        "input_tokens": 2.00 / 1_000_000,  # per token
        "output_tokens": 8.00 / 1_000_000,  # per token
    },
    "o4-mini": {  # Szybszy, bardziej przystępny model do rozumowania
        "input_tokens": 1.1 / 1_000_000,  # per token
        "output_tokens": 4.40 / 1_000_000,  # per token
    },
    "o3-mini": {  # Szybszy, bardziej przystępny model do rozumowania
        "input_tokens": 1.1 / 1_000_000,  # per token
        "output_tokens": 4.40 / 1_000_000,  # per token
    }
}