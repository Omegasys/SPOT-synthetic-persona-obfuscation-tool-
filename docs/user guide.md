# SPOT User Guide

SPOT (Synthetic Persona Obfuscation Tool) is a Linux application for creating and managing isolated synthetic personas and generating controlled synthetic activity.

SPOT is designed to keep synthetic activity separated from the user's real identity, real browser profiles, credentials, and personal data.

---

## 1. Basic Concepts

SPOT is built around several main concepts.

### Persona

A persona is a synthetic user profile.

A persona can contain:

- Name
- Interests
- Preferences
- Demographic attributes
- Activity preferences
- Daily routines
- Browser profile
- Synthetic memory
- Behavioral characteristics
- Scheduling rules

Personas should contain synthetic information only.

Do not import:

- Real passwords
- Real authentication cookies
- Personal browser profiles
- Banking information
- Private messages
- Personal documents
- Authentication tokens
- Other sensitive credentials

---

## 2. Creating a Persona

Create a basic persona:

```bash
spot persona create
