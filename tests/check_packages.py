import sys
import subprocess
import pkg_resources

required_packages = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'openpyxl']

def check_package(package):
    try:
        dist = pkg_resources.get_distribution(package)
        print(f"✓ {package} ({dist.version})")
        return True
    except pkg_resources.DistributionNotFound:
        print(f"✗ {package} not installed")
        return False

print("Checking required packages for comparative analysis:")
all_installed = True
for pkg in required_packages:
    if not check_package(pkg):
        all_installed = False

if not all_installed:
    print("\nInstalling missing packages...")
    for pkg in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
            print(f"Installed {pkg}")
        except:
            print(f"Failed to install {pkg}")
else:
    print("\nAll required packages are installed.")