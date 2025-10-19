from setuptools import setup, find_packages

setup(
    name="money-transfer-service",
    version="1.0.0",
    description="Money Transfer Service with Currency Conversion",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "sqlalchemy>=2.0.25",
        "alembic>=1.13.1",
        "asyncpg>=0.29.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "httpx>=0.26.0",
        "aio-pika>=9.4.0",
        "redis>=5.0.1",
        "python-telegram-bot>=20.8",
        "babel>=2.14.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
        ]
    },
)
