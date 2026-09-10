SPOT/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── AUTHORS.md
├── VERSION
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── .gitignore
├── .editorconfig
│
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   ├── configuration.md
│   ├── quick-start.md
│   ├── user-guide.md
│   ├── security-model.md
│   ├── threat-model.md
│   ├── privacy-model.md
│   ├── personas.md
│   ├── behavior-engine.md
│   ├── activity-engine.md
│   ├── browser-engine.md
│   ├── network-engine.md
│   ├── isolation.md
│   ├── qubes-integration.md
│   ├── whonix-integration.md
│   ├── scheduling.md
│   ├── plugins.md
│   ├── emergency-stop.md
│   ├── logging.md
│   ├── troubleshooting.md
│   └── development.md
│
├── config/
│   ├── spot.example.yaml
│   ├── scheduler.example.yaml
│   ├── network.example.yaml
│   ├── browser.example.yaml
│   ├── safety.example.yaml
│   └── logging.example.yaml
│
├── personalities/
│   ├── README.md
│   ├── templates/
│   │   ├── blank.yaml
│   │   ├── casual-user.yaml
│   │   ├── technology.yaml
│   │   ├── outdoors.yaml
│   │   └── creative.yaml
│   │
│   └── examples/
│       ├── alex.yaml
│       ├── morgan.yaml
│       ├── jordan.yaml
│       └── taylor.yaml
│
├── src/
│   └── spot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── version.py
│       │
│       ├── core/
│       │   ├── engine.py
│       │   ├── controller.py
│       │   ├── session.py
│       │   ├── task.py
│       │   ├── events.py
│       │   ├── state.py
│       │   └── lifecycle.py
│       │
│       ├── personas/
│       │   ├── manager.py
│       │   ├── persona.py
│       │   ├── identity.py
│       │   ├── interests.py
│       │   ├── preferences.py
│       │   ├── demographics.py
│       │   ├── routines.py
│       │   ├── memory.py
│       │   ├── evolution.py
│       │   └── generator.py
│       │
│       ├── behavior/
│       │   ├── engine.py
│       │   ├── model.py
│       │   ├── decision.py
│       │   ├── probability.py
│       │   ├── context.py
│       │   ├── consistency.py
│       │   ├── randomization.py
│       │   └── noise_budget.py
│       │
│       ├── activities/
│       │   ├── manager.py
│       │   ├── search.py
│       │   ├── browsing.py
│       │   ├── news.py
│       │   ├── media.py
│       │   ├── shopping.py
│       │   ├── research.py
│       │   └── dns.py
│       │
│       ├── browser/
│       │   ├── manager.py
│       │   ├── profiles.py
│       │   ├── sessions.py
│       │   ├── automation.py
│       │   ├── cookies.py
│       │   ├── storage.py
│       │   └── fingerprint.py
│       │
│       ├── network/
│       │   ├── manager.py
│       │   ├── routing.py
│       │   ├── proxy.py
│       │   ├── tor.py
│       │   ├── whonix.py
│       │   ├── dns.py
│       │   ├── dns_noise.py
│       │   ├── firewall.py
│       │   ├── kill_switch.py
│       │   └── health.py
│       │
│       ├── isolation/
│       │   ├── manager.py
│       │   ├── filesystem.py
│       │   ├── processes.py
│       │   ├── namespaces.py
│       │   ├── sandbox.py
│       │   ├── containers.py
│       │   └── permissions.py
│       │
│       ├── qubes/
│       │   ├── manager.py
│       │   ├── qubes_rpc.py
│       │   ├── templates.py
│       │   ├── disposable.py
│       │   ├── networking.py
│       │   ├── persona_qubes.py
│       │   └── policies/
│       │       ├── spot.policy
│       │       └── README.md
│       │
│       ├── scheduler/
│       │   ├── scheduler.py
│       │   ├── timers.py
│       │   ├── routines.py
│       │   ├── randomizer.py
│       │   ├── calendar.py
│       │   └── concurrency.py
│       │
│       ├── safety/
│       │   ├── manager.py
│       │   ├── limits.py
│       │   ├── allowlist.py
│       │   ├── blocklist.py
│       │   ├── rate_limit.py
│       │   ├── bandwidth.py
│       │   ├── resource_limits.py
│       │   ├── anomaly_detection.py
│       │   └── emergency_stop.py
│       │
│       ├── storage/
│       │   ├── database.py
│       │   ├── models.py
│       │   ├── encryption.py
│       │   ├── migrations/
│       │   └── backups.py
│       │
│       ├── analytics/
│       │   ├── statistics.py
│       │   ├── activity_report.py
│       │   ├── persona_report.py
│       │   ├── network_report.py
│       │   ├── consistency_report.py
│       │   └── export.py
│       │
│       ├── audit/
│       │   ├── logger.py
│       │   ├── events.py
│       │   ├── audit_log.py
│       │   └── redaction.py
│       │
│       ├── plugins/
│       │   ├── manager.py
│       │   ├── interface.py
│       │   ├── loader.py
│       │   └── registry.py
│       │
│       ├── ui/
│       │   ├── cli.py
│       │   ├── commands.py
│       │   ├── tui.py
│       │   ├── dashboard.py
│       │   └── status.py
│       │
│       └── utils/
│           ├── logging.py
│           ├── validation.py
│           ├── time.py
│           ├── random.py
│           ├── filesystem.py
│           └── system.py
│
├── plugins/
│   ├── README.md
│   │
│   ├── activities/
│   │   ├── search/
│   │   ├── browser/
│   │   ├── news/
│   │   ├── media/
│   │   └── dns/
│   │
│   ├── networking/
│   │   ├── tor/
│   │   ├── whonix/
│   │   └── proxy/
│   │
│   └── platforms/
│       ├── qubes/
│       └── linux/
│
├── systemd/
│   ├── spot.service
│   ├── spot.timer
│   ├── spot-emergency.service
│   └── README.md
│
├── qubes/
│   ├── README.md
│   ├── templates/
│   │   ├── spot-persona-template.xml
│   │   └── spot-disposable-template.xml
│   │
│   ├── services/
│   │   ├── spot-controller
│   │   ├── spot-persona
│   │   └── spot-network
│   │
│   └── policies/
│       ├── spot.policy
│       └── spot-firewall.policy
│
├── scripts/
│   ├── install.sh
│   ├── uninstall.sh
│   ├── update.sh
│   ├── start.sh
│   ├── stop.sh
│   ├── restart.sh
│   ├── status.sh
│   ├── emergency-stop.sh
│   ├── create-persona.sh
│   ├── destroy-persona.sh
│   ├── setup-qubes.sh
│   ├── setup-whonix.sh
│   └── setup-systemd.sh
│
├── tests/
│   ├── unit/
│   │   ├── test_personas.py
│   │   ├── test_behavior.py
│   │   ├── test_scheduler.py
│   │   ├── test_network.py
│   │   ├── test_browser.py
│   │   ├── test_storage.py
│   │   └── test_safety.py
│   │
│   ├── integration/
│   │   ├── test_persona_lifecycle.py
│   │   ├── test_concurrent_personas.py
│   │   ├── test_network_isolation.py
│   │   ├── test_browser_isolation.py
│   │   └── test_emergency_stop.py
│   │
│   └── qubes/
│       ├── test_qube_creation.py
│       ├── test_qube_isolation.py
│       └── test_qubes_networking.py
│
├── examples/
│   ├── basic/
│   │   ├── config.yaml
│   │   └── persona.yaml
│   │
│   ├── multi-persona/
│   │   ├── config.yaml
│   │   ├── persona-01.yaml
│   │   ├── persona-02.yaml
│   │   └── persona-03.yaml
│   │
│   └── qubes/
│       ├── config.yaml
│       └── personas.yaml
│
├── packaging/
│   ├── debian/
│   ├── fedora/
│   ├── arch/
│   ├── appimage/
│   └── flatpak/
│
├── assets/
│   ├── icons/
│   │   ├── spot.svg
│   │   ├── spot-symbol.svg
│   │   └── spot-mono.svg
│   └── screenshots/
│
└── .github/
    ├── workflows/
    │   ├── tests.yml
    │   ├── lint.yml
    │   ├── security.yml
    │   ├── build.yml
    │   └── release.yml
    │
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   ├── feature_request.md
    │   └── security_issue.md
    │
    └── pull_request_template.md