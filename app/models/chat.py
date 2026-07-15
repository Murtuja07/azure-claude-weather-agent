from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        examples=[
            "Will it rain tomorrow in Leeds?"
        ],
    )


class ChatResponse(BaseModel):
    answer: str