A lightweight, invite-only task manager for small teams on the same Wi-Fi. Members sign in (admin-approved, optional join code), elect a leader, get weekly tasks, and earn points & stars. Built with Django + HTMX for a snappy, dynamic UI and minimal JavaScript—perfect for running locally with SQLite and sharing over LAN.

✨ Features
	•	Access & Profiles
	•	Invite-only signup with admin approval + optional join code rotation
	•	Profile page with avatar upload (JPEG/PNG, ≤ 2 MB; auto-crop to square)
	•	Leader Elections
	•	One-day default or custom window (start/end), change vote until close
	•	Tie-breaker: earliest last vote
	•	Admins & current leader can be candidates; manual first-leader setup
	•	Tasks & Workflow (Mon–Sun week)
	•	Multi-member tasks with due dates; leader can self-assign
	•	Member clicks Mark Complete → Leader approves (no evidence required)
	•	Live countdown per task; completion auto-disabled at deadline
	•	-10 points once if overdue; +10 on approval; +2 per star
	•	Board lanes with internal scroll: Assigned / Submitted / Done / Incompleted
	•	Fun UX: success messages + small confetti bursts on approvals
	•	Leaderboards & History
	•	Weekly highlights (Top Stars) and a global leaderboard (member, total points, last task, last points, when)
	•	Tasks History page with pagination: who did what, approved by whom, and timestamps

🧱 Tech Stack
	•	Django 5, HTMX, SQLite, vanilla JS (with canvas-confetti), simple CSS
	•	Target: run on laptop, share on LAN (no cloud dependencies)

🔧 Requirements
	•	Python 3.10+
	•	macOS/Linux/Windows
	•	(Optional) pipx or virtualenv

🧭 App Tour
	•	Home (Board): / — Assigned / Submitted / Done / Incompleted (scrollable lanes)
	•	Elections: /elections/ — create/manage elections (leader can adjust)
	•	Admin Panel: /core/admin-panel/ — approve users, rotate join code, set first leader
	•	Profile: /accounts/profile/ — avatar upload, points, stars
	•	Tasks History: /tasksapp/history/ — full audit trail with pagination
	•	Auth: /accounts/signup/, /accounts/login/, /accounts/logout/

🪄 Workflow Details
	•	Points & Stars: +10 on approved assignment; -10 once if deadline missed; +2 per star
	•	Countdown & Deadline: task card shows a live timer; “Mark Complete” auto-disables when time is up
	•	Overdue Handling: overdue items move to Incompleted; penalties applied server-side (once per assignment)
	•	Leader Controls: leader/admin can assign tasks (including to self) and approve submissions

🗂️ Data & Files
	•	Database: db.sqlite3 (default)
	•	Media uploads: user avatars (max 2 MB; JPEG/PNG)
	•	Backups: stop the server, copy db.sqlite3 and media/

🧩 Troubleshooting
	•	Invalid HTTP_HOST / DisallowedHost: add your LAN IP to ALLOWED_HOSTS
	•	CSRF errors on forms: add http://<LAN-IP>:8000 to CSRF_TRUSTED_ORIGINS
	•	Missing tables: run python manage.py migrate
	•	Avatars not showing: ensure MEDIA_URL/MEDIA_ROOT are set and your templates use {{ user.profile.avatar.url }} with {% load static %} as needed

🛣️ Roadmap
	•	Election calendar widget (enhanced date/time pickers)
	•	Filters & search on Tasks History (by status/assignee)
	•	Optional data archival helpers for old records

🤝 Contributing

Issues and PRs welcome! Keep changes small and focused; include screenshots for UI tweaks.

📜 License

MIT — see LICENSE.
