from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import User

def require_token(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        token = request.data.get('token') or request.query_params.get('token')

        if not token:
            return Response({'error': 'Token manquant'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(token=token)
        except User.DoesNotExist:
            return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)
        
        request.user = user 
        return view_func(self, request, *args, **kwargs)
    
    return wrapper