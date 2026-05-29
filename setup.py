"""
MarkView-Pro - setup.py 安装配置。

使用 setuptools 构建和安装 MarkView-Pro 包。
"""

from setuptools import setup, find_packages

# 读取 README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# 读取版本
about: dict = {}
with open("markview_pro/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, about)
            break

setup(
    name="markview-pro",
    version=about.get("__version__", "1.0.0"),
    description="轻量级终端Markdown实时预览与智能格式化引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MarkView-Pro Team",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "markview=markview_pro.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    project_urls={
        "Homepage": "https://github.com/markview-pro/markview-pro",
        "Bug Reports": "https://github.com/markview-pro/markview-pro/issues",
        "Source": "https://github.com/markview-pro/markview-pro",
    },
)
