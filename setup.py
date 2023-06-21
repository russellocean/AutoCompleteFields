from setuptools import find_packages, setup

version = "0.1"

# setup.py
setup(
    name="TracAutocompleteFieldsPlugin",
    version=version,
    description="Autocomplete custom fields like Keywords, Supplier, Customer, and Sizes",
    author="Russell Welch",
    author_email="russellwelch17@gmail.com",
    url="Your project URL",
    keywords="trac plugin",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests*"]),
    include_package_data=True,
    install_requires=["Trac"],
    package_data={
        "autocompletefields": ["htdocs/css/*.css", "htdocs/css/*.gif", "htdocs/js/*.js"]
    },
    zip_safe=False,
    classifiers=[
        "Framework :: Trac",
        "Environment :: Web Environment",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    entry_points="""
    [trac.plugins]
    autocompletefields = autocompletefields.autocompletefields
    """,
)
