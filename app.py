import flet as ft
import random
from categories import categories

def main(page: ft.Page):
    page.title = "لعبة برة السالفة"
    page.window.width = 400
    page.window.height = 800

    # Set the alignment for the entire page content to be centered
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Initialize state variables if they don't exist
    if not hasattr(page, "players"):
        page.players = []
        page.num_players = 0
        page.selected_category = None
        page.roles = {}
        page.bara_al_salfa = None
        page.game_word = None
        page.current_player_index = 0
        page.votes = {}
        page.round_scores = {}
        page.global_scores = {}
        page.guess_word_options = []
        page.question_pairs = []
        page.current_pair_index = 0
        page.vote_index = 0
        page.guess_result = ''

    # Routing logic simplified
    page_views = {
        "home": home_page,
        "input_players": input_players_page,
        "select_category": select_category_page,
        "show_role": show_role_page,
        "display_role": display_role_page,
        "question_or_vote": question_or_vote_page,
        "question_time": question_time_page,
        "voting": voting_page,
        "voting_results": voting_results_page,
        "bara_guess": bara_guess_page,
        "total_scores": total_scores_page
    }

    # Start with the home page
    current_view = page_views.get(page.route, home_page)
    current_view(page)

def set_page(page: ft.Page, route: str):
    page.route = route
    page.controls.clear()  # Clear previous page content
    main(page)

def initialize_players(page: ft.Page):
    page.players = ['' for _ in range(page.num_players)]
    page.global_scores = {player: 0 for player in page.players}

def home_page(page: ft.Page):
    # Initialize num_players with None or an invalid value
    page.num_players = None

    # Function to update the button state
    def update_button_state(e):
        page.num_players = int(e.control.value)
        start_button.disabled = page.num_players is None
        page.update()

    page.add(ft.Text("لعبة برة السالفة", size=35, weight=ft.FontWeight.BOLD, text_align="center"))
    page.add(ft.Text("مرحبًا بك في لعبة برة السالفة! ابدأ بتحديد عدد اللاعبين.", size=20, text_align="center"))

    num_players_dropdown = ft.Dropdown(
        label="أدخل عدد اللاعبين:",
        options=[ft.dropdown.Option(str(i), str(i)) for i in range(3, 13)],
        on_change=update_button_state,  # Call the update function on change
    ) 
    page.add(num_players_dropdown)

    # Initially disable the button
    start_button = ft.ElevatedButton(
        text="ابدأ اللعبة",
        on_click=lambda _: (initialize_players(page), set_page(page, "input_players")),
        disabled=True,  # Disable button initially
    )
    page.add(start_button)

    # Add an initial update to disable the button if no selection is made
    page.update()



def input_players_page(page: ft.Page):
    page.add(ft.Text("أدخل أسماء اللاعبين", size=30, weight=ft.FontWeight.BOLD))
    
    # Initialize the players' names and the button state
    def update_button_state():
        # Enable the button only if all player names are filled
        next_button.disabled = not all(name.strip() for name in page.players)
        page.update()

    # Create text fields for each player and update the state on change
    for i in range(page.num_players):
        player_input = ft.TextField(
            label=f"اسم اللاعب رقم {i+1}:",
            value=page.players[i],
            on_change=lambda e, i=i: (page.players.__setitem__(i, e.control.value), update_button_state()),
        )
        page.add(player_input)

    next_button = ft.ElevatedButton(
        text="التالي",
        on_click=lambda _: set_page(page, "select_category"),
        disabled=True,  # Initially disabled
    )
    page.add(next_button)

    page.update()  # Ensure the button state is correctly initialized


def select_category_page(page: ft.Page):
    page.add(ft.Text("اختر القائمة", size=30, weight=ft.FontWeight.BOLD))

    def update_button_state(e):
        page.selected_category = e.control.value
        confirm_button.disabled = not page.selected_category  # Disable if no category selected
        page.update()

    category_select = ft.Dropdown(
        label="اختر قائمة الكلمات:",
        options=[ft.dropdown.Option(key, key) for key in categories.keys()],
        on_change=update_button_state,  # Update button state on change
    )
    page.add(category_select)

    confirm_button = ft.ElevatedButton(
        text="تأكيد القائمة",
        on_click=lambda _: assign_roles_and_word(page),
        disabled=True,  # Initially disabled
    )
    page.add(confirm_button)

    page.update()  # Ensure the button state is correctly initialized

def assign_roles_and_word(page: ft.Page):
    page.game_word = random.choice(categories[page.selected_category])
    page.bara_al_salfa = random.choice(page.players)
    page.roles = {
        player: 'برة السالفة' if player == page.bara_al_salfa else 'داخل السالفة'
        for player in page.players
    }
    page.round_scores = {player: 0 for player in page.players}  # Initialize scores for all players
    page.question_pairs = generate_question_pairs(page.players)
    set_page(page, 'show_role')

def generate_question_pairs(players):
    random.shuffle(players)
    return [(players[i], players[(i + 1) % len(players)]) for i in range(len(players))]

def show_role_page(page: ft.Page):
    current_player = page.players[page.current_player_index]
    page.add(ft.Text(f"أعط الشاشة إلى: {current_player}", size=25))
    next_button = ft.ElevatedButton(
        text="عرض الدور",
        on_click=lambda _: set_page(page, "display_role"),
    )
    page.add(next_button)

def display_role_page(page: ft.Page):
    current_player = page.players[page.current_player_index]
    role = page.roles[current_player]
    page.add(ft.Text(f"مرحبا {current_player}، دورك هو: {role}", size=20))
    
    if role == 'داخل السالفة':
        page.add(ft.Text(f"الفئة: {page.selected_category}", size=25))
        page.add(ft.Text(f"الكلمة السرية هي: {page.game_word}", size=35, weight=ft.FontWeight.BOLD, text_align="center"))
    else:
        page.add(ft.Text(f"الفئة: {page.selected_category}", size=25))
        page.add(ft.Text("مهمتك أن توضح للمجموعة أنك تعرف الموضوع بالإجابة بشكل عام.", size=35, weight=ft.FontWeight.BOLD, text_align="center"))

    next_button = ft.ElevatedButton(
        text="التالي",
        on_click=lambda _: (increment_player_index(page), set_page(page, 'show_role') if page.current_player_index < len(page.players) else set_page(page, 'question_or_vote')),
    )
    page.add(next_button)

def increment_player_index(page: ft.Page):
    page.current_player_index += 1

def question_or_vote_page(page: ft.Page):
    page.add(ft.Text("ماذا تريد أن تفعل الآن؟ يجب على اللاعبين الآن أن يطرحوا أسئلة أولا ومن ثم التصويت أو اختيار جولة أسئلة جديدة.", size=20, text_align="center"))
    question_button = ft.ElevatedButton(
        text="بدء جولة أسئلة جديدة",
        on_click=lambda _: (reset_for_questions(page), set_page(page, 'question_time')),
    )
    vote_button = ft.ElevatedButton(
        text="البدء في التصويت",
        on_click=lambda _: set_page(page, 'voting'),
    )
    page.add(question_button)
    page.add(vote_button)

def reset_for_questions(page: ft.Page):
    page.question_pairs = generate_question_pairs(page.players)
    page.current_pair_index = 0

def question_time_page(page: ft.Page):
    if page.current_pair_index < len(page.question_pairs):
        current_pair = page.question_pairs[page.current_pair_index]
        page.add(ft.Text(f"{current_pair[0]} قم بسؤال {current_pair[1]}", size=25))
        
        next_button = ft.ElevatedButton(
            text="التالي",
            on_click=lambda _: (
                increment_pair_index(page),
                set_page(page, 'question_time') if page.current_pair_index < len(page.question_pairs) else set_page(page, 'question_or_vote')
            ),
        )
        page.add(next_button)
    else:
        vote_button = ft.ElevatedButton(
            text="الانتقال إلى التصويت",
            on_click=lambda _: set_page(page, 'voting'),
        )
        page.add(vote_button)

def increment_pair_index(page: ft.Page):
    page.current_pair_index += 1

def voting_page(page: ft.Page):
    current_player = page.players[page.vote_index]
    page.add(ft.Text(f"الآن دور {current_player} للتصويت.", size=20))

    for player in page.players:
        if player != current_player:
            vote_button = ft.ElevatedButton(
                text=f"تصويت ضد {player}",
                on_click=lambda _, p=player: cast_vote(page, current_player, p),
            )
            page.add(vote_button)

def cast_vote(page: ft.Page, voter: str, voted_for: str):
    page.votes[voter] = voted_for
    if page.vote_index < len(page.players) - 1:
        page.vote_index += 1
        set_page(page, 'voting')
    else:
        set_page(page, 'voting_results')

def voting_results_page(page: ft.Page):
    page.add(ft.Text("نتائج التصويت", size=30, weight=ft.FontWeight.BOLD))
    bara_al_salfa = page.bara_al_salfa

    for player, voted_for in page.votes.items():
        page.add(ft.Text(f"{player} صوّت ضد {voted_for}", size=20))

    page.add(ft.Text(f"برة السالفة هو {bara_al_salfa}", size=30, weight=ft.FontWeight.BOLD))

    for player, voted_for in page.votes.items():
        if voted_for == bara_al_salfa:
            page.round_scores[player] = page.round_scores.get(player, 0) + 5
            page.add(ft.Text(f"{player} حصل على 5 نقاط لتصويته الصحيح", size=20))

    next_button = ft.ElevatedButton(
        text="التالي",
        on_click=lambda _: set_page(page, 'bara_guess'),
    )
    page.add(next_button)

def bara_guess_page(page: ft.Page):
    page.add(ft.Text(f"الآن، دور {page.bara_al_salfa} لتخمين الكلمة السرية.", size=25))
    generate_guess_options(page)
    
    for word in page.guess_word_options:
        guess_button = ft.ElevatedButton(
            text=word,
            on_click=lambda e, w=word: handle_bara_guess(page, w),
        )
        page.add(guess_button)

def generate_guess_options(page: ft.Page):
    category_words = categories[page.selected_category]
    page.guess_word_options = random.sample(
        [word for word in category_words if word != page.game_word], 7
    ) + [page.game_word]
    random.shuffle(page.guess_word_options)

def handle_bara_guess(page: ft.Page, guess: str):
    # Check if the guessed word is correct
    if guess == page.game_word:
        page.round_scores[page.bara_al_salfa] += 5
        page.guess_result = "صحيح! لقد خمنت الكلمة السرية بشكل صحيح وحصلت على 5 نقاط إضافية."
    else:
        page.guess_result = "خطأ! لم تخمن الكلمة السرية بشكل صحيح."
    
    set_page(page, 'total_scores')

def total_scores_page(page: ft.Page):
    page.controls.clear()

    # Display the secret word
    page.add(ft.Text(f"الكلمة السرية كانت: {page.game_word}", size=30, weight=ft.FontWeight.BOLD))
    
    # Display whether the guess was correct or wrong
    page.add(ft.Text(page.guess_result, size=20, color=ft.colors.GREEN if "صحيح" in page.guess_result else ft.colors.RED))

    # Display the round scores
    page.add(ft.Text("النقاط الكلية للجولة:", size=30, weight=ft.FontWeight.BOLD))
    for player, score in page.round_scores.items():
        page.global_scores[player] = page.global_scores.get(player, 0) + score
        page.add(ft.Text(f"{player}: {score} نقطة (الجولة الحالية)", size=20))

    # Display the global scores
    page.add(ft.Text("النقاط الكلية لجميع الجولات:", size=30, weight=ft.FontWeight.BOLD))
    for player in page.players:
        score = page.global_scores.get(player, 0)
        page.add(ft.Text(f"{player}: {score} نقطة (إجمالي النقاط)", size=20))

    # Button to start a new round
    next_button = ft.ElevatedButton(
        text="لعب جولة أخرى",
        on_click=lambda _: (reset_for_new_round(page), set_page(page, 'select_category')),
    )
    page.add(next_button)

    page.update()

def reset_for_new_round(page: ft.Page):
    # Reset variables for the new round
    page.current_player_index = 0
    page.current_pair_index = 0
    page.vote_index = 0
    page.votes = {}
    page.round_scores = {player: 0 for player in page.players}

ft.app(target=main)
