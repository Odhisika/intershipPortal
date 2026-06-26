from django.db import migrations


# ---------------------------------------------------------------------------
# Course definitions: each course gets an 8-week curriculum in the same
# style as the original Python & Django roadmap (goal/description +
# weekend milestone per week).
# ---------------------------------------------------------------------------

COURSES = [
    {
        "code": "software_development",
        "name": "Software Development (Python & Django)",
        "description": (
            "An 8-week intensive covering Python fundamentals through to "
            "building, testing, and deploying full-stack Django web "
            "applications, for students who know basic programming but are "
            "new to Python."
        ),
        "weeks": [
            (1, "Python Fundamentals",
             "Get comfortable writing and running Python code, and translate "
             "existing programming knowledge into Python syntax. Covers "
             "variables, data types, operators, strings, control flow, "
             "loops, and functions.",
             "Build a console-based BMI Calculator that takes weight & "
             "height, calculates BMI using a function, and prints a "
             "category using conditionals. Push to GitHub."),

            (2, "Python Intermediate, OOP & Developer Tooling",
             "Move from scripts to structured programs using data "
             "structures, object-oriented design, and professional tooling "
             "(Git, virtual environments).",
             "Build a console-based Inventory Management System using "
             "classes (Product, Inventory) with add/remove/update/search "
             "functionality, file-based persistence (JSON), and proper "
             "error handling. Commit progress in at least 3 separate Git "
             "commits."),

            (3, "Web Foundations & Django Basics",
             "Understand how the web works and build the first Django "
             "project, app, views, URLs, and templates.",
             "Build a personal portfolio website in Django with at least 3 "
             "pages (Home, Projects, Contact), a shared base template, "
             "navigation, and styled with CSS. Deploy locally and demo to "
             "the class."),

            (4, "Models, ORM, Admin & Forms",
             "Persist data using Django's ORM, manage content via the admin "
             "site, and collect user input through forms.",
             "Build a fully working Blog application: list view of posts, "
             "detail view per post, a form to create new posts, and "
             "comments displayed under each post. Data must be stored in "
             "the database and manageable via Django Admin."),

            (5, "Authentication, Class-Based Views & Static/Media Files",
             "Add user accounts, refactor views using Django's generic "
             "class-based views, and handle file uploads.",
             "Upgrade the Blog app: users can register, log in, "
             "create/edit/delete only their own posts, upload a featured "
             "image per post, and the post list is paginated and "
             "searchable."),

            (6, "REST APIs with Django REST Framework",
             "Expose application data as a JSON API so it can be consumed "
             "by mobile apps, JavaScript frontends, or third-party "
             "services.",
             "Add a full REST API to the Blog app covering posts and "
             "comments (list, detail, create, update, delete) with proper "
             "permissions, and a simple JavaScript page that displays posts "
             "fetched from the API."),

            (7, "Testing, Third-Party Integrations & Deployment",
             "Write tests, integrate a real-world payment provider, manage "
             "environment configuration, and deploy a Django app live.",
             "Deploy the Blog application (with authentication, image "
             "uploads, API, and Paystack donation flow) to a live cloud "
             "platform with a working public URL and a Postgres database."),

            (8, "Capstone Project & Presentation",
             "Apply everything learned to design, build, and present an "
             "original Django project end-to-end.",
             "Each student presents a deployed, original Django "
             "application built from scratch during the week, "
             "demonstrating models, views, templates, forms/authentication, "
             "and (where applicable) an API."),
        ],
    },

    {
        "code": "ui_ux_design",
        "name": "UI/UX Design",
        "description": (
            "An 8-week intensive covering design fundamentals, user "
            "research, wireframing, prototyping in Figma, and usability "
            "testing, culminating in a complete case study for a "
            "real-world product."
        ),
        "weeks": [
            (1, "Design Fundamentals & Visual Principles",
             "Build a foundation in design theory: layout, typography, "
             "color theory, contrast, hierarchy, and grid systems. Learn "
             "the difference between UI and UX and how they work together.",
             "Recreate the layout of a well-known app's home screen using "
             "only design principles (grid, spacing, hierarchy) in Figma, "
             "with a short write-up explaining your layout decisions."),

            (2, "Figma Essentials & Design Systems",
             "Master Figma: frames, components, auto layout, styles, and "
             "shared libraries. Introduction to design systems and how "
             "consistent components speed up design work.",
             "Build a small design system in Figma: a color palette, type "
             "scale, button states (default/hover/disabled), input fields, "
             "and at least 5 reusable components."),

            (3, "User Research & Personas",
             "Learn qualitative and quantitative research methods: user "
             "interviews, surveys, competitive analysis, and how to "
             "synthesize findings into personas and problem statements.",
             "Conduct 3-5 informal user interviews about a chosen app idea, "
             "synthesize findings into one persona and one problem "
             "statement, presented as a one-page document."),

            (4, "Information Architecture & Wireframing",
             "Translate research into structure: sitemaps, user flows, and "
             "low-fidelity wireframes. Learn to prioritize content and "
             "navigation before visual design.",
             "Create a sitemap, at least one user flow diagram, and "
             "low-fidelity wireframes (5-8 screens) for an app addressing "
             "the Week 3 problem statement."),

            (5, "High-Fidelity UI Design",
             "Apply visual design skills to turn wireframes into polished, "
             "high-fidelity mockups using the design system from Week 2. "
             "Covers iconography, imagery, and responsive layouts.",
             "Design high-fidelity mockups for all wireframed screens "
             "(desktop and mobile versions of at least 3 key screens), "
             "using consistent components from your design system."),

            (6, "Prototyping & Interaction Design",
             "Build interactive prototypes in Figma: transitions, "
             "micro-interactions, overlays, and smart animate. Learn "
             "principles of motion and feedback in interfaces.",
             "Create a clickable prototype covering the core user flow "
             "from Week 4, with at least 3 micro-interactions (e.g. button "
             "states, transitions, loading states)."),

            (7, "Usability Testing & Iteration",
             "Plan and run usability tests on your prototype, collect "
             "feedback, and iterate on the design based on findings. "
             "Introduction to accessibility (WCAG basics) and handoff to "
             "developers.",
             "Run usability tests with at least 3 participants, document "
             "findings, and produce a revised version of your prototype "
             "addressing the top 3 issues found."),

            (8, "Capstone Case Study & Presentation",
             "Compile the full design process into a polished case study "
             "and present it as a portfolio piece, mirroring a real-world "
             "design presentation to stakeholders.",
             "Each student presents a complete case study (research, "
             "wireframes, high-fidelity designs, prototype, and testing "
             "results) for an original product idea, formatted as a "
             "portfolio-ready presentation."),
        ],
    },

    {
        "code": "networking",
        "name": "Networking",
        "description": (
            "An 8-week intensive covering networking fundamentals, the "
            "OSI/TCP-IP models, subnetting, routing and switching with "
            "Cisco Packet Tracer, wireless networking, and an introduction "
            "to network security and troubleshooting."
        ),
        "weeks": [
            (1, "Networking Fundamentals & the OSI Model",
             "Introduction to networking concepts: what a network is, "
             "network types (LAN/WAN/MAN), the OSI and TCP/IP models, and "
             "how data moves through a network layer by layer.",
             "Create a labeled diagram mapping common devices and "
             "protocols (switch, router, HTTP, TCP, IP, Ethernet) to their "
             "correct OSI layers, with a short explanation for each."),

            (2, "IP Addressing & Subnetting",
             "Deep dive into IPv4 addressing, classes, subnet masks, CIDR "
             "notation, and subnetting calculations. Introduction to IPv6 "
             "basics.",
             "Given a network address and requirements (number of subnets "
             "and hosts), calculate and document a complete subnetting plan "
             "with subnet IDs, ranges, and broadcast addresses."),

            (3, "Network Devices & Cabling",
             "Hands-on with hubs, switches, routers, and access points. "
             "Cable types (UTP, fiber), connectors, and structured cabling "
             "basics. Intro to Cisco Packet Tracer.",
             "Build a simple wired network topology in Packet Tracer with "
             "2 switches, 1 router, and at least 4 end devices, with "
             "correct cabling and IP addressing."),

            (4, "Routing Fundamentals",
             "Static routing, default routes, and an introduction to "
             "dynamic routing protocols (RIP/OSPF basics). Understanding "
             "routing tables and how routers forward packets.",
             "In Packet Tracer, configure static routes between 3 "
             "interconnected networks so that all devices can reach each "
             "other; verify with ping and traceroute."),

            (5, "Switching, VLANs & Spanning Tree",
             "How switches learn MAC addresses, VLAN segmentation for "
             "traffic separation and security, trunking, and an "
             "introduction to Spanning Tree Protocol for loop prevention.",
             "Configure at least 3 VLANs across 2 switches with inter-VLAN "
             "routing via a router, and verify devices in different VLANs "
             "are properly isolated/connected as designed."),

            (6, "Wireless Networking",
             "Wireless standards (Wi-Fi generations), SSIDs, wireless "
             "security (WPA2/WPA3), access point placement, and common "
             "wireless troubleshooting issues.",
             "Design a wireless network plan for a small office (floor "
             "plan with AP placement, SSID/security plan, and channel "
             "assignments to minimize interference)."),

            (7, "Network Security & Access Control Basics",
             "Firewalls, ACLs, NAT/PAT, VPN concepts, and common network "
             "threats (DoS, spoofing, sniffing) and mitigations.",
             "Configure standard and extended ACLs in Packet Tracer to "
             "restrict traffic between specific networks/services, and "
             "configure basic NAT for internet access."),

            (8, "Troubleshooting & Capstone Project",
             "Systematic network troubleshooting methodology, common "
             "diagnostic tools (ping, traceroute, ipconfig, show commands), "
             "and documentation practices.",
             "Each student designs, builds, and documents a complete "
             "network (topology diagram, IP addressing plan, VLANs, "
             "routing, basic security) for a small business scenario, and "
             "presents it including a troubleshooting walkthrough of an "
             "injected fault."),
        ],
    },

    {
        "code": "cybersecurity",
        "name": "Cybersecurity",
        "description": (
            "An 8-week intensive covering security fundamentals, networking "
            "for security, system hardening, ethical hacking basics, web "
            "application security, and incident response, with hands-on "
            "labs throughout."
        ),
        "weeks": [
            (1, "Security Fundamentals & the CIA Triad",
             "Core security concepts: confidentiality, integrity, "
             "availability, threats vs vulnerabilities vs risks, common "
             "attack types, and an overview of security roles and career "
             "paths.",
             "Write a threat model for a simple scenario (e.g. a small "
             "business's customer database), identifying assets, threats, "
             "vulnerabilities, and recommended controls."),

            (2, "Networking for Security & Lab Setup",
             "Refresher on networking concepts relevant to security (ports, "
             "protocols, packet structure). Set up a personal lab using "
             "virtual machines (Kali Linux, a vulnerable target VM).",
             "Set up a working virtual lab (attacker VM + target VM on an "
             "isolated network) and capture/analyze basic traffic with "
             "Wireshark, documenting at least 3 protocols observed."),

            (3, "Linux Fundamentals & Command Line for Security",
             "Essential Linux skills for security work: file system "
             "navigation, permissions, processes, package management, and "
             "common command-line tools used in security assessments.",
             "Complete a set of Linux command-line challenges (file "
             "permissions, user management, process inspection, basic "
             "scripting) and document the commands used and why."),

            (4, "Reconnaissance & Scanning",
             "Information gathering techniques: passive vs active "
             "reconnaissance, OSINT basics, port scanning and service "
             "enumeration with Nmap.",
             "Perform a full reconnaissance and scanning exercise against "
             "the lab target VM using Nmap, producing a report of open "
             "ports, services, and versions identified."),

            (5, "Vulnerability Assessment & Exploitation Basics",
             "Understanding common vulnerabilities (CVE/CVSS), using "
             "vulnerability scanners, and an introduction to exploitation "
             "concepts using a safe, legal lab environment.",
             "Run a vulnerability scan against the lab target, identify the "
             "top 3 vulnerabilities, research their impact, and propose "
             "remediation steps for each."),

            (6, "Web Application Security",
             "Introduction to the OWASP Top 10: SQL injection, XSS, broken "
             "authentication, and other common web vulnerabilities, with "
             "hands-on practice against a deliberately vulnerable web app.",
             "Using a deliberately vulnerable web application (e.g. "
             "DVWA/OWASP Juice Shop), identify and document at least 3 "
             "different vulnerability types with proof-of-concept steps and "
             "fixes."),

            (7, "System Hardening & Defensive Security",
             "Hardening operating systems and applications: patch "
             "management, least privilege, firewalls, antivirus/EDR "
             "concepts, logging, and monitoring basics.",
             "Harden the lab target VM by applying at least 5 hardening "
             "measures (e.g. disabling unused services, configuring a "
             "firewall, enforcing password policy) and re-scan to show "
             "improvement."),

            (8, "Incident Response & Capstone Project",
             "Incident response lifecycle (preparation, detection, "
             "containment, eradication, recovery, lessons learned) and how "
             "to write a security assessment report.",
             "Each student conducts a mini security assessment of the lab "
             "environment end-to-end (recon, scanning, vulnerability "
             "analysis, one exploitation walkthrough, and hardening "
             "recommendations), presented as a professional security "
             "report."),
        ],
    },

    {
        "code": "hardware_repair",
        "name": "Hardware Repair",
        "description": (
            "An 8-week intensive covering computer hardware components, "
            "assembly and disassembly, diagnostics, troubleshooting common "
            "faults, operating system installation, and basic electronic "
            "repair skills."
        ),
        "weeks": [
            (1, "Computer Components & Safety",
             "Identify and understand the function of core components: "
             "motherboard, CPU, RAM, storage drives, PSU, and cooling "
             "systems. Electrical safety and proper handling practices "
             "(ESD precautions).",
             "Create a labeled component identification guide (with photos "
             "or diagrams) for at least 10 internal PC components, "
             "including their function and common failure symptoms."),

            (2, "Assembly & Disassembly",
             "Hands-on practice fully disassembling and reassembling a "
             "desktop PC: cable management, component seating, and "
             "post-assembly POST/boot verification.",
             "Fully disassemble a desktop PC down to bare components, "
             "clean it, reassemble it correctly, and successfully boot to "
             "BIOS/UEFI, documenting each step with photos."),

            (3, "Power Supplies & Diagnostics Tools",
             "Understanding PSU ratings and connectors, using a "
             "multimeter for basic voltage checks, and common diagnostic "
             "tools (POST cards, diagnostic LEDs/beep codes).",
             "Use a multimeter to test PSU output voltages on multiple "
             "rails and document whether they're within acceptable "
             "tolerance, plus interpret at least 3 different beep code "
             "scenarios."),

            (4, "Storage Devices & Data Recovery Basics",
             "HDD vs SSD vs NVMe, common storage failure symptoms, basic "
             "data backup strategies, and an introduction to data recovery "
             "tools for accidentally deleted files.",
             "Set up a backup routine for a sample system, simulate a file "
             "deletion, and successfully recover the file using a free "
             "recovery tool, documenting the process."),

            (5, "Operating System Installation & Troubleshooting",
             "Installing Windows and a Linux distribution from scratch "
             "(BIOS/UEFI setup, partitioning, driver installation), and "
             "troubleshooting common boot and OS issues.",
             "Perform a clean OS installation (Windows or Linux) on a test "
             "machine or VM, install essential drivers/updates, and "
             "document a troubleshooting guide for 3 common boot issues."),

            (6, "Laptop Repair & Component-Level Troubleshooting",
             "Laptop-specific challenges: disassembly differences, battery "
             "and charging issues, screen/keyboard replacement basics, and "
             "common laptop failure patterns.",
             "Disassemble a laptop (or use detailed teardown guides) to "
             "identify and document the location and replacement procedure "
             "for the battery, RAM, storage, and keyboard."),

            (7, "Basic Electronics & Soldering",
             "Introduction to basic electronic components (resistors, "
             "capacitors, diodes), reading simple circuit diagrams, and "
             "soldering/desoldering practice on a practice board.",
             "Complete a basic soldering practice kit (e.g. a simple LED "
             "circuit), demonstrating clean solder joints and a working "
             "circuit, with photos of before/after."),

            (8, "Diagnostics Workflow & Capstone Project",
             "Building a systematic hardware troubleshooting workflow: "
             "intake, symptom analysis, isolation testing, repair, and "
             "verification. Customer communication basics for repair "
             "shops.",
             "Each student receives a PC/laptop with an injected fault, "
             "diagnoses and repairs it using a documented troubleshooting "
             "workflow, and presents a repair report including root cause, "
             "steps taken, and verification of the fix."),
        ],
    },

    {
        "code": "it_support",
        "name": "IT Support",
        "description": (
            "An 8-week intensive covering help desk fundamentals, "
            "operating systems support (Windows/Linux), networking "
            "basics, Active Directory/user management, remote support "
            "tools, and customer service best practices for IT "
            "professionals."
        ),
        "weeks": [
            (1, "IT Support Fundamentals & Ticketing",
             "Role of an IT support technician, support tiers (Tier 1-3), "
             "ITIL basics (incidents vs requests vs problems), and using a "
             "helpdesk ticketing system to log and track issues.",
             "Set up a free/trial ticketing system, log 5 realistic sample "
             "tickets with proper categorization, priority, and "
             "resolution notes."),

            (2, "Windows Operating System Support",
             "Windows administration essentials: user accounts, file "
             "permissions, Control Panel/Settings, Task Manager, Event "
             "Viewer, and common Windows troubleshooting scenarios.",
             "Diagnose and resolve 3 simulated Windows issues (e.g. slow "
             "startup, application crash, permission error) using built-in "
             "tools, documenting the steps taken for each."),

            (3, "Hardware & Peripheral Support",
             "Common hardware troubleshooting for end-user devices: "
             "printers, monitors, peripherals, drivers, and basic "
             "internal component checks (RAM, storage).",
             "Create a troubleshooting flowchart for 'computer won't turn "
             "on' and 'printer not printing' scenarios, covering at least 5 "
             "diagnostic steps each."),

            (4, "Networking Basics for Support Technicians",
             "IP addressing basics, connecting devices to networks, "
             "Wi-Fi troubleshooting, common connectivity tools (ipconfig, "
             "ping, nslookup), and VPN basics for remote workers.",
             "Diagnose 3 simulated connectivity issues (no internet, can "
             "connect to LAN but not internet, intermittent Wi-Fi) using "
             "command-line tools, documenting findings and fixes."),

            (5, "User & Access Management (Active Directory Basics)",
             "Introduction to Active Directory concepts: users, groups, "
             "organizational units, group policy basics, and password "
             "reset/account lockout procedures.",
             "In a lab AD environment (or simulation), create users and "
             "groups, set appropriate permissions on a shared folder, and "
             "document the steps for resetting a locked-out user's "
             "password."),

            (6, "Remote Support Tools & Linux Basics for Support",
             "Using remote desktop/remote support tools (e.g. "
             "TeamViewer/AnyDesk/RDP) professionally, plus essential Linux "
             "command-line basics for supporting Linux-based systems.",
             "Conduct a simulated remote support session (with a "
             "classmate) to resolve an issue using a remote tool, and "
             "complete a set of basic Linux command-line tasks (navigate "
             "filesystem, check disk usage, view running processes)."),

            (7, "Cybersecurity Awareness for Support Staff",
             "Phishing awareness, password hygiene, malware basics, safe "
             "browsing practices, and the support technician's role in an "
             "organization's overall security posture.",
             "Create a one-page security awareness guide for end users "
             "covering phishing red flags, password best practices, and "
             "what to do if they suspect a security incident."),

            (8, "Customer Service Skills & Capstone Project",
             "Communication skills for IT support: active listening, "
             "managing difficult users, setting expectations, and writing "
             "clear documentation/knowledge base articles.",
             "Each student handles a set of simulated support scenarios "
             "(via ticket + roleplay call), resolving the issues and "
             "writing up 2 knowledge base articles based on the most common "
             "issues encountered during the programme."),
        ],
    },
]


def seed_courses(apps, schema_editor):
    Course = apps.get_model('core', 'Course')
    CurriculumWeek = apps.get_model('core', 'CurriculumWeek')

    for course_data in COURSES:
        course, _ = Course.objects.update_or_create(
            code=course_data["code"],
            defaults={
                "name": course_data["name"],
                "description": course_data["description"],
                "duration_weeks": len(course_data["weeks"]),
                "is_active": True,
            },
        )

        for week_number, title, description, milestone in course_data["weeks"]:
            CurriculumWeek.objects.update_or_create(
                course=course,
                week_number=week_number,
                defaults={
                    "title": title,
                    "description": description,
                    "milestone": milestone,
                },
            )


def unseed_courses(apps, schema_editor):
    Course = apps.get_model('core', 'Course')
    Course.objects.filter(
        code__in=[c["code"] for c in COURSES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_courses, unseed_courses),
    ]
