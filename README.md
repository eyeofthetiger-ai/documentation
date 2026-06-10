# EyeOfTheTiger Documentation

EyeOfTheTiger is an AI-ready camera that lets AI assistants capture images,
describe scenes, detect motion, and trigger actions. There are two ways to use
it, depending on how much control you want and where your AI agents run.

---

## Quick Start

We recommend starting with **local** — it's free to prototype and quick to get set up.

1. **Plug in your Eye of the Tiger** and wait for it to boot.
2. **Open `eyeofthetiger.local/setup`** in your browser to select your Wi-Fi network.
3. **Choose an integration** to get going.

Once you're up and running, head to the [local documentation](local/README.md) for
integration guides and examples. When you're ready to access your camera remotely,
the [cloud documentation](cloud/README.md) covers everything you need.

---

## Local

Your camera and your AI agent are on the same network. The agent talks directly
to the camera over HTTP or MCP — no cloud, no middleman, no account required.

**Pros**
- Free forever — no subscription, no usage limits
- Complete control over your data; images never leave your network
- Works without an internet connection
- Lower latency — direct LAN connection to the camera

**Cons**
- Your agent must be on the same network as the camera (or connected via VPN)
- No remote access out of the box
- You manage your own infrastructure

→ **[Local documentation](local/README.md)**

---

## Cloud

Your camera connects outbound to the EyeOfTheTiger platform. Your AI agents
connect to the platform from anywhere — no VPN, no port-forwarding, no local
setup beyond the camera itself.

**Pros**
- Access your camera from anywhere in the world
- Works with any AI client that supports HTTP or MCP (Claude Desktop, Cursor, etc.)
- No local agent infrastructure to manage
- REST API and hosted MCP server included

**Cons**
- Requires an internet connection on the camera
- Your plan includes free usage with your EyeOfTheTiger device, but continued
  use beyond the free allowance requires a subscription
- Images pass through the EyeOfTheTiger platform on the way to your agent

→ **[Cloud documentation](cloud/README.md)**
