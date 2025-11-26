from pydantic import BaseModel, Field

class FinalOutput(BaseModel):
    """Respond to the question in below format."""
    response: str = Field(description="First check the human message, if the query needed tool message, use it, otherwise use AI message to respond")
