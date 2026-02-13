print("Test 1")
import sys
print("Test 2", file=sys.stderr)
sys.stdout.flush()
sys.stderr.flush()
print("Test 3")
