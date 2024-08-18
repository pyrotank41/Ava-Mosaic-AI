# Mosaic-AI
```
 __   __  _______  _______  _______  ___   _______ 
|  |_|  ||       ||       ||   _   ||   | |       |
|       ||   _   ||  _____||  |_|  ||   | |       |
|       ||  | |  || |_____ |       ||   | |       |
|       ||  |_|  ||_____  ||       ||   | |      _|
| ||_|| ||       | _____| ||   _   ||   | |     |_ 
|_|   |_||_______||_______||__| |__||___| |_______|
```

## About Ava-Mosaic-AI

Mosaic is a lightweight Python library that extends the capabilities of the Instructor library for LLM-based tasks. Born out of a personal project to streamline repetitive processes in GenAI development, Mosaic aims to reduce overhead and simplify common operations in LLM/GenAI projects.

### Key Features

- Extends Instructor library functionality
- Simplifies common LLM-based tasks
- Reduces code repetition in GenAI projects
- Lightweight and easy to integrate

## Installation

```bash
pip install ava-mosaic-ai
```

## Quick Start

```python
import ava_mosaic_ai
from pydantic import BaseModel

# Initialize LLM
llm = ava_mosaic_ai.get_llm("openai")

# Define response model
class ResponseModel(BaseModel):
    response: str

# Use Mosaic's simplified interface
response = llm.create_completion(
    response_model=ResponseModel,
    messages=[{"role": "user", "content": "Tell me a joke about AI"}],
)
print(response)
```

## Documentation

For full documentation, visit [our docs site](https://mosaic-ai.readthedocs.io).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## Roadmap

- [ ] Add support for more LLM providers
- [ ] Implement advanced prompt engineering tools
- [ ] Develop a CLI for quick prototyping

## Special Thanks

- A heartfelt shoutout to [@daveebbelaar](https://github.com/daveebbelaar) for his implementation of `llm_factory`, which inspired this project. Check out his work [here](https://gist.github.com/daveebbelaar/d24eafc6ace1c8f4a091062733b52437).
- Immense gratitude to the creators of the [Instructor library](https://github.com/jxnl/instructor). Their work has saved countless hours in GenAI project development.

## License

Mosaic is released under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Built with ❤️ by [karan Singh Kochar]
