def map_aesthetic(request):
    aesthetic = 'cosmos'
    if request.user.is_authenticated:
        try:
            aesthetic = request.user.profile.map_aesthetic or 'cosmos'
        except Exception:
            pass
    return {'map_aesthetic': aesthetic}
