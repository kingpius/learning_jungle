from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def design_system(request):
    palette = [
        ("Canopy Emerald", "#1DA97A", "Primary actions, progress"),
        ("Lilac Glow", "#C89BFF", "Secondary surfaces"),
        ("Deep Violet", "#5E21B6", "Body text, focus"),
        ("Sky Explorer", "#2C7BEA", "Links, info banners"),
        ("Banana Beam", "#F7C948", "Treasure + rewards"),
        ("Jungle Mist", "#F2F5F7", "Backgrounds"),
        ("Tree Trunk", "#8C5A2B", "Dividers"),
    ]
    principles = [
        "Clarity beats cleverness",
        "Simplicity over completeness",
        "One primary action per screen",
        "Treasure unlock is the emotional peak",
    ]
    return render(
        request,
        "core/design_system.html",
        {
            "palette": palette,
            "principles": principles,
        },
    )


def design_system_elements(request):
    answers = [
        {"letter": "A", "text": "12 + 8 = 20", "selected": True},
        {"letter": "B", "text": "12 + 8 = 24", "selected": False},
        {"letter": "C", "text": "12 + 8 = 18", "selected": False},
        {"letter": "D", "text": "12 + 8 = 30", "selected": False},
    ]
    return render(
        request,
        "core/design_system_elements.html",
        {
            "answers": answers,
        },
    )
