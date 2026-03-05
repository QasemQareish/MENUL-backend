from apps.accounts.models import User

def create_internal_user(data: dict) -> User:
    """
    Create an internal user (owner, staff).
    Validates FK relations according to role.
    """
    role = data.get("role")
    restaurant = data.get("restaurant")
    branch = data.get("branch")
    kitchen = data.get("kitchen")

    # Validation
    if role == "owner" and not restaurant:
        raise ValueError("Owner must be assigned to a restaurant")

    if role == "branch_manager":
        if not branch:
            raise ValueError("Branch Manager must be assigned to a branch")
        if not branch.restaurant:
            raise ValueError("Branch must belong to a restaurant")

    if role in ["kitchen_manager", "chef"]:
        if not kitchen:
            raise ValueError(f"{role.replace('_',' ').title()} must be assigned to a kitchen")
        if not kitchen.branch or not kitchen.branch.restaurant:
            raise ValueError("Kitchen must be linked to a branch and a restaurant")

    if role == "waiter":
        if not branch:
            raise ValueError("Waiter must be assigned to a branch")
        if not branch.restaurant:
            raise ValueError("Branch must belong to a restaurant")

    # Create user
    password = data.pop("password", "0000")  # Default password
    user = User.objects.create(**data)
    user.set_password(password)
    user.save()
    return user
