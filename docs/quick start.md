SPOT Quick Start

This guide demonstrates a basic SPOT installation.

1. Install SPOT

Clone the repository and install the application:

git clone https://github.com/YOUR-USERNAME/SPOT.git
cd SPOT
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install .

2. Create Configuration

mkdir -p ~/.config/spot
cp config/spot.example.yaml ~/.config/spot/config.yaml

Validate it:

spot config validate

3. Create a Persona

Create a new persona from a template:

spot persona create

Or create one from an example:

spot persona create --template technology

List available personas:

spot persona list

4. Check SPOT

spot status

You should see the application state and configured personas.

5. Start SPOT

spot start

Check the status again:

spot status

6. Run Multiple Personas

If multiple personas are configured:

spot start --all

SPOT’s scheduler can manage multiple personas concurrently while maintaining their individual configuration and state.

7. Stop SPOT

spot stop

8. Emergency Stop

If SPOT needs to stop immediately:

spot emergency-stop

This should stop active sessions and scheduled activity as quickly as possible.

9. Automatic Startup

Once SPOT has been configured and tested manually, optional systemd integration can be enabled:

./scripts/setup-systemd.sh

Then check:

systemctl --user status spot

Basic Workflow

Install SPOT
     |
     v
Configure SPOT
     |
     v
Create Personas
     |
     v
Validate Configuration
     |
     v
Start SPOT
     |
     v
Scheduler
     |
     +---- Persona 01
     |
     +---- Persona 02
     |
     +---- Persona 03
     |
     v
Stop / Emergency Stop

Next Steps

After completing the quick start, see:

* docs/architecture.md
* docs/configuration.md
* docs/security-model.md
* docs/personas.md
* docs/networking.md
* docs/qubes-integration.md