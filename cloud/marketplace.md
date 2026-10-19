# Marketplace: install, pay for, and publish apps

The portal's **Marketplace** lists apps you can add to your EOT-1 with a
couple of clicks: apps made by EyeOfTheTiger, and apps other people have
built and published. This guide covers:

1. [Installing an app from the Marketplace](#install-an-app-from-the-marketplace)
2. [Credits: how apps are paid for](#credits-how-apps-are-paid-for)
3. [Publishing your own app](#publish-your-own-app)

New to apps? [Apps](../local/apps/README.md) explains what they are and where
they run. If you want to run code on your own EOT-1 without publishing it,
you don't need the Marketplace: see
[Build an app that runs on your EOT-1](../local/apps/README.md#build-an-app-that-runs-on-your-eot-1)
to install straight from a manifest.

## Install an app from the Marketplace

You need an EyeOfTheTiger account with at least one EOT-1 added to it.

1. Sign in at [platform.eyeofthetiger.ai](https://platform.eyeofthetiger.ai)
   and click **Marketplace** in the top bar.
2. Find the app. Each tile shows its logo, name, maker and price. To search,
   tap the magnifying glass at the top left of the list and type a name,
   maker or description.
3. Click the tile to open the app's page. It shows what the app does, who
   made it, where it runs (on your EOT-1 or in the cloud) and what it costs.
4. Click **Install** (free apps) or **Buy £X** (paid apps). A list of your
   EOT-1s appears.
5. Pick the EOT-1 you want the app on:
   - **Free app:** click **Install here** next to that EOT-1.
   - **Paid app:** click **Buy for this EOT-1**, then confirm. The price comes
     out of your [credits](#credits-how-apps-are-paid-for). If you don't have
     enough, a **Top up credits** link takes you to the Credits page and
     brings you back afterwards.
6. You land on that EOT-1's page with the app's install form open. The
   **Name** is filled in for you (change it if you want two copies on one
   EOT-1) and the **Port** is fixed by the app. Click **Install**.
7. The app appears in the EOT-1's apps list as it starts. From there you can
   **Open** it (if it has its own page), **Start**, **Stop**, view **Logs** or
   **Delete** it.

**To check that apps work on your account**, install **Hello, world - test
app** and click **Open** next to it. You should see your EOT-1's live stream
with "Hello, world." written over it. It runs on the cheapest cloud size, so
stop it when you're done.

You can also install from an EOT-1's own page: its apps section lists the
Marketplace apps, and **Buy** and **Install** work the same way there.

Things to know:

- **Purchases are per EOT-1.** Buying an app for one EOT-1 doesn't cover your
  others. Once bought, you can uninstall and reinstall it on that EOT-1
  without paying again.
- **Bundles** install several apps together. A bundle's price is the sum of
  its apps' prices. If a bundle includes a paid app, buy that app first from
  its own page, then install the bundle.
- **Apps that run on your EOT-1** need its apps platform switched on. If it's
  off, the install form tells you and lets you turn it on.
- **Apps that run in the cloud** need credits above £0 to install or start,
  because they're charged per hour while they run.

## Credits: how apps are paid for

Everything in the Marketplace is paid for from your organisation's prepaid
credits. Open them from the gear menu → **Credits**.

- **Top up** with £10, £25 or £50, or type another amount (at least £5).
  You pay by card on a Stripe checkout page, and the credits appear as soon
  as you return.
- **App purchases** (one-off prices) come out of your credits when you buy.
- **Cloud apps** are charged per hour while they're running, in small
  amounts every few minutes. Stopping an app stops the charges. The per-hour
  price is on each app's tile and page, and follows Google Cloud's current
  prices for the resources the app uses.
- **When credits reach £0, your cloud apps stop.** Top up, then start them
  again from the EOT-1's page. Apps running on your EOT-1 itself aren't
  affected.
- **Auto top-up** is off by default, so nothing is charged without you. To
  use it, tick **Save this card for auto top-up** when you next top up, then
  under **Auto top-up** tick **Top up automatically** and set "when credits
  fall below £X, add £Y". If an automatic charge fails, the Credits page
  tells you why.
- **History** on the Credits page lists every top-up, purchase and runtime
  charge with your balance after each one.
- All prices include VAT. Credits don't expire and aren't refundable.

## Publish your own app

Anyone with an account can submit an app to the Marketplace. Submitted apps run
**in the cloud** (on Google Cloud Run), attached to the customer's EOT-1
through the platform's API. They can't run on the EOT-1 itself yet.

### 1. Build a container that follows the cloud app contract

Your app is a Docker image that EyeOfTheTiger builds from your GitHub
repository. It must:

- **Have a `Dockerfile` at the root of the repository.** We run
  `docker build` on the repository root, nothing else.
- **Serve HTTP on one port** (1024 to 65535). You enter the port when you
  submit, and Cloud Run also passes it to your container as `$PORT`. If
  nothing listens on it, the install never finishes.
- **Expose `GET /status`** returning JSON about how the app is doing.
- **Use the environment variables the platform sets** to reach the
  customer's EOT-1:

  | Variable | What it is |
  |---|---|
  | `CAMERA_API_URL` | The platform's base URL, e.g. `https://platform.eyeofthetiger.ai` |
  | `CAMERA_API_KEY` | An API key for the customer's EOT-1, sent as the `x-api-key` header |
  | `CAMERA_ID` | The EOT-1 your app was installed for, e.g. `eot-a3f9c2d1` |
  | `APP_NAME` | The name the customer installed your app under |
  | `EMBED_TOKEN_SECRET` | Secret for checking the token on page visits (see below) |

  With these, your app calls the same API described in
  [Connect to the Portal](connect-to-portal.md), for example
  `GET $CAMERA_API_URL/api/v1/cameras/$CAMERA_ID/snapshot`.
- **Send your own `User-Agent` header on API calls**, e.g. `my-app/1.0`.
  The platform's firewall blocks Python's default `Python-urllib` user agent
  with a 403. Other HTTP libraries' defaults get through.
- **Connect to the platform over IPv4.** From Cloud Run, connections to the
  platform's IPv6 addresses sometimes hang until they time out. The template
  resolves IPv4 addresses only (see the top of its `app.py`).
- **Keep its own data elsewhere if it needs to persist anything.** The
  container's disk is wiped whenever the app stops.

**If your app serves its own web page**, clicking **Open** in the portal
starts the EOT-1's live stream and opens your app in a new tab. Your app's address is
reachable from the internet, so it must check the token the portal adds to
the URL (`?token=...`) on every request except a health check. The token is
`<payload>.<signature>`: the payload is base64url JSON
`{"cameraId", "name", "exp"}` (`exp` in milliseconds), and the signature is
the base64url HMAC-SHA256 of the payload string using `EMBED_TOKEN_SECRET`
(both without `=` padding). Accept it only if the signature matches, `exp`
is in the future, `cameraId` equals `CAMERA_ID` and `name` equals
`APP_NAME`. In Python:

```python
import base64, hashlib, hmac, json, os, time

def token_ok(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    payload_b64, _, sig = token.partition(".")
    expected = base64.urlsafe_b64encode(
        hmac.new(os.environ["EMBED_TOKEN_SECRET"].encode(), payload_b64.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    if not hmac.compare_digest(sig, expected):
        return False
    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)))
    return (payload.get("exp", 0) > time.time() * 1000
            and payload.get("cameraId") == os.environ["CAMERA_ID"]
            and payload.get("name") == os.environ["APP_NAME"])
```

### 2. Start from the example

[eyeofthetiger-ai/hello-world-app](https://github.com/eyeofthetiger-ai/hello-world-app)
is a complete app to copy: it shows the customer's live stream with "Hello,
world." over it, checks the token, and keeps the API key on the server. It's
the **Hello, world - test app** in the Marketplace, and uses only Python's
standard library.

1. On GitHub, open
   [hello-world-app](https://github.com/eyeofthetiger-ai/hello-world-app),
   click **Use this template** → **Create a new repository**, and make it
   **public**.
2. Try it locally with an API key from the portal (gear menu → **API keys**)
   and one of your EOT-1 ids. Without `EMBED_TOKEN_SECRET` the token check is
   off.

   ```bash
   docker build -t my-app .
   docker run --rm -p 8080:8080 \
     -e CAMERA_API_URL=https://platform.eyeofthetiger.ai \
     -e CAMERA_API_KEY=YOUR_API_KEY \
     -e CAMERA_ID=eot-a3f9c2d1 \
     my-app
   ```

   Start a live stream from your EOT-1's page in the portal, then open
   http://localhost:8080. You should see the stream with "Hello, world." on
   it.
3. Change it to do what your app should do, keeping the token check,
   `/status` and the `Dockerfile`. Run its tests with
   `python -m unittest test_app`, then push to GitHub.

### 3. Submit it

1. In the portal, click **Marketplace**, then the **Submit your own** tile
   at the end of the apps.
2. Fill in the form:

   | Field | What to enter |
   |---|---|
   | **App name** | What customers see, up to 63 characters. The install name is made from it. |
   | **Description** | What the app does, up to 500 characters. Say what data it sends where. |
   | **Maker name** | Your name or company, shown on the tile. |
   | **Public GitHub repository** | e.g. `https://github.com/you/your-app` |
   | **Branch, tag or commit** | Optional. Blank means the default branch. |
   | **Port your container listens on** | The port from step 1 (the template uses 8080). |
   | **Resources** | `cpu-tiny` (1 vCPU, 512 MiB), `cpu-small` (2 vCPU, 4 GiB) or `gpu-l4` (4 vCPU, 16 GiB, NVIDIA L4 GPU). Customers pay for these per hour while your app runs, so pick the smallest that works. |
   | **Price customers pay, one-off** | In pounds, including VAT. Leave blank for free. The minimum is £0.30. |
   | **Logo** | Optional. PNG, JPEG or WebP, up to 256 KB, ideally square. Without one, the tile shows your app's first letter. |
   | **My app serves its own web page** | Tick if customers should be able to **Open** it (see the token check above). |

3. Click **Submit for review**.

We build the exact commit your branch or tag points to at that moment.
Pushing to the repository afterwards doesn't change a submission. You can
submit up to 5 apps a day.

### 4. Pricing: what you receive

You set the price the customer pays. It includes 20% VAT and EyeOfTheTiger's
cut, which is 20% of the price before VAT. The form shows what you receive
as you type. For example, at **£6.00**:

| | |
|---|---|
| VAT (20%) | £1.00 |
| EyeOfTheTiger's 20% of the £5.00 pre-VAT price | £1.00 |
| **You receive** | **£4.00** |

The per-hour cloud runtime is charged to the customer separately and goes to
EyeOfTheTiger to cover hosting. You only earn from the one-off price.

### 5. Review and publishing

Your submission appears under **Your submissions** on the same page, with a
status:

| Status | Meaning |
|---|---|
| **Building** | We're building your image in an isolated environment. This takes a few minutes. |
| **Build failed** | The `docker build` failed. The error is shown; fix it and submit again. |
| **Awaiting review** | Built. An EyeOfTheTiger admin is reviewing it. |
| **Publishing** | Approved, and being added to the Marketplace. |
| **Published** | Live in the Marketplace for every EOT-1 owner. |
| **Not approved** | Rejected. The reason is shown, and also emailed to you. |

While your image builds, Claude reads (never runs) your source code and
writes a report for the reviewer: what the app really does, every place it
sends data, and anything that looks risky. The report is advice: a person
at EyeOfTheTiger always makes the decision. Apps are most likely to be
turned down when they:

- send camera images, video or the API key anywhere the description doesn't
  mention,
- download and run code after they've started,
- contain obfuscated code or do something other than what's described,
- serve a page without checking the embed token.

You get an email when your app is published or turned down.

### Current limits

- Repositories must be public.
- Submitted apps run in the cloud only, not on the EOT-1.
- Payouts to makers aren't automated yet. We record your share of every
  sale and contact you about your earnings.
- A published app can't be updated in place yet. Submitting a new version
  creates a new listing, so contact us if you want one replaced.
