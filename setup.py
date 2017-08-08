import os

from distutils.core import setup


def setup_package():
    root = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(root, 'limonado', '__about__.py')) as f:
        about = {}
        exec(f.read(), about)

    with open(os.path.join(root, 'README.rst')) as f:
        readme = f.read()

    setup(
        name="limonado",
        packages=["limonado"],
        package_data={'': ['*.py']},
        description=about['__summary__'],
        long_description=readme,
        keywords=about['__keywords__'],
        author=about['__author__'],
        author_email=about['__email__'],
        version=about['__version__'],
        url=about['__uri__'],
        license=about['__license__'],
        classifiers=[
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Topic :: Internet :: WWW/HTTP",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
        ],
    )


if __name__ == '__main__':
    setup_package()
