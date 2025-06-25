def profile_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return "myauth/user_{pk}/avatar/{filename}".format(
        pk=instance.user.pk, filename=filename
    )
