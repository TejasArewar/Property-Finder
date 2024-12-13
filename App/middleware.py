from django.shortcuts import render, redirect

def auth_middleware(get_response):
    restricted_paths = ['/property/', '/contact/', '/my_adds/']
    open_paths = ['/login/', '/signup/', '/home/']

    def middleware(request):
        user_id = request.session.get('id')

        if request.path.startswith('/edit_prop/') and user_id is None:
            return redirect('/login/')
        
        if request.path.startswith('/delete_prop/') and user_id is None:
            return redirect('/login/')
        
        if request.path in restricted_paths and user_id is None:
            return redirect('/login/')

        if request.path in open_paths and user_id is not None:
            return redirect('/property/')

        response = get_response(request)
        return response

    return middleware
