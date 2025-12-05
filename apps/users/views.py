from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from apps.users.serializers import (
    UserSerializer, UserSettingsSerializer, UserManagementSerializer,
    CreateUserSerializer, RoleChoicesSerializer, CompanySerializer
)
from apps.users.models import UserSettings, Company

User = get_user_model()


class UserManagementView(APIView):
    """API for managing users - only accessible by admins"""
    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)
        if not request.user.can_manage_users():
            self.permission_denied(request, message="אין לך הרשאה לנהל משתמשים")

    def get(self, request):
        """List all users (for admin users)"""
        # Filter by company if user has one
        if request.user.company:
            users = User.objects.filter(company=request.user.company)
        elif request.user.is_superuser or request.user.role == 'SUPER_ADMIN':
            users = User.objects.all()
        else:
            users = User.objects.filter(company=request.user.company)

        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new user"""
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            # If current user has a company, assign the new user to the same company
            if request.user.company and 'company' not in request.data:
                serializer.validated_data['company'] = request.user.company

            user = serializer.save()
            return Response(
                UserManagementSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """API for managing a specific user"""
    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)
        if not request.user.can_manage_users():
            self.permission_denied(request, message="אין לך הרשאה לנהל משתמשים")

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get a specific user"""
        user = self.get_user(pk)
        if not user:
            return Response(
                {'message': 'משתמש לא נמצא'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserManagementSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a user"""
        user = self.get_user(pk)
        if not user:
            return Response(
                {'message': 'משתמש לא נמצא'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserManagementSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Deactivate a user (soft delete)"""
        user = self.get_user(pk)
        if not user:
            return Response(
                {'message': 'משתמש לא נמצא'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent deleting yourself
        if user.id == request.user.id:
            return Response(
                {'message': 'לא ניתן למחוק את המשתמש שלך'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = False
        user.save()
        return Response({'message': 'המשתמש נוסף לארכיון'}, status=status.HTTP_200_OK)


class RoleChoicesView(APIView):
    """Get available user roles"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = [
            {'value': role[0], 'label': role[1]}
            for role in User.USER_ROLES
        ]
        return Response(roles)


class CurrentUserView(APIView):
    """Get current user with full details and permissions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserManagementSerializer(request.user)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Public registration endpoint - creates a new user with SUPER_ADMIN role
    if no users exist, otherwise creates a regular USER.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    username = request.data.get('username', email)
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    if not email or not password:
        return Response(
            {'message': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'message': 'User with this email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # First user becomes SUPER_ADMIN
    is_first_user = User.objects.count() == 0
    role = 'SUPER_ADMIN' if is_first_user else 'USER'

    # Create the user
    user = User.objects.create_user(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_staff=is_first_user,
        is_superuser=is_first_user
    )

    # Create token
    token, _ = Token.objects.get_or_create(user=user)

    # Serialize user data
    serializer = UserSerializer(user)

    return Response({
        'token': token.key,
        'user': serializer.data,
        'message': 'Registration successful' + (' - You are the admin!' if is_first_user else '')
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'message': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Try to find user by email or username
    user = None
    # First try by email field
    user_obj = User.objects.filter(email=email).first()
    if user_obj:
        user = authenticate(username=user_obj.email, password=password)

    # If not found by email, try by username field
    if user is None:
        user_obj = User.objects.filter(username=email).first()
        if user_obj:
            user = authenticate(username=user_obj.email, password=password)

    if user is None:
        return Response(
            {'message': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    
    # Serialize user data
    serializer = UserSerializer(user)
    
    return Response({
        'token': token.key,
        'user': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_settings_view(request):
    """Get or update user settings"""
    # Get or create settings for current user
    settings = UserSettings.get_or_create_for_user(request.user)

    if request.method == 'GET':
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = UserSettingsSerializer(settings, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
