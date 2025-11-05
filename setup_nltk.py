"""Setup script to download required NLTK data."""
import nltk
import sys

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading required NLTK data...")

    packages = [
        'stopwords',
        'punkt',
        'averaged_perceptron_tagger'
    ]

    for package in packages:
        try:
            print(f"  Downloading {package}...")
            nltk.download(package, quiet=True)
            print(f"  ✓ {package} downloaded")
        except Exception as e:
            print(f"  ✗ Failed to download {package}: {e}")
            return False

    print("\n✓ All NLTK data downloaded successfully!")
    return True

if __name__ == "__main__":
    success = download_nltk_data()
    sys.exit(0 if success else 1)
