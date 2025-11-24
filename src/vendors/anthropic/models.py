class ClaudeModel:
    Opus = "claude-opus-4-5-20251101"
    Sonnet = "claude-sonnet-4-5-20250929"
    Haiku = "claude-haiku-4-5-20251001"


MODEL_NAME = "Claude"
DEFAULT_MODEL_OPTION = "opus"
MODEL_OPTIONS = {
    "opus": ClaudeModel.Opus,
    "sonnet": ClaudeModel.Sonnet,
    "haiku": ClaudeModel.Haiku,
}
