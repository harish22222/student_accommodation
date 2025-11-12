from setuptools import setup, find_packages

setup(
    name="studentaccommodationpkg",
    version="0.1.0",
    description="Custom Festival Discount Library for Student Accommodation Project",
    author="Harish K",
    author_email="kharish820414@gmail.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["boto3"],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
)
