import os
import django # type: ignore
import sys

# Add the project root to sys.path
sys.path.append(r'C:\Users\Lenovo\Downloads\menstrual_irregularity\project1-main\menstrual_irregularity_detection_system-main\period-project-main')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from tracker.models import PendingUser # type: ignore

with open('pending_users_debug.txt', 'w') as f:
    f.write("--- PendingUser Detailed Check ---\n")
    pending = PendingUser.objects.all()
    if not pending:
        f.write("No pending users found.\n")
    else:
        for pu in pending:
            t = pu.verification_token
            f.write(f"User: {pu.username}\n")
            f.write(f"Token: '{t}'\n")
            f.write(f"Length: {len(t)}\n")
            f.write(f"Hex: {t.encode('utf-8').hex()}\n")
            f.write("-" * 20 + "\n")
print("Done. Check pending_users_debug.txt")
