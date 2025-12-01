from setuptools import setup, find_packages

# --- Function to read dependencies from requirements.txt ---
def get_requirements(filename):
    """
    Reads the list of dependencies from the requirements file, 
    excluding comments and empty lines.
    """
    with open(filename, 'r') as f:
        # Filter out comments and empty lines
        lines = f.readlines()
        dependencies = [
            line.strip() for line in lines 
            if line.strip() and not line.strip().startswith('') and not line.strip().startswith('#') 
        ]
        return dependencies

# Define the installation requirements by calling the function
INSTALL_REQUIRES = get_requirements('requirements.txt')

# Define optional/development requirements (you can separate these later if needed)
# For now, we will include all requirements as install_requires for simplicity.
# If you only want core dependencies, you'll need to manually split requirements.txt.


setup(
    # Project Name (must be unique on PyPI)
    name='mediassist-ai', 
    
    # Version (Crucial for a new release!)
    version='0.2.0', 
    
    # Metadata from your README
    description='AI-Powered Healthcare Q&A System Using RAG, ChromaDB & Gemini AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Om Thaware',
    author_email='omthaware@example.com',
    url='https://github.com/OmThawaregitgub/MediAssist-AI', 
    license='MIT',
    
    # Find all packages in your project
    packages=find_packages(),
    
    # The key change: dependencies are read directly from the file
    install_requires=INSTALL_REQUIRES,
    
    # Development dependencies are often listed separately
    # If your requirements.txt lists development dependencies (like black, pytest) 
    # and you don't want them installed by default, you must manually 
    # remove them from the 'INSTALL_REQUIRES' list above.
    # We'll leave them in 'install_requires' for now as they are mixed in the file.

    # Classifiers
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering :: Medical Science RAG',
    ],
    
    python_requires='>=3.9',
)