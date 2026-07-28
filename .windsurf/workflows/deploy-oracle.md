---
description: Deploy freelance_search Telegram bot to Oracle Cloud Free Tier VM (systemd, always-on)
---

1. Provision an Oracle Cloud Free Tier VM (Ampere A1 or E2.1.Micro, Ubuntu 24.04), note its public IP, open port 22 in the Security List/NSG (no other inbound ports needed — bot only makes outbound HTTPS calls).

Current VM: 158.180.20.184, user `ubuntu`, key `~/Downloads/keys/ssh-key-2026-07-28.key`, Ubuntu 24.04 (Python 3.12.3 preinstalled — deadsnakes PPA not needed, project requires 3.11+, 3.12 is compatible).

2. From local machine, copy the project to the VM (excludes `.venv`, `__pycache__`, `.git` via `.gitignore`-aware rsync):
```
rsync -avz --exclude-from='.gitignore' --exclude='.git' /Users/Vladimir.Glushakov/code/freelance_search/ ubuntu@<VM_IP>:/home/ubuntu/freelance_search/
```

3. Copy `.env` separately (never commit it):
```
scp /Users/Vladimir.Glushakov/code/freelance_search/.env ubuntu@<VM_IP>:/home/ubuntu/freelance_search/.env
```

4. (Optional) Copy `seen_jobs.db` to avoid re-sending already-seen jobs on first run:
```
scp /Users/Vladimir.Glushakov/code/freelance_search/seen_jobs.db ubuntu@<VM_IP>:/home/ubuntu/freelance_search/seen_jobs.db
```

5. SSH into the VM and install venv package (Ubuntu 24.04 ships Python 3.12 by default, which satisfies the project's 3.11+ requirement):
```
ssh -i ~/Downloads/keys/ssh-key-2026-07-28.key ubuntu@<VM_IP>
sudo apt update && sudo apt install -y python3-venv
```

6. Create venv and install dependencies:
```
cd /home/ubuntu/freelance_search
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

7. Install and enable the systemd service (unit file is at `deploy/freelance-bot.service` in the repo):
```
sudo cp deploy/freelance-bot.service /etc/systemd/system/freelance-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now freelance-bot
```

8. Verify it's running and check logs:
```
sudo systemctl status freelance-bot
tail -f /home/ubuntu/freelance_search/bot.log
```

9. To update code later, repeat step 2 (rsync) then `sudo systemctl restart freelance-bot`.

10. To stop local Mac instance once the cloud bot is confirmed working (avoid duplicate Telegram notifications):
```
pkill -f "bot.run_bot"
```
