# Gemini Virtual Assistant API - cURL Documentation

## Overview

This document provides the cURL commands to interact with a Gemini-powered virtual assistant API that helps users book appointments. The backend is hosted on Render.

---

## 🌐 Base URL

```
https://api-ai-flst.onrender.com
```

---

## 📥 Endpoint: `/chat`

**Method:** `POST`

### Purpose:

Initiates or continues a chat session with the assistant. The assistant gathers:

* Name
* Appointment Date/Time
* Purpose

Once all fields are collected, it simulates a booking via a fake API.

### Request Format:

```json
{
  "session_id": "<unique_session_id>",
  "message": "<user_message>"
}
```

### Headers:

```http
Content-Type: application/json
```

---

## ✅ Examples

### 1. Start a conversation

```bash
curl -X POST https://api-ai-flst.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo123",
    "message": "Hi, my name is Piyush"
  }'
```

### 2. Provide appointment date and time

```bash
curl -X POST https://api-ai-flst.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo123",
    "message": "Appointment on 22 July at 4:30 PM"
  }'
```

### 3. Provide purpose

```bash
curl -X POST https://api-ai-flst.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo123",
    "message": "The purpose is consultation"
  }'
```

---

## 🧠 Booking Simulation

Once all required fields are collected:

* Name
* Date/Time
* Purpose

The assistant automatically sends a POST request to:

```
https://jsonplaceholder.typicode.com/posts
```

You’ll receive a response like:

```json
{
  "reply": "✅ Appointment booked successfully for Piyush on 22 July at 4:30 PM for consultation.",
  "done": true
}
```

---

## 📝 Notes

* Always reuse the same `session_id` to maintain context.
* The API is designed for demonstration purposes.
* Gemini is used via Google Generative AI's Python SDK.

---

## 📬 Contact

If you need help or want to add more features, feel free to ask!
