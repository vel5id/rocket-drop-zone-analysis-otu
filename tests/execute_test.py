import subprocess
import sys
import os

print("Executing test of Task 5.2 components...")
print("=" * 60)

# Run the test script
result = subprocess.run([sys.executable, "test_run_worked_example.py"], 
                       capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nReturn code: {result.returncode}")

# Check if output files were created
output_dir = "outputs/economic"
if os.path.exists(output_dir):
    print(f"\nFiles in {output_dir}:")
    for file in os.listdir(output_dir):
        print(f"  - {file}")
else:
    print(f"\nOutput directory {output_dir} does not exist.")

if result.returncode == 0:
    print("\n✅ Test completed successfully!")
else:
    print("\n❌ Test failed!")