SPOT Installation

SPOT is primarily designed for Linux.

Requirements

A typical installation requires:

* Linux
* Python 3
* Git
* A supported web browser
* systemd for automatic startup

Optional components include:

* Qubes OS
* Whonix
* Tor
* A proxy or VPN
* Container/sandbox support

Clone the Repository

git clone https://github.com/YOUR-USERNAME/SPOT.git
cd SPOT

Create a Virtual Environment

python3 -m venv .venv
source .venv/bin/activate

Install Dependencies

pip install -r requirements.txt

For development:

pip install -r requirements-dev.txt

Install SPOT

If the project uses the Python package configuration:

pip install .

Verify the installation:

spot --version

Configuration

Copy the example configuration:

mkdir -p ~/.config/spot
cp config/spot.example.yaml ~/.config/spot/config.yaml

Review the configuration before starting SPOT.

Optional systemd Startup

SPOT can optionally start automatically when the system boots.

./scripts/setup-systemd.sh

Check the service:

systemctl --user status spot

Qubes OS

Qubes-specific installation instructions are maintained separately in:

docs/qubes-integration.md

Qubes users should review the generated RPC policies before enabling integration.

Uninstalling

Use:

./scripts/uninstall.sh

Review any remaining configuration and persona data before deleting it.