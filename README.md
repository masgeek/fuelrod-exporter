Of course, here is the directory structure formatted as a markdown code block that you can copy.

```
fuelrod-exporter/
├── src/
│   └── fuelrod_exporter/
│       ├── __init__.py
│       ├── app.py            # Main Flask application
│       ├── config.py         # Configuration settings
│       ├── models.py         # Pydantic models
│       ├── database.py       # Database operations
│       ├── exports.py        # Export management
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py       # API routes
│       │   └── blueprints.py   # Blueprint definitions
│       └── utils/
│           ├── __init__.py
│           ├── logger.py       # Logging configuration
│           └── redis_client.py # Redis client setup
├── cli.py                    # CLI commands
├── wsgi.py                   # WSGI entry point
├── requirements.txt          # Dependencies
├── .env.example              # Environment variables template
├── README.md                 # Project documentation
└── pyproject.toml            # Project configuration (provided)

```