from .models import Stage

def get_stages(stage, user):
    """
    根據身分、功能去察看能否使用該功能
    """
    if user.is_authenticated:
        if user.is_superuser:
            return True
        else:
            open_stages = Stage.objects.filter(is_active=True)
            if stage in open_stages:
                return True
            else:
                return False
    else:
        return False