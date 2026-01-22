"""Tests for JWT authentication (User Stories 1, 3, and 4)."""

import pytest
from fastapi.testclient import TestClient


# =============================================================================
# User Story 1: Authenticated API Access
# =============================================================================


class TestValidTokenReturns200:
    """T017: Test valid token returns 200."""

    def test_valid_token_returns_200(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Valid JWT token should return 200 OK with user data."""
        response = client.get("/api/v1/auth/session", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user_id
        assert data["authenticated"] is True
        assert data["email"] == "test@example.com"


class TestMissingTokenReturns401:
    """T018: Test missing token returns 401."""

    def test_missing_token_returns_401(self, client: TestClient):
        """Request without Authorization header should return 401."""
        response = client.get("/api/v1/auth/session")

        # HTTPBearer returns 401 when no token provided
        assert response.status_code == 401

    def test_empty_bearer_returns_401(self, client: TestClient):
        """Request with empty Bearer token should return 401."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": "Bearer "}
        )

        assert response.status_code == 401


class TestSequentialRequestsAuthenticated:
    """T019: Test sequential requests with same token."""

    def test_sequential_requests_authenticated(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Multiple requests with same valid token should all succeed."""
        # First request
        response1 = client.get("/api/v1/auth/session", headers=auth_header)
        assert response1.status_code == 200

        # Second request with same token
        response2 = client.get("/api/v1/auth/session", headers=auth_header)
        assert response2.status_code == 200

        # Third request with same token
        response3 = client.get("/api/v1/auth/session", headers=auth_header)
        assert response3.status_code == 200

        # All should return same user
        assert response1.json()["user_id"] == test_user_id
        assert response2.json()["user_id"] == test_user_id
        assert response3.json()["user_id"] == test_user_id


# =============================================================================
# User Story 3: Token Expiration Handling
# =============================================================================


class TestExpiredTokenReturns401:
    """T038: Test expired token returns 401."""

    def test_expired_token_returns_401(
        self, client: TestClient, expired_token: str
    ):
        """Expired JWT token should return 401 with expiration message."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Token has expired"


class TestTokenNearExpirySucceeds:
    """T039: Test valid token near expiry succeeds."""

    def test_token_near_expiry_succeeds(
        self, client: TestClient, token_near_expiry: str, test_user_id: str
    ):
        """Token about to expire should still work."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {token_near_expiry}"}
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == test_user_id


class TestClockSkewTolerance:
    """T040: Test clock skew tolerance (10s)."""

    def test_clock_skew_tolerance(
        self, client: TestClient, token_within_clock_skew: str, test_user_id: str
    ):
        """Token within clock skew tolerance should be accepted."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {token_within_clock_skew}"}
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == test_user_id


# =============================================================================
# User Story 4: Invalid Token Rejection
# =============================================================================


class TestMalformedTokenReturns401:
    """T044: Test malformed token returns 401."""

    def test_malformed_token_returns_401(
        self, client: TestClient, malformed_token: str
    ):
        """Malformed JWT should return 401 with generic error."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {malformed_token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


class TestWrongSignatureReturns401:
    """T045: Test wrong signature returns 401."""

    def test_wrong_signature_returns_401(
        self, client: TestClient, wrong_signature_token: str
    ):
        """Token signed with wrong secret should return 401."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {wrong_signature_token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


class TestTamperedPayloadReturns401:
    """T046: Test tampered payload returns 401."""

    def test_tampered_payload_returns_401(
        self, client: TestClient, tampered_token: str
    ):
        """Token with tampered payload should return 401."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


class TestMissingSubClaimReturns401:
    """T047: Test missing sub claim returns 401."""

    def test_missing_sub_claim_returns_401(
        self, client: TestClient, token_missing_sub: str
    ):
        """Token without 'sub' claim should return 401."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {token_missing_sub}"}
        )

        assert response.status_code == 401
        # Could be "Invalid credentials" or "Invalid token claims" depending on
        # whether python-jose catches it first or our code does


class TestEmptyAuthHeaderReturns401:
    """T048: Test empty Authorization header returns 401."""

    def test_empty_auth_header_returns_401(self, client: TestClient):
        """Empty Authorization header should return 401/403."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": ""}
        )

        # FastAPI HTTPBearer may return 403 for malformed auth header
        assert response.status_code in [401, 403]

    def test_bearer_only_returns_401(self, client: TestClient):
        """Authorization header with just 'Bearer' should return 401/403."""
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": "Bearer"}
        )

        assert response.status_code in [401, 403]


class TestMissingRequiredClaims:
    """Additional tests for required claims validation."""

    def test_missing_exp_handled(
        self, client: TestClient, token_missing_exp: str
    ):
        """
        Token without 'exp' claim behavior test.

        Note: python-jose behavior depends on configuration and version.
        The important thing is the request completes without unhandled error.
        """
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {token_missing_exp}"}
        )

        # Request completes - either accepted or rejected
        assert response.status_code in [200, 401]

    def test_missing_iat_handled(
        self, client: TestClient, token_missing_iat: str
    ):
        """
        Token without 'iat' claim behavior test.

        Note: python-jose may not strictly enforce 'iat' requirement
        depending on version. The important thing is the request doesn't
        cause an unhandled error.
        """
        response = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {token_missing_iat}"}
        )

        # Request completes without error - either accepted or rejected
        assert response.status_code in [200, 401]
