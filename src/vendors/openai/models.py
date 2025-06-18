class GPTModel:
    FourOh = "gpt-4o"
    FourPointOne = "gpt-4.1"
    FourOhMini = "gpt-4o-mini"


MODEL_NAME = "GPT"
DEFAULT_MODEL_OPTION = "4.1"
MODEL_OPTIONS = {
    "4o": GPTModel.FourOh,
    "4o-mini": GPTModel.FourOhMini,
    "4.1": GPTModel.FourPointOne,
}
