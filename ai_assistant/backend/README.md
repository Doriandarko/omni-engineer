# AI-Assisted Developer Tool Backend

This is the backend for the AI-assisted developer tool, built with FastAPI and providing both API and CLI interfaces.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables by copying `.env.example` to `.env` and filling in the values.

## Running the Application

To run the API:

```
uvicorn api.main:app --reload
```

To use the CLI:

```
python -m cli.main
```

## Running Tests

```
pytest
```

## Project Structure

- `api/`: FastAPI application
- `cli/`: Click-based CLI application
- `core/`: Shared core functionality
- `utils/`: Utility functions and configurations
- `tests/`: Unit and integration tests

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License.