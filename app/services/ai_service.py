"""
ai_service.py
-------------
Mock AI service — all functions return structured data.

TO CONNECT A REAL LLM:
  File: app/services/ai_service.py
  Function: generate_assignment_from_prompt()  — line ~60
  Function: evaluate_descriptive()             — line ~12
  Function: chat_response()                    — line ~110

  Replace the mock logic in those three functions with an API call, e.g.:

    import anthropic
    client = anthropic.Anthropic(api_key="YOUR_KEY")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

  Or for OpenAI:
    from openai import OpenAI
    client = OpenAI(api_key="YOUR_KEY")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":prompt}]
    )
    return response.choices[0].message.content

  The functions already handle JSON parsing, so just replace the mock
  return value with the real API response string.
"""

import random
import json
import re


# ── Descriptive evaluation ────────────────────────────────────────────────────

def evaluate_descriptive(question_text, student_answer, expected_keywords=None):
    """
    TO CONNECT LLM: replace the body of this function.
    Input you have: question_text (str), student_answer (str), expected_keywords (list)
    Output needed: {"score": float 0-10, "feedback": str, "suggestions": list[str]}
    """
    keywords = expected_keywords or []
    answer_lower = student_answer.lower() if student_answer else ''
    matched = sum(1 for k in keywords if k.lower() in answer_lower) if keywords else 0
    base_score = (matched / len(keywords) * 8) if keywords else random.uniform(4, 9)
    score = round(min(10, base_score + random.uniform(0, 1)), 1)
    feedbacks = [
        "Good understanding of core concepts. Consider elaborating more on the underlying principles.",
        "Your answer covers the main points but could benefit from specific examples.",
        "Well-structured response. The explanation is clear and concise.",
        "You've identified the key aspects. Try to connect them more explicitly.",
        "Solid attempt. Adding more detail about the process would strengthen your answer.",
    ]
    suggestions = [
        "Review the textbook section on this topic for deeper understanding.",
        "Try solving related practice problems to reinforce this concept.",
        "Connect this concept to real-world examples for better retention.",
    ]
    return {
        "score": score,
        "feedback": random.choice(feedbacks),
        "suggestions": random.sample(suggestions, 2)
    }


# ── MCQ wrong-answer explanation ─────────────────────────────────────────────

def evaluate_mcq_wrong(question_text, correct_answer):
    """
    TO CONNECT LLM: replace the body of this function.
    Output needed: {"explanation": str, max ~50 words}
    """
    explanations = [
        f"The correct answer is '{correct_answer}' because this directly relates to the fundamental principle being tested. Review the relevant module topic.",
        f"'{correct_answer}' is correct here. The other options contain subtle errors — re-read the definition carefully.",
        f"This question tests your understanding of the concept. '{correct_answer}' follows from the rule covered in the module.",
    ]
    return {"explanation": random.choice(explanations)}


# ── AI Assignment Generator — FREE-FORM PROMPT ───────────────────────────────

# System prompt sent to the LLM (used when you connect a real model)
ASSIGNMENT_SYSTEM_PROMPT = """You are an expert school teacher and curriculum designer.
Given a teacher's description, generate a complete assignment as a JSON object.

Return ONLY valid JSON, no markdown, no explanation, no backticks.

The JSON must follow this exact structure:
{
  "title": "Assignment title",
  "instructions": "Instructions for students",
  "questions": [
    {
      "type": "mcq",
      "text": "Question text",
      "marks": 2,
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "0",
      "order": 1
    },
    {
      "type": "multi_select",
      "text": "Question text",
      "marks": 4,
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "[\"0\",\"2\"]",
      "order": 2
    },
    {
      "type": "descriptive",
      "text": "Question text",
      "marks": 10,
      "options": null,
      "correct_answer": "keywords: concept, definition, example",
      "order": 3
    },
    {
      "type": "numerical",
      "text": "Question text",
      "marks": 5,
      "options": null,
      "correct_answer": "42",
      "tolerance": 0.5,
      "order": 4
    }
  ]
}

Rules:
- correct_answer for mcq is the index as a string: "0", "1", "2", or "3"
- correct_answer for multi_select is a JSON array string of indices e.g. "[\"0\",\"2\"]"
- correct_answer for descriptive is a comma-separated list of expected keywords
- correct_answer for numerical is the exact number as a string
- tolerance field only for numerical questions (can be null or omitted for others)
- options field only for mcq and multi_select (null for others)
- total marks should roughly match what the teacher asked for
- difficulty should match the teacher's request (easy/medium/hard)
"""


def generate_assignment_from_prompt(teacher_prompt, subject_name):
    """
    Takes a free-form teacher prompt and returns a full assignment dict.

    TO CONNECT A REAL LLM — this is the main function to update:
    ─────────────────────────────────────────────────────────────
    Replace everything below the comment 'MOCK IMPLEMENTATION'
    with a real API call. The function must return a dict with keys:
        {
          "title": str,
          "instructions": str,
          "questions": list of question dicts (see ASSIGNMENT_SYSTEM_PROMPT)
        }

    Example with Anthropic Claude:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            system=ASSIGNMENT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Subject: {subject_name}\n\n{teacher_prompt}"}]
        )
        raw = message.content[0].text
        return json.loads(raw)

    Example with OpenAI:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ASSIGNMENT_SYSTEM_PROMPT},
                {"role": "user",   "content": f"Subject: {subject_name}\n\n{teacher_prompt}"}
            ]
        )
        return json.loads(resp.choices[0].message.content)
    ─────────────────────────────────────────────────────────────
    """

    # ── MOCK IMPLEMENTATION (replace this block with real LLM call) ──────────
    prompt_lower = teacher_prompt.lower()

    # Parse rough intent from the prompt
    total_marks = 20
    for word in prompt_lower.split():
        if word.isdigit() and 5 <= int(word) <= 100:
            total_marks = int(word)
            break

    difficulty = "medium"
    if any(w in prompt_lower for w in ["easy", "simple", "basic", "beginner"]):
        difficulty = "easy"
    elif any(w in prompt_lower for w in ["hard", "difficult", "advanced", "tough"]):
        difficulty = "hard"

    # Extract topic hint from prompt
    topic = subject_name
    for phrase in ["on ", "about ", "for ", "covering ", "topic:"]:
        if phrase in prompt_lower:
            after = teacher_prompt[prompt_lower.index(phrase) + len(phrase):]
            topic = after.split(".")[0].split(",")[0].strip()[:60]
            break

    # Build a mixed assignment
    questions = []
    order = 1
    remaining = total_marks

    diff_map = {"easy": 1, "medium": 2, "hard": 3}
    mcq_marks = diff_map[difficulty]

    # MCQs — use ~40% of marks
    mcq_count = max(2, round(total_marks * 0.4 / mcq_marks))
    for i in range(mcq_count):
        questions.append({
            "type": "mcq",
            "text": f"Which of the following best describes the key concept in '{topic}'? (Q{i+1})",
            "marks": mcq_marks,
            "options": [
                f"The correct definition related to {topic}",
                f"A common misconception about {topic}",
                f"A partially correct statement",
                f"An unrelated concept"
            ],
            "correct_answer": "0",
            "order": order
        })
        order += 1
        remaining -= mcq_marks

    # 1 multi-select if enough marks left
    if remaining >= 4:
        ms_marks = min(4, remaining - 5)
        questions.append({
            "type": "multi_select",
            "text": f"Select ALL statements that are correct regarding '{topic}'.",
            "marks": ms_marks,
            "options": [
                f"Statement 1 — True fact about {topic}",
                f"Statement 2 — False statement",
                f"Statement 3 — True fact about {topic}",
                f"Statement 4 — False statement"
            ],
            "correct_answer": json.dumps(["0", "2"]),
            "order": order
        })
        order += 1
        remaining -= ms_marks

    # 1 numerical if subject sounds mathy or remaining marks allow
    mathy = any(w in subject_name.lower() for w in ["math", "physics", "science", "chemistry", "bio"])
    if remaining >= 4 and mathy:
        num_marks = min(5, remaining - 3)
        questions.append({
            "type": "numerical",
            "text": f"Given the formula related to '{topic}', calculate the value when the input is 12. Show your working.",
            "marks": num_marks,
            "options": None,
            "correct_answer": "24",
            "tolerance": 0.5,
            "order": order
        })
        order += 1
        remaining -= num_marks

    # Descriptive — rest of the marks
    if remaining > 0:
        questions.append({
            "type": "descriptive",
            "text": f"Explain the concept of '{topic}' in your own words. Support your answer with at least two examples and discuss its significance in {subject_name}.",
            "marks": remaining,
            "options": None,
            "correct_answer": f"{topic}, definition, examples, significance, {subject_name}",
            "order": order
        })

    title_difficulty = {"easy": "Basic", "medium": "Unit", "hard": "Advanced"}
    return {
        "title": f"{topic} — {title_difficulty[difficulty]} Test",
        "instructions": f"Read all questions carefully before answering. This assignment covers '{topic}'. Show all working for numerical questions. Total marks: {total_marks}.",
        "questions": questions
    }
    # ── END MOCK IMPLEMENTATION ───────────────────────────────────────────────


# ── Student AI chat ───────────────────────────────────────────────────────────

def chat_response(topic_id, subject_id, message, context=''):
    """
    TO CONNECT LLM: replace the body of this function.
    Output needed: {"reply": str, "topic_id": ..., "subject_id": ...}
    """
    responses = [
        "That's a great question! Based on this topic, the key concept to understand is that everything connects back to the fundamental principle. Try to think about how this applies in real life.",
        "I can help with that! The topic you're studying covers this area in depth. Review the content above, especially the definitions section.",
        "Good thinking! You're on the right track. Remember that in this subject, the approach is always to start with the basics and build up.",
        "Let me help clarify that. The most important thing to remember about this topic is the core formula or rule. Practice applying it to different scenarios.",
        "Excellent question! This is commonly asked in exams too. The answer relates to what we covered earlier in the module — specifically the relationship between the key components.",
    ]
    return {"reply": random.choice(responses), "topic_id": topic_id, "subject_id": subject_id}

"""
ai_service.py
-------------
Mock AI service — all functions return structured data.

TO CONNECT A REAL LLM:
  File: app/services/ai_service.py
  Function: generate_assignment_from_prompt()  — line ~60
  Function: evaluate_descriptive()             — line ~12
  Function: chat_response()                    — line ~110

  Replace the mock logic in those three functions with an API call, e.g.:

    import anthropic
    client = anthropic.Anthropic(api_key="YOUR_KEY")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

  Or for OpenAI:
    from openai import OpenAI
    client = OpenAI(api_key="YOUR_KEY")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":prompt}]
    )
    return response.choices[0].message.content

  The functions already handle JSON parsing, so just replace the mock
  return value with the real API response string.
"""

import random
import json
import re


# ── Descriptive evaluation ────────────────────────────────────────────────────

def evaluate_descriptive(question_text, student_answer, expected_keywords=None):
    """
    TO CONNECT LLM: replace the body of this function.
    Input you have: question_text (str), student_answer (str), expected_keywords (list)
    Output needed: {"score": float 0-10, "feedback": str, "suggestions": list[str]}
    """
    keywords = expected_keywords or []
    answer_lower = student_answer.lower() if student_answer else ''
    matched = sum(1 for k in keywords if k.lower() in answer_lower) if keywords else 0
    base_score = (matched / len(keywords) * 8) if keywords else random.uniform(4, 9)
    score = round(min(10, base_score + random.uniform(0, 1)), 1)
    feedbacks = [
        "Good understanding of core concepts. Consider elaborating more on the underlying principles.",
        "Your answer covers the main points but could benefit from specific examples.",
        "Well-structured response. The explanation is clear and concise.",
        "You've identified the key aspects. Try to connect them more explicitly.",
        "Solid attempt. Adding more detail about the process would strengthen your answer.",
    ]
    suggestions = [
        "Review the textbook section on this topic for deeper understanding.",
        "Try solving related practice problems to reinforce this concept.",
        "Connect this concept to real-world examples for better retention.",
    ]
    return {
        "score": score,
        "feedback": random.choice(feedbacks),
        "suggestions": random.sample(suggestions, 2)
    }


# ── MCQ wrong-answer explanation ─────────────────────────────────────────────

def evaluate_mcq_wrong(question_text, correct_answer):
    """
    TO CONNECT LLM: replace the body of this function.
    Output needed: {"explanation": str, max ~50 words}
    """
    explanations = [
        f"The correct answer is '{correct_answer}' because this directly relates to the fundamental principle being tested. Review the relevant module topic.",
        f"'{correct_answer}' is correct here. The other options contain subtle errors — re-read the definition carefully.",
        f"This question tests your understanding of the concept. '{correct_answer}' follows from the rule covered in the module.",
    ]
    return {"explanation": random.choice(explanations)}


# ── AI Assignment Generator — FREE-FORM PROMPT ───────────────────────────────

# System prompt sent to the LLM (used when you connect a real model)
ASSIGNMENT_SYSTEM_PROMPT = """You are an expert school teacher and curriculum designer.
Given a teacher's description, generate a complete assignment as a JSON object.

Return ONLY valid JSON, no markdown, no explanation, no backticks.

The JSON must follow this exact structure:
{
  "title": "Assignment title",
  "instructions": "Instructions for students",
  "questions": [
    {
      "type": "mcq",
      "text": "Question text",
      "marks": 2,
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "0",
      "order": 1
    },
    {
      "type": "multi_select",
      "text": "Question text",
      "marks": 4,
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "[\"0\",\"2\"]",
      "order": 2
    },
    {
      "type": "descriptive",
      "text": "Question text",
      "marks": 10,
      "options": null,
      "correct_answer": "keywords: concept, definition, example",
      "order": 3
    },
    {
      "type": "numerical",
      "text": "Question text",
      "marks": 5,
      "options": null,
      "correct_answer": "42",
      "tolerance": 0.5,
      "order": 4
    }
  ]
}

Rules:
- correct_answer for mcq is the index as a string: "0", "1", "2", or "3"
- correct_answer for multi_select is a JSON array string of indices e.g. "[\"0\",\"2\"]"
- correct_answer for descriptive is a comma-separated list of expected keywords
- correct_answer for numerical is the exact number as a string
- tolerance field only for numerical questions (can be null or omitted for others)
- options field only for mcq and multi_select (null for others)
- total marks should roughly match what the teacher asked for
- difficulty should match the teacher's request (easy/medium/hard)
"""


def generate_assignment_from_prompt(teacher_prompt, subject_name):
    """
    Takes a free-form teacher prompt and returns a full assignment dict.

    TO CONNECT A REAL LLM — this is the main function to update:
    ─────────────────────────────────────────────────────────────
    Replace everything below the comment 'MOCK IMPLEMENTATION'
    with a real API call. The function must return a dict with keys:
        {
          "title": str,
          "instructions": str,
          "questions": list of question dicts (see ASSIGNMENT_SYSTEM_PROMPT)
        }

    Example with Anthropic Claude:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            system=ASSIGNMENT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Subject: {subject_name}\n\n{teacher_prompt}"}]
        )
        raw = message.content[0].text
        return json.loads(raw)

    Example with OpenAI:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ASSIGNMENT_SYSTEM_PROMPT},
                {"role": "user",   "content": f"Subject: {subject_name}\n\n{teacher_prompt}"}
            ]
        )
        return json.loads(resp.choices[0].message.content)
    ─────────────────────────────────────────────────────────────
    """

    # ── MOCK IMPLEMENTATION (replace this block with real LLM call) ──────────
    prompt_lower = teacher_prompt.lower()

    # Parse rough intent from the prompt
    total_marks = 20
    for word in prompt_lower.split():
        if word.isdigit() and 5 <= int(word) <= 100:
            total_marks = int(word)
            break

    difficulty = "medium"
    if any(w in prompt_lower for w in ["easy", "simple", "basic", "beginner"]):
        difficulty = "easy"
    elif any(w in prompt_lower for w in ["hard", "difficult", "advanced", "tough"]):
        difficulty = "hard"

    # Extract topic hint from prompt
    topic = subject_name
    for phrase in ["on ", "about ", "for ", "covering ", "topic:"]:
        if phrase in prompt_lower:
            after = teacher_prompt[prompt_lower.index(phrase) + len(phrase):]
            topic = after.split(".")[0].split(",")[0].strip()[:60]
            break

    # Build a mixed assignment
    questions = []
    order = 1
    remaining = total_marks

    diff_map = {"easy": 1, "medium": 2, "hard": 3}
    mcq_marks = diff_map[difficulty]

    # MCQs — use ~40% of marks
    mcq_count = max(2, round(total_marks * 0.4 / mcq_marks))
    for i in range(mcq_count):
        questions.append({
            "type": "mcq",
            "text": f"Which of the following best describes the key concept in '{topic}'? (Q{i+1})",
            "marks": mcq_marks,
            "options": [
                f"The correct definition related to {topic}",
                f"A common misconception about {topic}",
                f"A partially correct statement",
                f"An unrelated concept"
            ],
            "correct_answer": "0",
            "order": order
        })
        order += 1
        remaining -= mcq_marks

    # 1 multi-select if enough marks left
    if remaining >= 4:
        ms_marks = min(4, remaining - 5)
        questions.append({
            "type": "multi_select",
            "text": f"Select ALL statements that are correct regarding '{topic}'.",
            "marks": ms_marks,
            "options": [
                f"Statement 1 — True fact about {topic}",
                f"Statement 2 — False statement",
                f"Statement 3 — True fact about {topic}",
                f"Statement 4 — False statement"
            ],
            "correct_answer": json.dumps(["0", "2"]),
            "order": order
        })
        order += 1
        remaining -= ms_marks

    # 1 numerical if subject sounds mathy or remaining marks allow
    mathy = any(w in subject_name.lower() for w in ["math", "physics", "science", "chemistry", "bio"])
    if remaining >= 4 and mathy:
        num_marks = min(5, remaining - 3)
        questions.append({
            "type": "numerical",
            "text": f"Given the formula related to '{topic}', calculate the value when the input is 12. Show your working.",
            "marks": num_marks,
            "options": None,
            "correct_answer": "24",
            "tolerance": 0.5,
            "order": order
        })
        order += 1
        remaining -= num_marks

    # Descriptive — rest of the marks
    if remaining > 0:
        questions.append({
            "type": "descriptive",
            "text": f"Explain the concept of '{topic}' in your own words. Support your answer with at least two examples and discuss its significance in {subject_name}.",
            "marks": remaining,
            "options": None,
            "correct_answer": f"{topic}, definition, examples, significance, {subject_name}",
            "order": order
        })

    title_difficulty = {"easy": "Basic", "medium": "Unit", "hard": "Advanced"}
    return {
        "title": f"{topic} — {title_difficulty[difficulty]} Test",
        "instructions": f"Read all questions carefully before answering. This assignment covers '{topic}'. Show all working for numerical questions. Total marks: {total_marks}.",
        "questions": questions
    }
    # ── END MOCK IMPLEMENTATION ───────────────────────────────────────────────


# ── Student AI chat ───────────────────────────────────────────────────────────

def chat_response(topic_id, subject_id, message, context=''):
    """
    TO CONNECT LLM: replace the body of this function.
    Output needed: {"reply": str, "topic_id": ..., "subject_id": ...}
    """
    responses = [
        "That's a great question! Based on this topic, the key concept to understand is that everything connects back to the fundamental principle. Try to think about how this applies in real life.",
        "I can help with that! The topic you're studying covers this area in depth. Review the content above, especially the definitions section.",
        "Good thinking! You're on the right track. Remember that in this subject, the approach is always to start with the basics and build up.",
        "Let me help clarify that. The most important thing to remember about this topic is the core formula or rule. Practice applying it to different scenarios.",
        "Excellent question! This is commonly asked in exams too. The answer relates to what we covered earlier in the module — specifically the relationship between the key components.",
    ]
    return {"reply": random.choice(responses), "topic_id": topic_id, "subject_id": subject_id}

def generate_questions(subject_name, topic, difficulty='medium', count=3, q_type='mcq'):
    """
    Mock question generator. Returns a list of question dicts.
    Replace with real LLM call if needed.
    """
    import random
    questions = []
    for i in range(count):
        if q_type == 'mcq':
            questions.append({
                "type": "mcq",
                "text": f"Sample MCQ {i+1} about {topic} in {subject_name}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "0",
                "marks": 2
            })
        elif q_type == 'descriptive':
            questions.append({
                "type": "descriptive",
                "text": f"Explain {topic} in your own words.",
                "marks": 5
            })
        else:
            questions.append({
                "type": q_type,
                "text": f"Sample {q_type} question {i+1} on {topic}",
                "marks": 3
            })
    return questions