from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Filtrar apenas dependências obrigatórias (remover comentários e linhas vazias)
install_requires = [req for req in requirements if req and not req.startswith("#")]

setup(
    name="pocketoptionapi",
    version="1.0.99",
    author="AdminhuDev",
    author_email="telegram: t.me/devAdminhu",
    description="API Python robusta e moderna para integração com a PocketOption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdminhuDev/pocketoptionapi",
    project_urls={
        "Bug Reports": "https://github.com/AdminhuDev/pocketoptionapi/issues",
        "Source": "https://github.com/AdminhuDev/pocketoptionapi",
        "Documentation": "https://github.com/AdminhuDev/pocketoptionapi#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    keywords="pocketoption trading api websocket financial investment",
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pocketoption-test=pocketoptionapi.teste:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 