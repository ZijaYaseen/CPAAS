# How to Connect Your Email to the Platform

This guide walks you through connecting your Gmail account so you can **receive and reply to customer emails** directly from your inbox — no switching tabs, no forwarding.

**Time needed:** ~10 minutes  
**What you need:** A Gmail account

---

## Overview

Connecting email involves two things:

1. **Sending replies** — so when you reply to a customer, it goes from your Gmail
2. **Receiving messages** — so when a customer emails you, it shows up in your inbox here

---

## Part 1 — Create a Gmail App Password

Gmail requires a special password for third-party apps. You'll need this to let the platform send emails on your behalf.

**Step 1.** Go to [myaccount.google.com](https://myaccount.google.com) and sign in with your Gmail.

**Step 2.** Click **Security** in the left menu.

**Step 3.** Under "How you sign in to Google", click **2-Step Verification** and turn it on if it's off. (This is required for App Passwords to work.)

**Step 4.** Once 2-Step Verification is on, go back to Security and search for **App passwords** in the search bar at the top, or scroll down to find it.

**Step 5.** Click **App passwords**, then:
- Under "Select app" choose **Mail**
- Under "Select device" choose **Other** and type a name like `My Platform`
- Click **Generate**

**Step 6.** A 16-character password will appear (e.g., `abcd efgh ijkl mnop`). **Copy it now** — it won't be shown again.

> **Tip:** Spaces don't matter. You can copy it with or without spaces.

---

## Part 2 — Connect Email in Settings

**Step 1.** In the platform, go to **Settings → Channels**.

**Step 2.** Click **Connect Email**.

**Step 3.** Fill in the form:

| Field | What to enter |
|---|---|
| Channel Name | Anything you like, e.g. `Support Email` |
| Your Email Address | Your Gmail, e.g. `support@gmail.com` |
| SMTP Host | `smtp.gmail.com` |
| SMTP Port | `587` |
| SMTP Username | Same as Your Email Address |
| SMTP Password | The 16-character App Password from Part 1 |

**Step 4.** Click **Connect**. You'll see a success message with your **Webhook URL** — copy it, you'll need it in the next step.

---

## Part 3 — Set Up Email Receiving (Cloudmailin)

This step connects your Gmail to the platform so incoming emails show up in your inbox here.

**Step 1.** Go to [cloudmailin.com](https://www.cloudmailin.com) and create a free account.

**Step 2.** After signing in, click **Add Address**.

**Step 3.** In the **Target URL** field, paste the Webhook URL you copied from the platform in Part 2.

**Step 4.** Under **Format**, select **Multipart - Normalized**.

**Step 5.** Click **Create**. Cloudmailin will give you an email address that looks like:  
`a1b2c3d4@cloudmailin.net`  
**Copy this address.**

---

## Part 4 — Forward Your Gmail to Cloudmailin

This tells Gmail to send a copy of every incoming email to Cloudmailin, which then shows it in your platform inbox.

**Step 1.** Open [Gmail](https://mail.google.com) and click the **gear icon** (⚙️) in the top-right, then click **See all settings**.

**Step 2.** Go to the **Forwarding and POP/IMAP** tab.

**Step 3.** Click **Add a forwarding address** and paste your Cloudmailin address (from Part 3 Step 5).

**Step 4.** Gmail will send a confirmation email to your Cloudmailin address.  
To confirm it:
- Go back to your Cloudmailin dashboard
- Click on your address → check **Recent Deliveries**
- Find the confirmation email from Google and open it
- Click the confirmation link inside

**Step 5.** Back in Gmail settings (Forwarding tab), select:  
**"Forward a copy of incoming mail to [your Cloudmailin address]"**

**Step 6.** Click **Save Changes**.

---

## Part 5 — Test It

**Step 1.** Ask a friend or colleague to send an email to your Gmail address.

**Step 2.** Within a few seconds, the email should appear as a new conversation in your **Inbox** on the platform.

**Step 3.** Click the conversation, type a reply, and hit **Enter** — the reply will go to your friend's email directly from your Gmail.

---

## Troubleshooting

**Email not showing up in inbox?**

- Make sure forwarding is set to **Enable** (not Disable) in Gmail settings
- Check that the Cloudmailin Target URL matches exactly what was shown in your channel settings
- In Cloudmailin, check **Recent Deliveries** — if you see a green 200 status, it's working

**Reply not sending?**

- Double-check the App Password — it must be the 16-character one from Gmail, not your regular password
- Make sure 2-Step Verification is still turned on in your Google account

**Still stuck?**

Contact support with the email address you're trying to connect and we'll sort it out.

---

## What happens after setup

- Every email sent to your Gmail → appears in your platform inbox instantly
- You reply from the platform → customer receives it from your Gmail address
- Your customers never need to change anything — they just email you as normal
