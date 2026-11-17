# Week 13 Pilot Exit Survey

Given to each pilot learner at the end of Week 13, after they've had at
least a few sessions across chat, practice, and progress. Pairs with the
in-app feedback widget (`frontend/src/components/FeedbackWidget.js`),
which captures issues *as they happen*; this survey captures the
after-the-fact, whole-experience view once the friction of the moment
has faded and they can compare sessions.

Keep it short enough to finish in 5 minutes — long surveys get abandoned
or rushed. Everything free-text is intentional: category counts already
come from the `feedback` table, so this is for the texture numbers can't
give.

## How to send it

Plain form (Google Form / Typeform / paper, whatever's lowest-friction
for this cohort) rather than another in-app screen — a learner who is
frustrated with the app is not the ideal audience for "please open the
app again to tell us about your frustration."

## Questions

### 1. Overall

- On a scale of 1–5, how likely are you to keep using this to study
  stats/coding? (1 = not at all, 5 = definitely)
- What's the single biggest reason for that score?

### 2. Chat & explanations

- Did the tutor correctly understand what you were asking (stats vs.
  coding, right subtopic)? Any examples where it got confused?
- Were explanations pitched at the right level — too basic, too
  advanced, or about right?

### 3. Practice (quizzes & coding exercises)

- Did the difficulty feel right for where you are, or did it feel
  off (too easy / too hard) at any point?
- For coding exercises specifically: any issues with the editor,
  running your code, or reading the test results?

### 4. Progress / mastery view

- Did the mastery bars feel like an accurate reflection of what you
  actually know? Any subtopic where the score surprised you?

### 5. Speed & reliability

- Did you ever hit a point where the app felt stuck, slow, or
  unresponsive? What were you doing at the time?
- Did you see the "can't reach the API" or similar error message?
  How did you handle it (retried, gave up, waited)?

### 6. Rough edges (open-ended)

- What was the single most annoying thing about using this app?
- Was there anything you expected the app to do that it couldn't?

### 7. Anything else

- Anything else you'd want us to know before the next round?

## After collecting responses

Group answers under the same `bug` / `ux_friction` / `other` buckets
used by the in-app feedback widget so the two sources roll up together,
then weigh both against the "Known rough edges" list in `README.md`
before deciding what Week 14 polish actually goes after.
