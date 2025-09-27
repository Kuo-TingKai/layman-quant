"""
Setup script for the quantitative trading system
量化交易系統安裝腳本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="quant-trading-system",
    version="1.0.0",
    author="Quant Trading Team",
    author_email="quant@example.com",
    description="A quantitative trading system designed for retail traders with limited budgets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/quant-trading-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "quant-backtest=run_backtest:main",
            "quant-live=run_live:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
