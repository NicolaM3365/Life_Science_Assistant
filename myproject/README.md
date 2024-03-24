# Research Support Project

This Life Science Assistant project is designed to support researchers by providing tools for PDF analysis, chat with PDFs, summarization, and more. It leverages the PDF.ai API for document handling and analysis.

## Features

- Upload PDFs via URL or file upload.
- Chat with PDFs to get insights or ask questions about the content.
- Summarize PDFs to get a concise overview of the document's key points.
- Delete PDFs from the system and AI Drive.
- Search through uploaded PDFs based on title or author.
- View detailed information about a specific PDF, including chat history.


## Live Demo

You can access a live demo of the Life Science Assistant project here: Life Science Assistant on Render

https://life-science-assistant-1.onrender.com


## Cloning the Repository

To get started with the Life Science Assistant project, you can clone the repository to your local machine using the following command:

```bash

git clone https://github.com/NicolaM3365/Life_Science_Assistant.git

## Setup

1. Clone the repository to your local machine.
2. Ensure you have Python and Django installed.
3. Set up a virtual environment and activate it.
4. Install the project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Create a `.env` file in the project root and add your PDF.ai API key:

    ```plaintext
    PDF_AI_API_KEY='your_api_key_here'
    ```

6. Run the Django migrations:

    ```bash
    python manage.py migrate
    ```

7. Start the Django development server:

    ```bash
    python manage.py runserver
    ```

8. Open a web browser and go to `http://localhost:8000` to see the project in action.

## Key Dependencies

- Django: The web framework for building the application.
- Requests: Used to make HTTP requests to the PDF.ai API.
- Django Crispy Forms & Crispy Bootstrap5: For rendering forms.
- Pillow: For handling image uploads.
- Gunicorn & Whitenoise: For serving the application and static files.

## Environment Variables

- `PDF_AI_API_KEY`: The API key for accessing the PDF.ai services.

## Logging

Logging is configured to output debug and error information to the console, aiding in development and troubleshooting.

## Database Configuration

This project uses PostgreSQL in production with connection settings defined in `settings.py`. For local development, SQLite can be used for simplicity.

## Security

Remember to set `DEBUG` to `False` in production and use environment variables to manage sensitive information like the `SECRET_KEY` and database credentials.

## Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

## License

Specify your project's license here.
