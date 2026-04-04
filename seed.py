"""
seed.py — Run once to populate the database with full dummy data.
Usage: python seed.py
"""
from app import create_app, db
from app.models.hierarchy import District, Block, School
from app.models.user import User, ParentStudent
from app.models.academic import Class, ClassTeacher, StudentClass, Subject, Module, Topic, TopicProgress
from app.models.assignment import Assignment, Question, Submission, SubmissionAnswer
from app.models.announcement import Announcement
from datetime import datetime, timedelta
import json

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Tables created.")

    # ── Hierarchy ──────────────────────────────────────────────
    district1 = District(name="Chennai District")
    district2 = District(name="Coimbatore District")
    db.session.add_all([district1, district2])
    db.session.flush()

    block1 = Block(name="Ambattur Block", district_id=district1.id)
    block2 = Block(name="Tambaram Block", district_id=district1.id)
    block3 = Block(name="RS Puram Block", district_id=district2.id)
    db.session.add_all([block1, block2, block3])
    db.session.flush()

    school1 = School(name="Govt. Higher Secondary School, Ambattur", block_id=block1.id, district_id=district1.id)
    school2 = School(name="Govt. High School, Tambaram", block_id=block2.id, district_id=district1.id)
    school3 = School(name="Govt. High School, RS Puram", block_id=block3.id, district_id=district2.id)
    db.session.add_all([school1, school2, school3])
    db.session.flush()

    # ── Users ──────────────────────────────────────────────────
    def make_user(username, full_name, role, district_id=None, block_id=None, school_id=None, email=None):
        u = User(username=username, full_name=full_name, role=role,
                 district_id=district_id, block_id=block_id, school_id=school_id,
                 email=email or f"{username}@lms.edu")
        u.set_password("pass123")
        return u

    super_admin   = make_user("superadmin",    "Super Admin",            "super_admin")
    dist_admin1   = make_user("districtadmin1","Ravi Kumar (DA)",        "district_admin", district_id=district1.id)
    dist_admin2   = make_user("districtadmin2","Priya Nair (DA)",        "district_admin", district_id=district2.id)
    block_admin1  = make_user("blockadmin1",   "Senthil Raja (BA)",      "block_admin",    district_id=district1.id, block_id=block1.id)
    block_admin2  = make_user("blockadmin2",   "Meena Devi (BA)",        "block_admin",    district_id=district1.id, block_id=block2.id)
    school_admin1 = make_user("schooladmin1",  "Kavitha Sundaram (SA)",  "school_admin",   district_id=district1.id, block_id=block1.id, school_id=school1.id)
    school_admin2 = make_user("schooladmin2",  "Arjun Pillai (SA)",      "school_admin",   district_id=district1.id, block_id=block2.id, school_id=school2.id)

    teacher1 = make_user("teacher1", "Mrs. Lakshmi Priya",  "teacher", district_id=district1.id, block_id=block1.id, school_id=school1.id)
    teacher2 = make_user("teacher2", "Mr. Ramesh Babu",     "teacher", district_id=district1.id, block_id=block1.id, school_id=school1.id)
    teacher3 = make_user("teacher3", "Ms. Deepa Krishnan",  "teacher", district_id=district1.id, block_id=block2.id, school_id=school2.id)

    student1 = make_user("student1", "Arjun Sharma",   "student", district_id=district1.id, block_id=block1.id, school_id=school1.id)
    student2 = make_user("student2", "Priya Venkat",   "student", district_id=district1.id, block_id=block1.id, school_id=school1.id)
    student3 = make_user("student3", "Karthik Rajan",  "student", district_id=district1.id, block_id=block1.id, school_id=school1.id)
    student4 = make_user("student4", "Ananya Suresh",  "student", district_id=district1.id, block_id=block2.id, school_id=school2.id)

    parent1 = make_user("parent1", "Mr. Sharma (Parent)", "parent", district_id=district1.id, block_id=block1.id, school_id=school1.id)
    parent2 = make_user("parent2", "Mrs. Venkat (Parent)","parent", district_id=district1.id, block_id=block1.id, school_id=school1.id)

    all_users = [super_admin, dist_admin1, dist_admin2, block_admin1, block_admin2,
                 school_admin1, school_admin2, teacher1, teacher2, teacher3,
                 student1, student2, student3, student4, parent1, parent2]
    db.session.add_all(all_users)
    db.session.flush()

    # Parent–student links
    db.session.add(ParentStudent(parent_id=parent1.id, student_id=student1.id))
    db.session.add(ParentStudent(parent_id=parent1.id, student_id=student2.id))
    db.session.add(ParentStudent(parent_id=parent2.id, student_id=student2.id))
    db.session.flush()

    # ── Classes ────────────────────────────────────────────────
    class10a = Class(name="Class 10 - Section A", academic_year="2024-25",
                     school_id=school1.id, block_id=block1.id, district_id=district1.id)
    class10b = Class(name="Class 10 - Section B", academic_year="2024-25",
                     school_id=school1.id, block_id=block1.id, district_id=district1.id)
    class9a  = Class(name="Class 9 - Section A",  academic_year="2024-25",
                     school_id=school2.id, block_id=block2.id, district_id=district1.id)
    db.session.add_all([class10a, class10b, class9a])
    db.session.flush()

    # Enroll students
    db.session.add(StudentClass(student_id=student1.id, class_id=class10a.id))
    db.session.add(StudentClass(student_id=student2.id, class_id=class10a.id))
    db.session.add(StudentClass(student_id=student3.id, class_id=class10b.id))
    db.session.add(StudentClass(student_id=student4.id, class_id=class9a.id))
    db.session.flush()

    # ── Subjects ───────────────────────────────────────────────
    math10   = Subject(name="Mathematics",       class_id=class10a.id, school_id=school1.id, block_id=block1.id, district_id=district1.id)
    science10= Subject(name="Science",           class_id=class10a.id, school_id=school1.id, block_id=block1.id, district_id=district1.id)
    english10= Subject(name="English",           class_id=class10a.id, school_id=school1.id, block_id=block1.id, district_id=district1.id)
    math10b  = Subject(name="Mathematics",       class_id=class10b.id, school_id=school1.id, block_id=block1.id, district_id=district1.id)
    science9 = Subject(name="Science",           class_id=class9a.id,  school_id=school2.id, block_id=block2.id, district_id=district1.id)
    db.session.add_all([math10, science10, english10, math10b, science9])
    db.session.flush()

    # Assign teachers to class-subjects
    db.session.add(ClassTeacher(class_id=class10a.id, teacher_id=teacher1.id, subject_id=math10.id))
    db.session.add(ClassTeacher(class_id=class10a.id, teacher_id=teacher2.id, subject_id=science10.id))
    db.session.add(ClassTeacher(class_id=class10a.id, teacher_id=teacher1.id, subject_id=english10.id))
    db.session.add(ClassTeacher(class_id=class10b.id, teacher_id=teacher1.id, subject_id=math10b.id))
    db.session.add(ClassTeacher(class_id=class9a.id,  teacher_id=teacher3.id, subject_id=science9.id))
    db.session.flush()

    # ── Modules & Topics ──────────────────────────────────────
    # Mathematics modules
    mod_algebra = Module(subject_id=math10.id, title="Chapter 1: Algebra", order=1)
    mod_geometry= Module(subject_id=math10.id, title="Chapter 2: Geometry", order=2)
    mod_stats   = Module(subject_id=math10.id, title="Chapter 3: Statistics", order=3)
    db.session.add_all([mod_algebra, mod_geometry, mod_stats])
    db.session.flush()

    algebra_topics = [
        Topic(module_id=mod_algebra.id, title="Introduction to Polynomials", order=1,
              content_text="A polynomial is an expression consisting of variables and coefficients, involving only the operations of addition, subtraction, multiplication, and non-negative integer exponentiation. For example: 3x² + 2x - 5 is a polynomial of degree 2, also called a quadratic polynomial.\n\nKey Concepts:\n• Degree of a polynomial: the highest power of the variable\n• Coefficient: the number multiplied with the variable\n• Constant term: the term with no variable\n• Monomial: one term (e.g., 5x)\n• Binomial: two terms (e.g., x + 3)\n• Trinomial: three terms (e.g., x² + 2x + 1)\n\nExamples:\n1. p(x) = 2x³ - 4x + 7  (degree 3, cubic)\n2. q(x) = x² - 9        (degree 2, quadratic)\n3. r(x) = 6x - 1        (degree 1, linear)"),
        Topic(module_id=mod_algebra.id, title="Zeroes of a Polynomial", order=2,
              content_text="A zero (or root) of a polynomial p(x) is a value of x for which p(x) = 0.\n\nFinding Zeroes:\nFor a linear polynomial ax + b, the zero is x = -b/a.\nFor a quadratic ax² + bx + c, zeroes can be found by factorisation or the quadratic formula:\n  x = (-b ± √(b² - 4ac)) / 2a\n\nThe Discriminant (D = b² - 4ac):\n• D > 0: two distinct real zeroes\n• D = 0: two equal real zeroes\n• D < 0: no real zeroes\n\nRelationship between zeroes and coefficients:\nFor ax² + bx + c with zeroes α and β:\n  α + β = -b/a\n  α × β = c/a"),
        Topic(module_id=mod_algebra.id, title="Division Algorithm for Polynomials", order=3,
              content_text="Just as we divide integers using long division, we can divide polynomials.\n\nDivision Algorithm: If p(x) and g(x) are polynomials with g(x) ≠ 0, then:\n  p(x) = g(x) × q(x) + r(x)\nwhere q(x) is the quotient and r(x) is the remainder, and degree of r(x) < degree of g(x).\n\nSteps for polynomial long division:\n1. Arrange terms in descending order of degree\n2. Divide the leading term of dividend by leading term of divisor\n3. Multiply the entire divisor by this result\n4. Subtract from dividend\n5. Bring down the next term\n6. Repeat until degree of remainder < degree of divisor"),
    ]
    geometry_topics = [
        Topic(module_id=mod_geometry.id, title="Similar Triangles", order=1,
              content_text="Two triangles are similar if their corresponding angles are equal and corresponding sides are proportional.\n\nCriteria for Similarity:\n1. AA (Angle-Angle): If two angles of one triangle equal two angles of another\n2. SSS (Side-Side-Side): If three sides are proportional\n3. SAS (Side-Angle-Side): If two sides are proportional and included angle is equal\n\nBasic Proportionality Theorem (Thales Theorem): A line drawn parallel to one side of a triangle divides the other two sides proportionally.\n\nApplications: Similar triangles are used in architecture, maps, engineering, and physics."),
        Topic(module_id=mod_geometry.id, title="Pythagoras Theorem", order=2,
              content_text="In a right-angled triangle, the square of the hypotenuse equals the sum of squares of the other two sides.\n  c² = a² + b²\nwhere c is the hypotenuse.\n\nProof using similar triangles:\nDraw an altitude from the right angle to the hypotenuse and use proportionality.\n\nConverse: If c² = a² + b², the triangle is right-angled.\n\nPythagorean Triplets: Sets of whole numbers (a, b, c) satisfying c² = a² + b²:\n  (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)"),
    ]
    stats_topics = [
        Topic(module_id=mod_stats.id, title="Mean, Median and Mode", order=1,
              content_text="Measures of Central Tendency summarise a dataset with a single value.\n\nMean: Sum of all observations / Number of observations\n  For grouped data: Mean = Σfx / Σf\n\nMedian: The middle value when data is arranged in order.\n  For odd n: median = ((n+1)/2)th value\n  For even n: median = average of (n/2)th and (n/2 + 1)th values\n  For grouped data use the formula: M = l + [(n/2 - cf)/f] × h\n\nMode: The value that appears most frequently.\n  For grouped data: Mode = l + [(f1-f0)/(2f1-f0-f2)] × h\n\nEmpirical Relationship: Mode = 3 × Median − 2 × Mean"),
    ]
    db.session.add_all(algebra_topics + geometry_topics + stats_topics)

    # Science modules
    mod_carbon  = Module(subject_id=science10.id, title="Carbon and Its Compounds", order=1)
    mod_life    = Module(subject_id=science10.id, title="Life Processes", order=2)
    db.session.add_all([mod_carbon, mod_life])
    db.session.flush()

    science_topics = [
        Topic(module_id=mod_carbon.id, title="Introduction to Carbon", order=1,
              content_text="Carbon is one of the most versatile elements, found in millions of compounds. It forms the basis of all living organisms.\n\nWhy Carbon is Special (Covalent Bonding):\n• Carbon has 4 valence electrons — it can form 4 covalent bonds\n• It can bond with other carbon atoms (catenation)\n• It forms double and triple bonds\n\nAllotropes of Carbon:\n• Diamond: each carbon bonds to 4 others in a tetrahedral structure, making it the hardest natural substance\n• Graphite: carbon atoms form layers of hexagonal rings; used as lubricant and in pencils\n• Fullerene (C60): soccer-ball shaped molecule"),
        Topic(module_id=mod_carbon.id, title="Functional Groups in Carbon Compounds", order=2,
              content_text="Functional groups are specific groups of atoms within molecules that are responsible for the characteristic chemical reactions of those molecules.\n\nCommon Functional Groups:\n• Halogens (-Cl, -Br): haloalkanes\n• Alcohol (-OH): e.g., ethanol C₂H₅OH\n• Aldehyde (-CHO): e.g., formaldehyde\n• Ketone (-C=O-): e.g., acetone\n• Carboxylic acid (-COOH): e.g., acetic acid\n\nNaming Rule: The functional group determines the suffix of the compound name."),
        Topic(module_id=mod_life.id, title="Nutrition in Living Organisms", order=1,
              content_text="All living organisms need energy to sustain life processes. Nutrition is the process by which organisms obtain and use food.\n\nTypes of Nutrition:\n1. Autotrophic Nutrition: Organisms make their own food\n   • Photosynthesis: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂ (in presence of sunlight and chlorophyll)\n\n2. Heterotrophic Nutrition: Organisms consume other organisms\n   • Holozoic (animals)\n   • Saprophytic (fungi, bacteria decomposing dead matter)\n   • Parasitic (getting nutrition from a host)\n\nHuman Digestive System: Mouth → Oesophagus → Stomach → Small Intestine → Large Intestine → Rectum"),
        Topic(module_id=mod_life.id, title="Respiration", order=2,
              content_text="Respiration is the process by which living organisms break down food to release energy.\n\nAerobic Respiration (with oxygen):\n  C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy (38 ATP)\n\nAnaerobic Respiration (without oxygen):\n  In yeast: C₆H₁₂O₆ → 2C₂H₅OH + 2CO₂ + Energy\n  In muscles: C₆H₁₂O₆ → 2 lactic acid + Energy\n\nHuman Respiratory System: Nostrils → Nasal cavity → Pharynx → Larynx → Trachea → Bronchi → Lungs → Alveoli\n\nGaseous Exchange: Oxygen diffuses from alveoli into blood; CO₂ diffuses from blood into alveoli."),
    ]
    db.session.add_all(science_topics)
    db.session.flush()

    # English module
    mod_grammar = Module(subject_id=english10.id, title="Grammar Essentials", order=1)
    mod_writing = Module(subject_id=english10.id, title="Writing Skills", order=2)
    db.session.add_all([mod_grammar, mod_writing])
    db.session.flush()
    db.session.add_all([
        Topic(module_id=mod_grammar.id, title="Parts of Speech", order=1,
              content_text="The eight parts of speech classify words based on their role in a sentence.\n\n1. Noun: names a person, place, thing, or idea (e.g., book, city)\n2. Pronoun: replaces a noun (e.g., he, they, it)\n3. Verb: shows action or state (e.g., run, is, think)\n4. Adjective: describes a noun (e.g., tall, red, clever)\n5. Adverb: modifies a verb, adjective, or another adverb (e.g., quickly, very)\n6. Preposition: shows relationship (e.g., in, on, under)\n7. Conjunction: connects words or clauses (e.g., and, but, because)\n8. Interjection: expresses emotion (e.g., Oh!, Wow!)"),
        Topic(module_id=mod_writing.id, title="Essay Writing", order=1,
              content_text="An essay is a structured piece of writing that presents an argument or discusses a topic.\n\nStructure of an Essay:\n1. Introduction (10%): Hook, background context, thesis statement\n2. Body Paragraphs (80%): Each paragraph has one main idea\n   • Topic sentence\n   • Supporting evidence\n   • Analysis/explanation\n   • Concluding sentence\n3. Conclusion (10%): Summarise main points, restate thesis, closing thought\n\nTypes of Essays:\n• Descriptive: describes a person, place, or thing\n• Narrative: tells a story\n• Expository: explains a topic\n• Argumentative: takes a position and argues for it"),
    ])
    db.session.flush()

    # Mark some topics as viewed for student1
    viewed_topic_ids = [algebra_topics[0].id, algebra_topics[1].id, geometry_topics[0].id,
                        science_topics[0].id, science_topics[2].id]
    for tid in viewed_topic_ids:
        db.session.add(TopicProgress(student_id=student1.id, topic_id=tid))
    # student2 viewed some
    for tid in [algebra_topics[0].id, science_topics[0].id]:
        db.session.add(TopicProgress(student_id=student2.id, topic_id=tid))
    db.session.flush()

    # ── Assignments ────────────────────────────────────────────
    now = datetime.utcnow()

    # Assignment 1: Math — past deadline, has approved submission
    asgn1 = Assignment(
        subject_id=math10.id, class_id=class10a.id, teacher_id=teacher1.id,
        title="Polynomials — Unit Test 1",
        instructions="Attempt all questions. Show your working for numerical problems.",
        deadline=now - timedelta(days=5),
        max_attempts=1, allow_retry=False,
        school_id=school1.id, block_id=block1.id, district_id=district1.id
    )
    # Assignment 2: Science — upcoming, not submitted
    asgn2 = Assignment(
        subject_id=science10.id, class_id=class10a.id, teacher_id=teacher2.id,
        title="Carbon Compounds — Assignment 1",
        instructions="Read the chapter carefully before attempting.",
        deadline=now + timedelta(days=7),
        max_attempts=2, allow_retry=True,
        school_id=school1.id, block_id=block1.id, district_id=district1.id
    )
    # Assignment 3: Math — upcoming
    asgn3 = Assignment(
        subject_id=math10.id, class_id=class10a.id, teacher_id=teacher1.id,
        title="Statistics — Mean, Median and Mode",
        instructions="All calculations must be shown clearly.",
        deadline=now + timedelta(days=3),
        max_attempts=1,
        school_id=school1.id, block_id=block1.id, district_id=district1.id
    )
    db.session.add_all([asgn1, asgn2, asgn3])
    db.session.flush()

    # Questions for Assignment 1 (Polynomials)
    q1 = Question(assignment_id=asgn1.id, type="mcq", order=1, marks=2,
        text="Which of the following is a polynomial of degree 3?",
        options=json.dumps(["x² + 2x + 1", "x³ - 4x + 7", "1/x + 2", "√x + 5"]),
        correct_answer="1")
    q2 = Question(assignment_id=asgn1.id, type="mcq", order=2, marks=2,
        text="The zeroes of the polynomial p(x) = x² - 5x + 6 are:",
        options=json.dumps(["2 and 3", "1 and 6", "-2 and -3", "2 and -3"]),
        correct_answer="0")
    q3 = Question(assignment_id=asgn1.id, type="numerical", order=3, marks=3,
        text="If the sum of zeroes of p(x) = kx² + 2x + 3k is equal to their product, find the value of k.",
        correct_answer="-0.667", tolerance=0.01)
    q4 = Question(assignment_id=asgn1.id, type="descriptive", order=4, marks=5,
        text="Explain the division algorithm for polynomials with an example. What conditions must be satisfied?",
        correct_answer="division algorithm, p(x)=g(x)q(x)+r(x), degree remainder, example")
    q5 = Question(assignment_id=asgn1.id, type="multi_select", order=5, marks=4,
        text="Which of the following are Pythagorean triplets? (Select all that apply)",
        options=json.dumps(["(3, 4, 5)", "(5, 12, 13)", "(6, 7, 8)", "(8, 15, 17)"]),
        correct_answer=json.dumps(["0", "1", "3"]))
    db.session.add_all([q1, q2, q3, q4, q5])

    # Questions for Assignment 2 (Science — Carbon)
    q6 = Question(assignment_id=asgn2.id, type="mcq", order=1, marks=2,
        text="Carbon has atomic number 6. How many valence electrons does it have?",
        options=json.dumps(["2", "4", "6", "8"]),
        correct_answer="1")
    q7 = Question(assignment_id=asgn2.id, type="mcq", order=2, marks=2,
        text="Which allotrope of carbon is used as a lubricant?",
        options=json.dumps(["Diamond", "Fullerene", "Graphite", "Coal"]),
        correct_answer="2")
    q8 = Question(assignment_id=asgn2.id, type="descriptive", order=3, marks=6,
        text="Explain why carbon forms a large number of compounds compared to other elements. Mention at least two key properties.",
        correct_answer="catenation, tetravalency, covalent bonds, versatile")
    db.session.add_all([q6, q7, q8])

    # Questions for Assignment 3 (Statistics)
    q9 = Question(assignment_id=asgn3.id, type="numerical", order=1, marks=3,
        text="The mean of 5 numbers is 18. If one number is removed, the mean becomes 16. What is the removed number?",
        correct_answer="26", tolerance=0)
    q10 = Question(assignment_id=asgn3.id, type="mcq", order=2, marks=2,
        text="The mode of the data 2, 3, 4, 5, 4, 3, 4 is:",
        options=json.dumps(["2", "3", "4", "5"]),
        correct_answer="2")
    q11 = Question(assignment_id=asgn3.id, type="descriptive", order=3, marks=5,
        text="Explain the empirical relationship between mean, median and mode with an example.",
        correct_answer="Mode = 3 Median - 2 Mean, empirical, example")
    db.session.add_all([q9, q10, q11])
    db.session.flush()

    # ── Submission for Assignment 1 (student1 — approved) ──────
    sub1 = Submission(
        assignment_id=asgn1.id, student_id=student1.id, attempt_number=1,
        status="approved",
        submitted_at=now - timedelta(days=4),
        teacher_approved_at=now - timedelta(days=3),
        final_score=12.5,
        teacher_feedback="Good work overall! Your understanding of polynomial division needs more practice. Review the examples again."
    )
    db.session.add(sub1)
    db.session.flush()

    answers1 = [
        SubmissionAnswer(submission_id=sub1.id, question_id=q1.id, answer_text="1",
            ai_score=2.0, teacher_score=2.0, is_correct=True),
        SubmissionAnswer(submission_id=sub1.id, question_id=q2.id, answer_text="2",
            ai_score=0.0, ai_feedback="The zeroes are found by factorising x²-5x+6 = (x-2)(x-3), giving zeroes 2 and 3, not -2 and -3.",
            teacher_score=0.0, is_correct=False),
        SubmissionAnswer(submission_id=sub1.id, question_id=q3.id, answer_text="-0.667",
            ai_score=3.0, teacher_score=3.0, is_correct=True),
        SubmissionAnswer(submission_id=sub1.id, question_id=q4.id,
            answer_text="The division algorithm states that any polynomial p(x) divided by g(x) can be written as p(x) = g(x) * q(x) + r(x) where the degree of r(x) is less than g(x). For example, if we divide x²+3x+1 by x+1, we get quotient x+2 and remainder -1.",
            ai_score=4.0, ai_feedback="Good attempt. The definition is mostly correct. Remember to state clearly that g(x) ≠ 0 as a condition.",
            teacher_score=4.5, teacher_override=True, is_correct=True),
        SubmissionAnswer(submission_id=sub1.id, question_id=q5.id, answer_text='["0","1","3"]',
            ai_score=4.0, teacher_score=4.0, is_correct=True),
    ]
    db.session.add_all(answers1)

    # Submission for Assignment 1 (student2 — pending_review)
    sub2 = Submission(
        assignment_id=asgn1.id, student_id=student2.id, attempt_number=1,
        status="pending_review",
        submitted_at=now - timedelta(days=3),
    )
    db.session.add(sub2)
    db.session.flush()
    answers2 = [
        SubmissionAnswer(submission_id=sub2.id, question_id=q1.id, answer_text="1", ai_score=2.0, is_correct=True),
        SubmissionAnswer(submission_id=sub2.id, question_id=q2.id, answer_text="0", ai_score=2.0, is_correct=True),
        SubmissionAnswer(submission_id=sub2.id, question_id=q3.id, answer_text="-0.5", ai_score=0.0, is_correct=False),
        SubmissionAnswer(submission_id=sub2.id, question_id=q4.id,
            answer_text="Division algorithm divides a polynomial by another polynomial similar to long division of numbers.",
            ai_score=2.5, ai_feedback="Partially correct. Add the formal expression p(x)=g(x)q(x)+r(x) and an example."),
        SubmissionAnswer(submission_id=sub2.id, question_id=q5.id, answer_text='["0","1"]', ai_score=2.7, is_correct=False,
            ai_feedback="You missed (8,15,17). Check: 8²+15²=64+225=289=17². That is a valid Pythagorean triplet."),
    ]
    db.session.add_all(answers2)

    # ── Announcements ──────────────────────────────────────────
    ann1 = Announcement(
        created_by=school_admin1.id, scope="school",
        school_id=school1.id, block_id=block1.id, district_id=district1.id,
        title="Annual Sports Day — 15th March",
        body="All students are invited to participate in the Annual Sports Day on 15th March 2025. Events include 100m sprint, long jump, relay race, and shot put. Registration starts from Monday. Contact your class teacher for details.",
        channel="in_app"
    )
    ann2 = Announcement(
        created_by=teacher1.id, scope="class", class_id=class10a.id,
        school_id=school1.id, block_id=block1.id, district_id=district1.id,
        title="Maths Unit Test — Syllabus Update",
        body="Dear students of Class 10-A, the upcoming unit test on Polynomials will now include Chapter 3 (Statistics) as well. Please revise Mean, Median and Mode. The test is scheduled for next Friday.",
        channel="in_app"
    )
    ann3 = Announcement(
        created_by=teacher2.id, scope="class", class_id=class10a.id,
        school_id=school1.id, block_id=block1.id, district_id=district1.id,
        title="Science Project Submission Reminder",
        body="This is a reminder that the Carbon Compounds project is due by this Friday. Please submit your write-up along with the diagrams. Late submissions will not be accepted.",
        channel="in_app"
    )
    ann4 = Announcement(
        created_by=school_admin1.id, scope="school",
        school_id=school1.id, block_id=block1.id, district_id=district1.id,
        title="Parent-Teacher Meeting — 20th March",
        body="A Parent-Teacher Meeting is scheduled for 20th March 2025 from 9 AM to 1 PM. Parents of all classes are requested to attend. Attendance register will be maintained.",
        channel="in_app"
    )
    db.session.add_all([ann1, ann2, ann3, ann4])
    db.session.commit()

    print("\n✅ Seed data created successfully!\n")
    print("=" * 55)
    print("DEMO LOGIN CREDENTIALS (password: pass123)")
    print("=" * 55)
    accounts = [
        ("superadmin",     "Super Admin",                  "All districts/schools"),
        ("districtadmin1", "Ravi Kumar (District Admin)",  "Chennai District"),
        ("blockadmin1",    "Senthil Raja (Block Admin)",   "Ambattur Block"),
        ("schooladmin1",   "Kavitha Sundaram (SA)",        "GHS Ambattur"),
        ("teacher1",       "Mrs. Lakshmi Priya (Teacher)", "Maths + English"),
        ("teacher2",       "Mr. Ramesh Babu (Teacher)",    "Science"),
        ("student1",       "Arjun Sharma (Student)",       "Class 10-A — has approved report"),
        ("student2",       "Priya Venkat (Student)",       "Class 10-A — submission pending review"),
        ("student3",       "Karthik Rajan (Student)",      "Class 10-B"),
        ("parent1",        "Mr. Sharma (Parent)",          "Parent of Arjun & Priya"),
    ]
    for u, n, scope in accounts:
        print(f"  {u:<18} {n:<32} ({scope})")
    print("=" * 55)
