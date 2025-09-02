## Project structure
The project uses uv, run python scripts with uv run

## Code style
Use type hints when possible. Avoid relative importants when possible.
If the class is pydantic model, do not override __init__ Also, assume Pydantic >=2 by default
We use eliot as default logging library using with start_action(...) as action pattern. Please, use it.
Try to avoid too many try catch blocks as we have logging