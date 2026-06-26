# How to Add Live Chat to Your Website

This guide shows you how to add a live chat widget to your website so your visitors can message you — and you can reply from your inbox instantly.

**Time needed:** 5 minutes  
**What you need:** Access to your website's HTML code

---

## What it looks like

Once set up, a small chat box will appear in the bottom-right corner of your website. Visitors can type a message, and you'll see it in your inbox right away.

---

## Step 1 — Create a Web Chat Channel

**1.** Go to **Settings → Channels** in the platform.

**2.** Under the **Web Chat** section, click **Create Channel**.

**3.** Give it a name — for example: `Website Chat` or `Support Widget`.

**4.** Click **Create**. You'll see:
- A **Channel ID** (a long code like `6832096d-e8ec-...`)
- A ready-to-use **embed code snippet**

**Copy the embed code** — you'll paste it into your website in the next step.

---

## Step 2 — Add the Chat Widget to Your Website

The embed code looks like this:

```html
<script
  src="https://ucaas-api-919679113744.asia-south1.run.app/webchat-widget.js"
  data-account="YOUR_CHANNEL_ID"
  data-api="https://ucaas-api-919679113744.asia-south1.run.app">
</script>
```

**Where to paste it:**

Paste this code just before the closing `</body>` tag on every page where you want the chat to appear.

---

### If your website is built with a website builder:

**WordPress**
1. Go to **Appearance → Theme Editor** (or use a plugin like "Insert Headers and Footers")
2. Open your theme's `footer.php` file
3. Paste the code just before `</body>`
4. Click **Update File**

**Shopify**
1. Go to **Online Store → Themes → Edit Code**
2. Open `theme.liquid`
3. Paste the code just before `</body>`
4. Click **Save**

**Wix**
1. Go to **Settings → Custom Code**
2. Click **+ Add Custom Code**
3. Paste the code, set it to load on **All pages**, place it in the **Body - end**
4. Click **Apply**

**Squarespace**
1. Go to **Settings → Advanced → Code Injection**
2. Paste the code in the **Footer** section
3. Click **Save**

**Plain HTML website**
Open your HTML file and paste the code just before `</body>`.

---

## Step 3 — Test It

**1.** Open your website in a browser. You should see a **"Chat with us"** box in the bottom-right corner.

**2.** Type a test message and press **Enter** or click **Send**.

**3.** Open your platform inbox — the message should appear within a few seconds.

**4.** Reply from the inbox — your reply will show up inside the chat widget on your website automatically.

---

## That's it!

Your visitors can now message you directly from your website, and you can reply from one central inbox alongside all your other channels.

---

## Frequently Asked Questions

**Will the chat widget remember returning visitors?**  
Yes. The widget stores a session in the visitor's browser, so if they come back, their previous conversation continues.

**Can I add the widget to multiple pages?**  
Yes. Add the code to every page where you want the chat to appear. You can even add it site-wide (usually by editing the footer/layout template once).

**Can I change the look of the widget?**  
The default widget has a clean, minimal style. Custom branding (colors, logo, name) is available — contact support to set it up.

**What if a visitor messages when I'm offline?**  
The message still comes in and sits in your inbox. You can reply whenever you're back online, and the visitor will see your reply the next time they open the chat.

**Do visitors need to create an account?**  
No. Visitors just type and send — no sign-up required on their end.
