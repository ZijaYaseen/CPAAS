# How to Connect WhatsApp to the Platform

This guide walks you through connecting your WhatsApp Business number so customer messages arrive in your inbox and you can reply directly from the platform.

**Time needed:** 20–30 minutes  
**What you need:** A Facebook/Meta account and a phone number

---

## Overview

WhatsApp integration uses **Meta's official WhatsApp Business API**. For testing, Meta provides a free sandbox — no cost, no approval needed.

---

## Part 1 — Create a Meta Developer App

**Step 1.** Go to [developers.facebook.com](https://developers.facebook.com) and sign in with your Facebook account.

**Step 2.** Click **My Apps** (top-right) → **Create App**.

**Step 3.** Select the use case **"Connect with customers through WhatsApp"** → click **Next**.

**Step 4.** Fill in your app name (e.g. `My Business`) and email → click **Create App**.

**Step 5.** You'll land on the app dashboard. Click **"Customize the Connect with customers through WhatsApp use case"**.

**Step 6.** Make sure **"Integrate with API"** is selected → then click **"Step 1. Try it out"** in the left menu.

---

## Part 2 — Get Your Credentials

On the **"Step 1. Try it out"** page you'll find everything you need:

### Phone Number ID
Under the test phone number, you'll see **Phone Number ID** — a long number like `116270875727105`.  
**Copy it.**

### WhatsApp Business Account ID
On the same page, next to the Phone Number ID, you'll see **WhatsApp Business Account ID** — another long number.  
**Copy it.**

### Access Token
Below that, there's a field called **Access Token** showing a long string starting with `EAAB...`.  
**Copy it.**

> **Note:** This token expires in 24 hours — perfect for testing. For production you'll set up a permanent one.

---

## Part 3 — Test That WhatsApp Works

Still on the "Try it out" page:

**Step 1.** In the **"To"** field, enter your personal WhatsApp number in international format (e.g. `+923001234567`).

**Step 2.** Click **Send message** — you'll receive a test message on your WhatsApp from Meta's test number.

This confirms your credentials are correct.

---

## Part 4 — Set Up the Webhook

The webhook tells Meta to forward customer messages to your platform.

**Step 1.** In the left menu, click **"Step 2. Production setup"** → then click **"Configure Webhooks"**.

**Step 2.** Fill in:
- **Callback URL:**  
  *(Copy the Webhook URL from Settings → Channels → Connect WhatsApp in the platform)*
- **Verify Token:** `whatsapp-verify-token`

**Step 3.** Click **Verify and save**. You should see a green success message.

**Step 4.** After saving, find the **Webhook fields** table → click **Subscribe** next to `messages`.

---

## Part 5 — Connect WhatsApp in the Platform

**Step 1.** Go to **Settings → Channels** in the platform.

**Step 2.** Click **Connect WhatsApp**.

**Step 3.** Fill in the form:

| Field | What to enter |
|---|---|
| Channel Name | e.g. `WhatsApp Support` |
| Phone Number ID | From Part 2 |
| WhatsApp Business Account ID | From Part 2 |
| Access Token | The `EAAB...` string from Part 2 |
| App Secret | Optional — found in App Settings → Basic → App Secret |

**Step 4.** Click **Connect WhatsApp**.

The platform automatically activates your webhook in the background — no extra steps needed.

---

## Part 6 — Test End-to-End

**Step 1.** From your personal WhatsApp, send a message **to** the Meta test number (the `+1 555...` number you received a message from in Part 3).

**Step 2.** Within a few seconds, that message should appear as a new conversation in your platform **Inbox**.

**Step 3.** Reply from the inbox — your reply will arrive on the sender's WhatsApp.

---

## For Production (Using Your Real Business Number)

The test setup uses Meta's shared test number. To use your own business number:

1. In your Meta App, go to **WhatsApp → Phone Numbers** → **Add phone number**
2. Enter your business number and verify it via SMS or call
3. Once verified, use that number's **Phone Number ID** when connecting in the platform

> **Important:** A number added to WhatsApp Business API can no longer be used with the regular WhatsApp app. Always use a dedicated business number.

For a permanent Access Token (doesn't expire in 24 hours):
- Go to **Meta Business Settings → System Users** → create a system user → generate a token with `whatsapp_business_messaging` permission.

---

## Troubleshooting

**Webhook verification failed?**
- Make sure you entered `whatsapp-verify-token` exactly (lowercase, with dashes)
- Wait 1 minute and try again

**Messages not appearing in inbox?**
- Make sure `messages` is subscribed in the webhook fields
- In the test environment, only numbers you've added to the allowed list can send messages to the test number

**"Missing WhatsApp credentials" error?**
- Re-enter your credentials in Settings → Channels → Connect WhatsApp

**Access Token expired?**
- Go back to Meta → WhatsApp → API Setup and generate a new token
- For production, use a permanent System User token

---

## What happens after setup

- Customer sends WhatsApp message to your number → appears in inbox instantly
- You reply from the platform → delivered to their WhatsApp
- Works alongside Email and Web Chat in the same unified inbox
