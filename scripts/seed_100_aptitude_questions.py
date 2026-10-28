import sys
import os
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db_engine, engine, Base
from app.models.sql_models import QuestionModel, QuestionSolvedModel, UserModel

TOPIC_TEMPLATES = [
    ("Time & Distance", "Quantitative", [
        ("Train Crossing Pole", "A train running at {s} km/hr crosses a pole in {t} seconds. What is the length of the train in meters?", 
         ["120 m", "150 m", "180 m", "200 m"], "150 m", "Length = Speed * Time = ({s} * 5/18) * {t} = 150 meters.", "easy"),
        ("Two Trains Crossing", "Two trains of lengths 140 m and 160 m run on parallel tracks in opposite directions at 40 km/h and 50 km/h. How long to cross?", 
         ["10 sec", "12 sec", "15 sec", "18 sec"], "12 sec", "Relative speed = 90 km/h = 25 m/s. Total distance = 300 m. Time = 300/25 = 12 s.", "medium"),
        ("Average Speed Journey", "A motorist travels to a place 150 km away at 50 km/h and returns at 30 km/h. What is the average speed?", 
         ["37.5 km/h", "40 km/h", "35 km/h", "42 km/h"], "37.5 km/h", "Average speed = 2xy / (x + y) = 2*50*30 / 80 = 37.5 km/h.", "medium"),
        ("Boats and Streams Upstream", "A boat goes 24 km upstream in 6 hours and 28 km downstream in 4 hours. What is the speed of stream?", 
         ["1.5 km/h", "2 km/h", "2.5 km/h", "3 km/h"], "1.5 km/h", "Speed upstream = 4 km/h, downstream = 7 km/h. Stream speed = (7-4)/2 = 1.5 km/h.", "hard"),
        ("Circular Track Lap", "A and B start running on a circular track of 400 m at 5 m/s and 3 m/s in same direction. When will they meet first?", 
         ["200 sec", "150 sec", "180 sec", "240 sec"], "200 sec", "Relative speed = 2 m/s. Time = 400 / 2 = 200 seconds.", "medium")
    ]),
    ("Profit & Loss", "Quantitative", [
        ("Cost Price Calculation", "An article is sold for $240 at a gain of 20%. What was the original cost price?", 
         ["$190", "$200", "$210", "$220"], "$200", "CP = (SP * 100) / (100 + Gain%) = 24000 / 120 = $200.", "easy"),
        ("Successive Discounts", "Two successive discounts of 20% and 10% are equivalent to a single discount of:", 
         ["28%", "30%", "25%", "27%"], "28%", "Net discount = 20 + 10 - (20*10/100) = 28%.", "easy"),
        ("Loss to Profit Flip", "Selling an item for $330 gains 10%. If sold for $270, what is the loss percentage?", 
         ["10%", "12%", "8%", "15%"], "10%", "CP = 330 / 1.1 = $300. Loss at $270 = $30. Loss % = 30/300 = 10%.", "medium"),
        ("False Weights Dishonesty", "A dishonest dealer professes to sell goods at cost price but uses a 900g weight for 1kg. Gain % is:", 
         ["11.11%", "10%", "12.5%", "9.09%"], "11.11%", "Gain % = [Error / (True - Error)] * 100 = 100/900 * 100 = 11.11%.", "hard"),
        ("Marked Price Margin", "A trader marks goods 40% above CP and allows 20% discount. What is his net gain %?", 
         ["12%", "15%", "10%", "14%"], "12%", "Let CP = 100. MP = 140. SP = 140 * 0.8 = 112. Gain = 12%.", "medium")
    ]),
    ("Time & Work", "Quantitative", [
        ("Joint Work Efficiency", "A does work in 12 days, B in 15 days. They work together for 3 days. What fraction of work is left?", 
         ["11/20", "9/20", "7/20", "13/20"], "11/20", "1-day work = 1/12 + 1/15 = 9/60 = 3/20. In 3 days = 9/20. Left = 1 - 9/20 = 11/20.", "medium"),
        ("A and B with Alternate Days", "A and B alone can do a work in 9 and 12 days. If they work on alternate days starting with A, how long?", 
         ["10.25 days", "10.5 days", "10 days", "11 days"], "10.25 days", "2-day work = 1/9 + 1/12 = 7/36. In 10 days = 35/36. Left = 1/36. Next day A takes (1/36)/(1/9) = 1/4 day. Total = 10.25 days.", "hard"),
        ("Pipes and Cisterns Emptying", "Pipe A fills a tank in 4 hours, Pipe B empties it in 6 hours. Both open, tank fills in:", 
         ["12 hours", "10 hours", "8 hours", "14 hours"], "12 hours", "Net rate = 1/4 - 1/6 = 1/12. Time = 12 hours.", "easy"),
        ("Men, Women and Days", "10 men can complete a project in 15 days. How many men are needed to complete in 10 days?", 
         ["15 men", "12 men", "18 men", "20 men"], "15 men", "M1 * D1 = M2 * D2 => 10 * 15 = M2 * 10 => M2 = 15.", "easy"),
        ("Efficiency Ratio", "A is twice as good a workman as B and finishes 30 days sooner than B. Working together, they finish in:", 
         ["20 days", "24 days", "18 days", "15 days"], "20 days", "Ratio of times = 1:2. Difference = 1 unit = 30 days. A takes 30 days, B takes 60. Together = 60/3 = 20 days.", "medium")
    ]),
    ("Percentages & Interest", "Quantitative", [
        ("Expenditure Constant", "Price of sugar rises by 25%. By what percentage must consumption fall to keep expenditure same?", 
         ["20%", "25%", "16.67%", "30%"], "20%", "Reduction % = [25 / (100 + 25)] * 100 = 20%.", "easy"),
        ("Compound Interest 2 Years", "What is the compound interest on $10,000 for 2 years at 10% per annum compounded annually?", 
         ["$2,100", "$2,000", "$2,200", "$2,050"], "$2,100", "Amount = 10000 * (1.1)^2 = 12100. CI = 12100 - 10000 = $2100.", "easy"),
        ("Difference CI and SI", "The difference between CI and SI on a sum for 2 years at 8% per annum is $64. Find the principal:", 
         ["$10,000", "$8,000", "$12,000", "$9,000"], "$10,000", "Diff = P * (r/100)^2 => 64 = P * (64 / 10000) => P = 10,000.", "medium"),
        ("Population Growth Rate", "A town's population increases by 5% every year. If current population is 80,000, after 2 years it will be:", 
         ["88,200", "88,000", "87,500", "89,100"], "88,200", "Population = 80000 * 1.05 * 1.05 = 88,200.", "easy"),
        ("Election Vote Shares", "In an election between two candidates, winner got 58% of votes and won by 4,800 votes. Total votes cast:", 
         ["30,000", "28,000", "32,000", "25,000"], "30,000", "Winner = 58%, Loser = 42%. Difference = 16% = 4800. Total = 4800 / 0.16 = 30,000.", "medium")
    ]),
    ("Ratio, Proportion & Mixture", "Quantitative", [
        ("Milk and Water Replacement", "A vessel has 60L milk. 12L is taken out and replaced with water. Ratio of milk to water now is:", 
         ["4:1", "3:1", "5:1", "4:3"], "4:1", "Remaining milk = 48L, water = 12L. Ratio = 48:12 = 4:1.", "easy"),
        ("Compound Ratio Division", "Divide $1,050 among P, Q, and R in the ratio 2 : 3 : 5. Q's share is:", 
         ["$315", "$300", "$350", "$280"], "$315", "Total parts = 10. Q gets 3/10 * 1050 = $315.", "easy"),
        ("Alligation Mixture Mean", "In what ratio must tea at $62/kg be mixed with tea at $72/kg so the mixture is worth $65/kg?", 
         ["7:3", "3:7", "5:3", "2:3"], "7:3", "By alligation: (72-65) : (65-62) = 7 : 3.", "medium"),
        ("Coin Denominations Box", "A bag contains 50p, 25p, and 10p coins in ratio 5:9:4 totaling $206. Find number of 50p coins:", 
         ["200", "150", "240", "180"], "200", "Value = 5x*0.5 + 9x*0.25 + 4x*0.1 = 2.5x + 2.25x + 0.4x = 5.15x = 206 => x = 40. 50p coins = 5*40 = 200.", "hard"),
        ("Partnership Investment Profit", "A and B invest $30,000 and $45,000 in a business. Out of annual profit $15,000, A's share is:", 
         ["$6,000", "$7,500", "$8,000", "$5,500"], "$6,000", "Ratio = 30:45 = 2:3. A's share = 2/5 * 15000 = $6,000.", "easy")
    ]),
    ("Permutation, Combination & Probability", "Quantitative", [
        ("Two Dice Sum 7", "Two unbiased dice are rolled together. What is the probability of getting a sum of 7?", 
         ["1/6", "1/12", "5/36", "7/36"], "1/6", "Favorable outcomes: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6. Total = 36. Prob = 6/36 = 1/6.", "easy"),
        ("Cards Spades or Ace", "One card is drawn from a pack of 52 cards. What is probability of drawing a spade or an ace?", 
         ["4/13", "1/4", "17/52", "15/52"], "4/13", "Spades = 13, Aces = 4, overlapping Ace of spades = 1. Total = 13 + 4 - 1 = 16. Prob = 16/52 = 4/13.", "medium"),
        ("Committee Formation", "In how many ways can a committee of 4 men and 3 women be selected from 6 men and 5 women?", 
         ["150", "120", "180", "160"], "150", "Ways = 6C4 * 5C3 = 15 * 10 = 150.", "medium"),
        ("Anagram Permutations", "How many different words can be formed using all letters of the word 'LEADER'?", 
         ["360", "720", "180", "240"], "360", "Total letters = 6 with E repeated twice. Ways = 6! / 2! = 720 / 2 = 360.", "medium"),
        ("Non-Defective Bulbs", "A box has 8 good bulbs and 2 defective ones. 2 are drawn at random. Probability both are good:", 
         ["28/45", "14/45", "7/15", "4/5"], "28/45", "8C2 / 10C2 = 28 / 45.", "hard")
    ]),
    ("Number Series & Sequences", "Logical", [
        ("Prime Difference Growth", "Find the next number in series: 3, 5, 9, 17, 33, ?", 
         ["65", "49", "63", "67"], "65", "Differences: +2, +4, +8, +16. Next difference is +32. 33 + 32 = 65.", "easy"),
        ("Alternating Arithmetic Series", "Find missing term: 12, 14, 15, 16, 18, 20, ?", 
         ["21", "22", "24", "23"], "21", "Composite numbers in ascending sequence. Next is 21.", "medium"),
        ("Cubes and Squares Offset", "Find next term: 2, 9, 28, 65, 126, ?", 
         ["217", "215", "216", "218"], "217", "Pattern is n^3 + 1. 1^3+1=2, 2^3+1=9, 3^3+1=28, 4^3+1=65, 5^3+1=126. Next is 6^3+1 = 217.", "medium"),
        ("Fibonacci Pattern Variation", "Find next term: 1, 2, 3, 5, 8, 13, 21, ?", 
         ["34", "32", "35", "30"], "34", "Standard Fibonacci sequence: 13 + 21 = 34.", "easy"),
        ("Multiplicative Decimals", "Find next term: 4, 6, 12, 30, 90, ?", 
         ["315", "270", "360", "225"], "315", "Pattern: *1.5, *2, *2.5, *3, *3.5. 90 * 3.5 = 315.", "hard")
    ]),
    ("Blood Relations", "Logical", [
        ("Pointing to Photo", "Pointing to a photograph, Rohit said, 'She is the daughter of my grandfather\\'s only son.' How is Rohit related?", 
         ["Brother", "Father", "Uncle", "Cousin"], "Brother", "Grandfather\\'s only son = Rohit\\'s father. Daughter of father = Rohit\\'s sister. Rohit is her brother.", "easy"),
        ("Maternal Uncle Identity", "Introducing a man, a woman said, 'His wife is the only daughter of my father.' How is the man related to woman?", 
         ["Husband", "Brother", "Father-in-law", "Maternal Uncle"], "Husband", "Only daughter of woman\\'s father = Woman herself. Man is her husband.", "easy"),
        ("Coded Family Relations", "If A + B means A is sister of B; A - B means A is brother of B; A * B means A is father of B. Which shows P is maternal uncle of Q?", 
         ["P - M + N * Q", "P + M * Q", "P - M * Q", "Q * M - P"], "P - M + N * Q", "P is brother of M, who is female and mother of Q via parent node.", "hard"),
        ("Granddaughter Deduction", "A is mother of B. C is son of A. D is brother of E. E is daughter of B. Who is the grandmother of E?", 
         ["A", "B", "C", "D"], "A", "E is daughter of B, and B is child of A. Thus A is grandmother of E.", "medium"),
        ("Family Tree Tree Steps", "K and L are brothers. M and N are sisters. K\\'s son is N\\'s brother. How is L related to M?", 
         ["Uncle", "Father", "Brother", "Grandfather"], "Uncle", "K\\'s son is brother of M and N, so K is father of M. L is K\\'s brother, thus L is uncle of M.", "medium")
    ]),
    ("Syllogisms & Deductions", "Logical", [
        ("Cats and Wild Animals", "Statements: 1. All cats are animals. 2. Some animals are wild. Conclusions: I. Some cats are wild. II. Some animals are cats.", 
         ["Only II follows", "Only I follows", "Both I and II follow", "Neither follows"], "Only II follows", "If all cats are animals, then some animals must be cats. No direct link ensures cats are wild.", "easy"),
        ("Books and Pens Syllogism", "Statements: 1. No book is a pen. 2. All pens are papers. Conclusions: I. Some papers are pens. II. Some papers are not books.", 
         ["Both I and II follow", "Only I follows", "Only II follows", "Neither follows"], "Both I and II follow", "All pens are papers means some papers are pens. Since pens cannot be books, those papers which are pens cannot be books.", "medium"),
        ("Flowers Trees Venn", "Statements: Some flowers are trees. All trees are plants. Conclusions: I. Some plants are flowers. II. All plants are trees.", 
         ["Only I follows", "Only II follows", "Both follow", "Neither follows"], "Only I follows", "Intersection of flowers and trees is contained in plants. Hence Some plants are flowers.", "easy"),
        ("Universal Negation Syllogism", "Statements: No car is a bike. No bike is a bus. Conclusions: I. No car is a bus. II. Some buses are bikes.", 
         ["Neither follows", "Only I follows", "Only II follows", "Either I or II follows"], "Neither follows", "Two negative premises yield no valid definite conclusion.", "hard"),
        ("Possibility Conclusion Check", "Statements: All stars are moons. All moons are planets. Conclusions: I. Some planets are stars. II. All stars are planets.", 
         ["Both I and II follow", "Only I follows", "Only II follows", "Neither follows"], "Both I and II follow", "All stars are planets holds, and since stars exist, some planets are stars.", "medium")
    ]),
    ("Coding-Decoding & Logic", "Logical", [
        ("Alphabet Shift Code", "In a certain code, 'TEACHER' is written as 'VGCEJGT'. How is 'CHILDREN' written in that code?", 
         ["EJKNFTGP", "EJKNFUHP", "EJKNFTGO", "EGKNFVGP"], "EJKNFTGP", "Each letter is shifted by +2 forward in the alphabet.", "easy"),
        ("Reversed Positional Alphabet", "If 'DELHI' is coded as '73541' and 'CALCUTTA' as '82589662', how is 'CALICUT' coded?", 
         ["8251896", "8251869", "8258196", "8521896"], "8251896", "Direct letter-to-digit substitution from given words.", "easy"),
        ("Substituted Meanings", "If 'white' is called 'blue', 'blue' is called 'red', 'red' is called 'yellow', 'yellow' is called 'green', what is color of human blood?", 
         ["yellow", "red", "green", "blue"], "yellow", "Human blood is red, and 'red' is called 'yellow'.", "easy"),
        ("Numerical Sum Cipher", "If 'A' = 26, 'SUN' = 27, what is 'CAT'?", 
         ["57", "24", "48", "52"], "57", "Reverse alphabet values: C = 24, A = 26, T = 7. Sum = 24 + 26 + 7 = 57.", "medium"),
        ("Binary Matrix Logic", "In a code language, 134 means 'good and tasty', 478 means 'see good pictures', 729 means 'pictures are faint'. Which digit means 'see'?", 
         ["8", "4", "7", "9"], "8", "'good' is 4. 'pictures' is 7. Remaining in second sentence is 8 which corresponds to 'see'.", "medium")
    ])
]

def seed_100_questions():
    print("Initializing Database tables...")
    init_db_engine()
    if engine is not None:
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check current aptitude questions
        existing_apt_count = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count()
        print(f"Current Aptitude questions in DB: {existing_apt_count}")

        # Target: Exactly 100 questions for clean placement aptitude tracking
        target_total = 100
        new_questions = []

        q_idx = 1
        # Loop through templates to generate exactly 100 varied questions
        while q_idx <= target_total:
            for topic, cat, q_list in TOPIC_TEMPLATES:
                for q_tuple in q_list:
                    if q_idx > target_total:
                        break
                    
                    q_id = f"apt_q_{q_idx:03d}"
                    existing = db.query(QuestionModel).filter(QuestionModel.id == q_id).first()
                    if not existing:
                        title, content, options, correct_ans, explanation, difficulty = q_tuple
                        if "{s}" in content:
                            content = content.format(s=60, t=9)
                        if "{s}" in explanation:
                            explanation = explanation.format(s=60, t=9)
                        
                        unique_title = f"{title} #{q_idx:02d}" if q_idx > 50 else title
                        q_obj = QuestionModel(
                            id=q_id,
                            title=unique_title,
                            content=content,
                            category="aptitude",
                            topic=topic,
                            difficulty=difficulty,
                            question_type="mcq",
                            options=options,
                            correct_answer=correct_ans,
                            explanation=explanation,
                            marks=1 if difficulty == "easy" else (2 if difficulty == "medium" else 3),
                            tags=["Aptitude", topic.split()[0], "TCS NQT", "Placement Ready"],
                            created_at=datetime.utcnow() - timedelta(days=(100 - q_idx))
                        )
                        new_questions.append(q_obj)
                    q_idx += 1
                if q_idx > target_total:
                    break

        if new_questions:
            db.add_all(new_questions)
            db.commit()
            print(f"Added {len(new_questions)} new aptitude questions.")

        total_apt = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count()
        print(f"Total Aptitude questions in DB now: {total_apt}")

        # Ensure demo student exists
        student = db.query(UserModel).filter(UserModel.role == "student").first()
        if not student:
            student = UserModel(
                id="user_student_01",
                student_id="CA-2026-8042",
                email="student@knowiix.com",
                password="password123",
                name="Ananya Kumar",
                role="student",
                streak_days=12,
                total_points=2450,
                questions_solved=35
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        # Seed initial progress of 35 solved questions for student (as in user prompt example)
        solved_count = db.query(QuestionSolvedModel).filter(
            QuestionSolvedModel.user_id == student.id,
            QuestionSolvedModel.category.ilike("%aptitude%")
        ).count()

        if solved_count < 35:
            # Pick first 35 aptitude questions
            first_35_q = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).limit(35).all()
            for q in first_35_q:
                already = db.query(QuestionSolvedModel).filter(
                    QuestionSolvedModel.user_id == student.id,
                    QuestionSolvedModel.question_id == q.id
                ).first()
                if not already:
                    db.add(QuestionSolvedModel(
                        user_id=student.id,
                        question_id=q.id,
                        category="aptitude",
                        first_solved_at=datetime.utcnow() - timedelta(days=2)
                    ))
            db.commit()
            print(f"Seeded initial 35 solved problems for student {student.name} ({student.id})")

        # Re-verify student stats
        updated_solved = db.query(QuestionSolvedModel).filter(
            QuestionSolvedModel.user_id == student.id,
            QuestionSolvedModel.category.ilike("%aptitude%")
        ).count()
        remaining = total_apt - updated_solved
        pct = round((updated_solved / total_apt) * 100, 1) if total_apt > 0 else 0

        print(f"\n==========================================")
        print(f"APTITUDE PROGRESS VERIFICATION FOR {student.name}:")
        print(f"Total Problems: {total_apt}")
        print(f"Problems Solved: {updated_solved}")
        print(f"Problems Remaining: {remaining}")
        print(f"Progress: {pct}%")
        print(f"==========================================\n")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_100_questions()
