from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TreasureChest
from children.models import Child

@login_required
def create_treasure_chest(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)

    if TreasureChest.objects.filter(child=child).exists():
        return redirect("/")  # MVP-safe: prevent duplicates

    if request.method == "POST":
        description = request.POST.get("reward_description")
        value = request.POST.get("reward_value")

        TreasureChest.objects.create(
            parent=request.user,
            child=child,
            reward_description=description,
            reward_value=value,
        )
        return redirect("/")

    return render(request, "rewards/create.html", {"child": child})
