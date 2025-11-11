import os
from flask import Flask, request, jsonify, Response
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenAI client from env var
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


# === SWAPPABLE SYSTEM PROMPT ===
SYSTEM_PROMPT = """
You are **Coach-in-My-Pocket** — an empathetic, structured, NLP-informed self-development coach.

PRIMARY MISSION
- Help the user improve clarity, mindset, emotional regulation, self-belief, habits, and follow-through.
- Do this through interactive coaching, not lectures: listen, reflect, then ask one powerful next question.

NON-NEGOTIABLE RULES

1. ONE QUESTION RULE
- In every reply, ask EXACTLY ONE question.
- Do NOT chain questions with “and”, “or”, “also”.
- If you’re unsure which question to ask, choose the ONE that best moves the user forward.

2. STYLE & TONE
- Warm, calm, non-judgmental, concise.
- Mirror key emotions in 1–2 short sentences (“It sounds like…”, “I hear that…”).
- No essays. Default to 3–8 short sentences max before your final question.
- No toxic positivity, no shaming, no sarcasm.

3. COACHING, NOT THERAPY
- You are a coach, not a doctor or therapist.
- Do NOT diagnose, label disorders, or give medical instructions.
- If the user mentions self-harm, abuse, or crisis:
  - Respond with empathy.
  - Encourage them to seek professional or emergency help in their country.
  - Stay supportive but within coaching boundaries.

4. CORE METHODS (USE GENTLY, NOT BY NAME)
- GROW: Goal → Reality → Options → Will.
- NLP-style reframing, future pacing, and anchoring.
- CBT-style pattern spotting (thought → feeling → behavior).
- Motivational Interviewing: evoke their reasons, not yours.
- Journaling prompts for reflection when useful.

5. SESSION FLOW (DEFAULT)
Unless user overrides with something specific, guide the conversation in this order:
- Stage 1: RAPPORT & FOCUS
  - Understand what’s on their mind and choose ONE focus area.
- Stage 2: CLARIFY GOAL
  - What “better” looks like for them in clear, simple terms.
- Stage 3: EXPLORE REALITY
  - Current situation, patterns, obstacles.
- Stage 4: BELIEFS & MEANING
  - Gently surface stories/assumptions behind their patterns.
- Stage 5: REFRAME & OPTIONS
  - Offer 1–3 empowering perspectives or options (short, practical).
- Stage 6: COMMITMENT
  - Help them pick 1 small, concrete action and a when.
- Stage 7: RECAP
  - Briefly summarize their insight + action in their own words.

Always pick up from where the user left off. Respect context from earlier messages.

6. HOW TO RESPOND (TEMPLATE)

Each reply should roughly follow this structure:

1) Micro-mirror:
   - One or two sentences that show you understood what they said.

2) Micro-coaching:
   - One to four sentences that either:
     - clarify,
     - gently challenge a belief,
     - highlight a pattern,
     - or suggest 1–2 options (if they’re stuck).
   - Keep it practical and grounded in their words.

3) Single next question:
   - End with ONE clear, specific, open-ended question that leads to the next stage.
   - Examples:
     - “What feels like the real priority underneath all of this?”
     - “What’s one small step you’d realistically take this week?”

Do NOT end a message without a question.
Do NOT switch topics randomly.
Do NOT flood them with frameworks or jargon; keep it human and simple.

7. MODULES (IF USER ASKS)
If the user explicitly asks for help in an area (e.g., anxiety, productivity, relationships, faith, confidence), adapt:
- Keep same coaching style.
- Tailor questions to that theme.
- If faith-based is requested, integrate respectfully and supportively.

8. MEMORY & RETURNING USERS
- If the user reminds you of previous goals in this same conversation, acknowledge continuity.
- Example: “Last time you mentioned working on self-confidence at work. How has that been since we spoke?”

Stay inside these rules at all times.


"""

# Later: when your manager shares his official Coach GPT prompt + knowledge,
# replace SYSTEM_PROMPT with his version and (optionally) inject knowledge chunks.

# In-memory store (OK for MVP demo)
conversations = {}


def enforce_single_question(text: str) -> str:
    parts = text.split("?")
    if len(parts) <= 2:
        return text.strip()
    return (parts[0] + "?").strip()


@app.route("/api/coach", methods=["POST"])
def coach():
    data = request.get_json(force=True)
    user_id = str(data.get("user_id", "demo-user"))
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = conversations.get(user_id, [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    messages.append({"role": "user", "content": user_message})

    #completion = client.chat.completions.create(
       # model="gpt-4o-mini",  # can switch to gpt-4.1 later
       # messages=messages,
        #temperature=0.6,


    #reply = completion.choices[0].message.content
    reply = "Thanks for sharing that. What’s one thing that made you feel that way recently?"

    reply = enforce_single_question(reply)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    conversations[user_id] = history

    return jsonify({"reply": reply})


# === Minimal UI so you can demo in browser ===

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Coach in My Pocket – MVP</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    :root {
      --bg: #020817;
      --bg-elevated: #050816;
      --accent: #22c55e;
      --accent-soft: rgba(34, 197, 94, 0.16);
      --border-subtle: #111827;
      --text-main: #e5e7eb;
      --text-soft: #9ca3af;
      --radius-xl: 18px;
      --radius-lg: 14px;
      --radius-md: 10px;
      --shadow-soft: 0 18px 55px rgba(15,23,42,0.65);
      --transition-fast: 0.18s ease-out;
      --font: system-ui, -apple-system, BlinkMacSystemFont, -system-ui, sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 18px;
      height: 100vh;
      font-family: var(--font);
      background:
        radial-gradient(circle at top left, rgba(34,197,94,0.08), transparent 55%),
        radial-gradient(circle at top right, rgba(56,189,248,0.06), transparent 55%),
        var(--bg);
      color: var(--text-main);
      display: flex;
      justify-content: center;
      align-items: stretch;
    }

    .shell {
      width: min(1280px, 100%);
      height: 100%;
      background: linear-gradient(to bottom right, rgba(15,23,42,0.98), rgba(2,6,23,1));
      border-radius: 26px;
      border: 1px solid rgba(148,163,253,0.08);
      box-shadow: var(--shadow-soft);
      padding: 18px 18px 14px;
      display: grid;
      grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
      gap: 16px;
      backdrop-filter: blur(14px);
    }

    /* Left: Brand / Overview */
    .left {
      display: flex;
      flex-direction: column;
      gap: 14px;
      padding: 12px 14px 10px;
      border-radius: 20px;
      background: radial-gradient(circle at top, rgba(34,197,94,0.07), transparent 65%) #020817;
      border: 1px solid rgba(75,85,99,0.55);
    }

    .brand-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .logo {
      height: 26px;
      width: 26px;
      border-radius: 999px;
      background: radial-gradient(circle at 25% 0, #bbf7d0, #22c55e);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #020817;
      font-size: 16px;
      font-weight: 700;
      box-shadow: 0 8px 16px rgba(34,197,94,0.25);
    }

    .brand-text h1 {
      margin: 0;
      font-size: 17px;
      font-weight: 600;
      letter-spacing: 0.01em;
    }

    .brand-text p {
      margin: 1px 0 0;
      font-size: 11px;
      color: var(--text-soft);
    }

    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 4px;
    }

    .pill {
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 9px;
      color: var(--accent);
      background: var(--accent-soft);
      border: 1px solid rgba(34,197,94,0.24);
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .pill span.icon {
      font-size: 10px;
    }

    .card {
      padding: 9px 9px 8px;
      border-radius: 16px;
      background: rgba(9,9,18,0.98);
      border: 1px solid rgba(75,85,99,0.55);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .card-title {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-soft);
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }

    .card-main {
      font-size: 11px;
      color: var(--text-main);
      line-height: 1.5;
    }

    .mini-label {
      font-size: 9px;
      color: var(--text-soft);
    }

    .step-list {
      display: grid;
      gap: 3px;
      margin-top: 1px;
      font-size: 10px;
      color: var(--text-soft);
    }

    .step-list div::before {
      content: "• ";
      color: var(--accent);
    }

    .status {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 8px;
      border-radius: 12px;
      background: rgba(17,24,39,0.98);
      border: 1px solid rgba(55,65,81,0.9);
      font-size: 9px;
      color: var(--text-soft);
      margin-top: auto;
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 999px;
      background: #22c55e;
      box-shadow: 0 0 10px #22c55e;
    }

    /* Right: Chat */
    .right {
      display: flex;
      flex-direction: column;
      height: 100%;
      padding: 10px 10px 8px;
      border-radius: 20px;
      background: radial-gradient(circle at top right, rgba(34,197,94,0.035), transparent 70%) #020817;
      border: 1px solid rgba(55,65,81,0.7);
      gap: 10px;
    }

    .chat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }

    .chat-title-wrap {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .chat-title {
      font-size: 14px;
      font-weight: 500;
    }

    .chat-subtitle {
      font-size: 10px;
      color: var(--text-soft);
    }

    .mode-pill {
      padding: 4px 8px;
      border-radius: 999px;
      border: 1px solid rgba(75,85,99,0.9);
      font-size: 9px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: var(--text-soft);
    }

    .mode-pill span.icon {
      color: var(--accent);
      font-size: 10px;
    }

    #chat {
      flex: 1;
      padding: 6px 4px 6px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .bubble {
      max-width: 82%;
      padding: 9px 11px;
      border-radius: var(--radius-lg);
      font-size: 12px;
      line-height: 1.55;
      white-space: pre-wrap;
      box-shadow: 0 4px 14px rgba(15,23,42,0.55);
      border: 1px solid transparent;
      transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast);
    }

    .bubble.coach {
      align-self: flex-start;
      background: rgba(5,9,20,1);
      border-color: rgba(34,197,94,0.28);
    }

    .bubble.user {
      align-self: flex-end;
      background: rgba(15,23,42,1);
      border-color: rgba(75,85,99,0.9);
    }

    .bubble.coach:hover,
    .bubble.user:hover {
      transform: translateY(-1px);
      box-shadow: 0 10px 26px rgba(15,23,42,0.9);
    }

    #input-area {
      display: flex;
      gap: 8px;
      padding: 8px 8px 6px;
      border-radius: 16px;
      background: radial-gradient(circle at top left, rgba(15,23,42,0.98), rgba(2,6,23,1));
      border: 1px solid rgba(55,65,81,0.95);
      align-items: flex-end;
    }

    #message {
      flex: 1;
      padding: 9px 10px;
      border-radius: 12px;
      border: 1px solid rgba(75,85,99,0.9);
      background: transparent;
      color: var(--text-main);
      font-size: 12px;
      resize: none;
      min-height: 34px;
      max-height: 88px;
      outline: none;
      transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
    }

    #message::placeholder {
      color: var(--text-soft);
    }

    #message:focus {
      border-color: var(--accent);
      box-shadow: 0 0 16px rgba(34,197,94,0.18);
      background: rgba(2,6,23,1);
    }

    #send {
      padding: 0 16px;
      height: 34px;
      border: none;
      border-radius: 999px;
      background: var(--accent);
      color: #020817;
      font-weight: 600;
      font-size: 11px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 10px 22px rgba(34,197,94,0.35);
      transition: transform var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
      white-space: nowrap;
    }

    #send span.icon {
      font-size: 12px;
    }

    #send:hover {
      transform: translateY(-1px);
      box-shadow: 0 14px 30px rgba(34,197,94,0.42);
      background: #4ade80;
    }

    #send:disabled {
      opacity: 0.55;
      box-shadow: none;
      cursor: default;
      transform: none;
    }

    @media (max-width: 840px) {
      body {
        padding: 10px;
      }
      .shell {
        grid-template-columns: 1fr;
        height: 100%;
      }
      .left {
        order: 2;
      }
      .right {
        order: 1;
        height: 60vh;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <!-- LEFT PANEL: BRAND & FLOW -->
    <aside class="left">
      <div class="brand-row">
        <div class="logo">C</div>
        <div class="brand-text">
          <h1>Coach in My Pocket</h1>
          <p>Your AI growth partner. Always on, always in your corner.</p>
        </div>
      </div>

      <div class="pill-row">
        <div class="pill"><span class="icon">⚡</span>One powerful question at a time</div>
        <div class="pill"><span class="icon">🧠</span>NLP-informed coaching</div>
        <div class="pill"><span class="icon">🕊</span>Non-judgmental & calm</div>
      </div>

      <div class="card">
        <div class="card-title">How it works</div>
        <div class="card-main">
          Share what’s on your mind. Your coach mirrors what it hears, surfaces patterns,
          and guides you toward one clear next step — never overwhelm, always focused.
        </div>
      </div>

      <div class="card">
        <div class="card-title">Session journey</div>
        <div class="mini-label">A typical flow inside this MVP:</div>
        <div class="step-list">
          <div>Rapport & focus on one theme</div>
          <div>Clarify what “better” looks like</div>
          <div>Explore what’s really happening</div>
          <div>Reframe beliefs & unlock options</div>
          <div>Commit to one small, concrete step</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Important</div>
        <div class="card-main">
          This is a coaching assistant, not a therapist.
          In case of crisis or self-harm thoughts, please seek qualified professional or emergency help.
        </div>
      </div>

      <div class="status">
        <div class="status-dot"></div>
        <div>Demo mode: responses are currently mocked until production API key is connected.</div>
      </div>
    </aside>

    <!-- RIGHT PANEL: CHAT -->
    <section class="right">
      <div class="chat-header">
        <div class="chat-title-wrap">
          <div class="chat-title">Live Coaching Space</div>
          <div class="chat-subtitle">Start typing and your pocket coach will respond with one focused question.</div>
        </div>
        <div class="mode-pill">
          <span class="icon">◎</span>
          Guided Q&A · Prototype
        </div>
      </div>

      <div id="chat"></div>

      <div id="input-area">
        <textarea
          id="message"
          placeholder="Tell your coach what’s on your mind, in one or two sentences..."
        ></textarea>
        <button id="send">
          <span class="icon">➜</span>
          Ask Coach
        </button>
      </div>
    </section>
  </div>

  <script>
    const chat = document.getElementById("chat");
    const input = document.getElementById("message");
    const sendBtn = document.getElementById("send");
    const userId = "u-" + Math.floor(Math.random() * 1e9);

    function addBubble(text, role) {
      const div = document.createElement("div");
      div.className = "bubble " + role;
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    async function send() {
      const text = input.value.trim();
      if (!text) return;
      addBubble(text, "user");
      input.value = "";
      sendBtn.disabled = true;

      try {
        const res = await fetch("/api/coach", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, message: text })
        });

        const data = await res.json();
        if (data.reply) {
          addBubble(data.reply, "coach");
        } else {
          addBubble("Something went wrong. Please try again in a moment.", "coach");
        }
      } catch (e) {
        addBubble("Error reaching your coach. Please check your connection.", "coach");
      } finally {
        sendBtn.disabled = false;
        input.focus();
      }
    }

    sendBtn.addEventListener("click", send);

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    // Initial welcome message
    addBubble("Hey, I’m your Coach-in-My-Pocket. What’s been on your mind lately?", "coach");
  </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return Response(HTML_PAGE, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

