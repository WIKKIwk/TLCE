from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="titan_telegram",
    version="1.0.0",
    description="Telegram Bot Integration for Titan Warehouse System",
    author="Accord Team",
    author_email="dev@accord.uz",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
