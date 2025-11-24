class GPTModel:
    FivePointOne = "gpt-5.1"
    FiveMini = "gpt-5-mini"
    FiveNano = "gpt-5-nano"


MODEL_NAME = "GPT"
DEFAULT_MODEL_OPTION = "5.1"
MODEL_OPTIONS = {
    "5.1": GPTModel.FivePointOne,
    "5-mini": GPTModel.FiveMini,
    "5-nano": GPTModel.FiveNano,
}
