import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.auth.service import AuthService
from services.auth.repository import AuthRepository
from models import User
from schemas.auth import UserCreate, UserLogin
from common.exceptions import UserNotFoundException, AuthenticationException, ValidationException
from unittest.mock import MagicMock, patch
import bcrypt

def test_auth_service_initialization():
    """Test AuthService initialization"""
    db = MagicMock(spec=Session)
    auth_service = AuthService(db)
    assert auth_service.repository.db == db
    assert isinstance(auth_service, AuthService)

def test_register_user_success():
    """Test successful user registration"""
    db = MagicMock(spec=Session)

    # Mock user data
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="securepassword123",
        role="candidate"
    )

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_email', return_value=None), \
         patch.object(AuthRepository, 'create_user') as mock_create:

        auth_service = AuthService(db)
        result = auth_service.register_user(user_data)

        # Verify repository calls
        AuthRepository.get_user_by_email.assert_called_once(db, "test@example.com")
        mock_create.assert_called_once()

        # Verify result
        assert result["success"] is True
        assert "User registered successfully" in result["message"]

def test_register_user_email_exists():
    """Test user registration with existing email"""
    db = MagicMock(spec=Session)

    # Mock existing user
    existing_user = User(id=1, email="test@example.com", name="Existing User")
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="securepassword123",
        role="candidate"
    )

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_email', return_value=existing_user):
        auth_service = AuthService(db)

        with pytest.raises(ValidationException) as exc_info:
            auth_service.register_user(user_data)

        assert "Email already exists" in str(exc_info.value)

def test_login_user_success():
    """Test successful user login"""
    db = MagicMock(spec=Session)

    # Mock user data
    password = "securepassword123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        password=hashed_password.decode('utf-8'),
        role="candidate"
    )

    login_data = UserLogin(email="test@example.com", password=password)

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_email', return_value=user):
        auth_service = AuthService(db)
        result = auth_service.login_user(login_data)

        # Verify result
        assert result["success"] is True
        assert "Login successful" in result["message"]
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["name"] == "Test User"
        assert result["user"]["role"] == "candidate"

def test_login_user_wrong_password():
    """Test user login with wrong password"""
    db = MagicMock(spec=Session)

    # Mock user data
    password = "securepassword123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        password=hashed_password.decode('utf-8'),
        role="candidate"
    )

    login_data = UserLogin(email="test@example.com", password="wrongpassword")

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_email', return_value=user):
        auth_service = AuthService(db)

        with pytest.raises(AuthenticationException) as exc_info:
            auth_service.login_user(login_data)

        assert "Invalid password" in str(exc_info.value)

def test_login_user_not_found():
    """Test user login with non-existent email"""
    db = MagicMock(spec=Session)

    login_data = UserLogin(email="nonexistent@example.com", password="password123")

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_email', return_value=None):
        auth_service = AuthService(db)

        with pytest.raises(UserNotFoundException) as exc_info:
            auth_service.login_user(login_data)

        assert "User not found" in str(exc_info.value)

def test_get_user_by_id_success():
    """Test getting user by ID successfully"""
    db = MagicMock(spec=Session)

    # Mock user
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        role="candidate"
    )

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_id', return_value=user):
        auth_service = AuthService(db)
        result = auth_service.get_user_by_id(1)

        # Verify result
        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["role"] == "candidate"

def test_get_user_by_id_not_found():
    """Test getting user by ID when user doesn't exist"""
    db = MagicMock(spec=Session)

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_id', return_value=None):
        auth_service = AuthService(db)

        with pytest.raises(UserNotFoundException) as exc_info:
            auth_service.get_user_by_id(999)

        assert "User not found" in str(exc_info.value)

def test_update_user_success():
    """Test updating user successfully"""
    db = MagicMock(spec=Session)

    # Mock existing user
    user = User(
        id=1,
        email="test@example.com",
        name="Old Name",
        role="candidate"
    )

    # Mock update data
    update_data = {"name": "New Name"}

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_id', return_value=user), \
         patch.object(AuthRepository, 'update_user') as mock_update:

        auth_service = AuthService(db)
        result = auth_service.update_user(1, update_data)

        # Verify repository calls
        mock_update.assert_called_once_with(db, user, update_data)

        # Verify result
        assert result["success"] is True
        assert "User updated successfully" in result["message"]

def test_update_user_not_found():
    """Test updating user when user doesn't exist"""
    db = MagicMock(spec=Session)

    # Mock update data
    update_data = {"name": "New Name"}

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_id', return_value=None):
        auth_service = AuthService(db)

        with pytest.raises(UserNotFoundException) as exc_info:
            auth_service.update_user(999, update_data)

        assert "User not found" in str(exc_info.value)

def test_delete_user_success():
    """Test deleting user successfully"""
    db = MagicMock(spec=Session)

    # Mock existing user
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        role="candidate"
    )

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_id', return_value=user), \
         patch.object(AuthRepository, 'delete_user') as mock_delete:

        auth_service = AuthService(db)
        result = auth_service.delete_user(1)

        # Verify repository calls
        mock_delete.assert_called_once_with(db, user)

        # Verify result
        assert result["success"] is True
        assert "User deleted successfully" in result["message"]

def test_delete_user_not_found():
    """Test deleting user when user doesn't exist"""
    db = MagicMock(spec=Session)

    # Mock repository behavior
    with patch.object(AuthRepository, 'get_user_by_id', return_value=None):
        auth_service = AuthService(db)

        with pytest.raises(UserNotFoundException) as exc_info:
            auth_service.delete_user(999)

        assert "User not found" in str(exc_info.value)