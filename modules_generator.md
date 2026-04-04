# modules_generator.md
## Prompt for generating course/module/topic management scripts

Use this prompt to ask an LLM (Claude, GPT-4, etc.) to generate Python scripts
that manage the LMS database directly — adding, editing, removing courses,
modules, topics, and assignments without going through the web UI.

---

## THE PROMPT

Copy everything between the triple dashes below and paste it to the LLM,
replacing the [BRACKETED] parts with what you actually want.

---

You are a Python developer working on a Flask + SQLAlchemy LMS application.

### Database

SQLite file at: `lms.db` (same directory as the script)
ORM models are in `app/models/` but the scripts should use raw sqlite3
so they can be run standalone without starting Flask.

### Schema (relevant tables)

```
districts  — id, name, is_active
blocks     — id, name, district_id, is_active
schools    — id, name, block_id, district_id, is_active
classes    — id, name, academic_year, school_id, block_id, district_id, is_active
subjects   — id, name, class_id, school_id, block_id, district_id, is_active
modules    — id, subject_id, title, order, is_active
topics     — id, module_id, title, content_text, file_path, pdf_path, video_url, order, is_active
assignments— id, subject_id, class_id, teacher_id, title, instructions, deadline,
             max_attempts, allow_retry, school_id, block_id, district_id, is_active, created_at
questions  — id, assignment_id, type, text, marks, correct_answer, options,
             tolerance, order, is_active
             (type is one of: mcq, multi_select, descriptive, numerical, file_upload)
             (options is a JSON array string for mcq/multi_select, NULL otherwise)
             (correct_answer for mcq = index string "0"/"1"/"2"/"3")
             (correct_answer for multi_select = JSON array string e.g. '["0","2"]')
users      — id, username, role, school_id, block_id, district_id, is_active
```

### Rules

- Never hard-delete rows. Set is_active = 0 for soft deletes.
- Always print what was created/updated/deleted with the row id.
- Use parameterised queries (? placeholders), never string formatting for values.
- Scripts must be runnable with just: python script_name.py
- Put DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lms.db') at the top.
- If inserting, print the new row id after commit.
- If a required foreign key row doesn't exist, print a clear error and exit.

### Task

[DESCRIBE EXACTLY WHAT YOU WANT THE SCRIPT TO DO]

Examples of tasks you can put here:
  - "Add a new module called 'Trigonometry' to subject id 1, then add 3 topics to it with placeholder content"
  - "Bulk-import topics from a list of (title, content_text) pairs into module id 4"
  - "List all subjects and their module/topic counts for school id 1"
  - "Soft-delete all topics in module id 7"
  - "Create a full assignment for subject id 2 with 3 MCQs and 1 descriptive question"
  - "Update the video_url for topic id 12 to a YouTube link"
  - "Add a new subject 'Physics' to class id 3 and assign teacher id 5 to it"
  - "Export all topics for subject id 1 as a JSON file"

### Output format

Return a single Python script with:
1. A docstring at the top explaining what it does
2. All logic in a main() function
3. if __name__ == '__main__': main() at the bottom
4. No external dependencies beyond the Python standard library

---

## TIPS FOR BEST RESULTS

- Be specific about IDs if you know them (e.g. "subject id 3" not "the maths subject")
- For bulk operations, describe the data inline or say "read from a list in the script"
- If you want interactive input, say "prompt the user for each value"
- To see what IDs exist first, ask: "Write a script that lists all subjects with
  their IDs, class names, and school names"

## EXAMPLE CONVERSATION

You:
> [paste the prompt above with task = "List all subjects with their IDs,
>  class name, school name, and count of active modules and topics"]

LLM returns a script. Run it:
> python list_subjects.py

You see the IDs you need. Then ask again with a new task using those IDs.

---

## CONNECTING A REAL LLM TO THE APP

To replace mock AI with a real model, edit ONE function in:
    app/services/ai_service.py

For assignment generation (the main one):
    Function: generate_assignment_from_prompt()   — look for "MOCK IMPLEMENTATION"

For descriptive answer grading:
    Function: evaluate_descriptive()

For student chat:
    Function: chat_response()

The ASSIGNMENT_SYSTEM_PROMPT string in that file is the ready-made system
prompt — just pass it to your LLM of choice along with the teacher's prompt.
