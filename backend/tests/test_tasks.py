"""Tests for task endpoints with user isolation (User Story 2)."""

import pytest
from fastapi.testclient import TestClient


# =============================================================================
# User Story 2: User Isolation & Data Protection
# =============================================================================


class TestGetOwnTasksReturns200:
    """T024: Test own tasks returns 200."""

    def test_get_own_tasks_returns_200(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """User can list their own tasks."""
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_get_own_tasks_with_pagination(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """User can paginate their own tasks."""
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks?limit=10&offset=0",
            headers=auth_header
        )

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0


class TestCrossUserAccessReturns404:
    """T025: Test cross-user access returns 404."""

    def test_cross_user_access_returns_404(
        self,
        client: TestClient,
        auth_header: dict,
        another_user_id: str
    ):
        """User cannot access another user's tasks - returns 404."""
        response = client.get(
            f"/api/v1/users/{another_user_id}/tasks",
            headers=auth_header
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Not found"

    def test_cross_user_task_access_returns_404(
        self,
        client: TestClient,
        auth_header: dict,
        another_user_id: str
    ):
        """User cannot access a specific task of another user."""
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/v1/users/{another_user_id}/tasks/{fake_task_id}",
            headers=auth_header
        )

        assert response.status_code == 404


class TestCreateTaskSetsOwner:
    """T026: Test create task with owner verification."""

    def test_create_task_sets_owner(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Created task should have correct owner_id."""
        task_data = {
            "title": "Test Task",
            "description": "Test description",
            "completed": False
        }

        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json=task_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["owner_id"] == test_user_id
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_cannot_create_task_for_another_user(
        self,
        client: TestClient,
        auth_header: dict,
        another_user_id: str
    ):
        """User cannot create tasks for another user."""
        task_data = {
            "title": "Unauthorized Task",
            "description": "Should fail",
            "completed": False
        }

        response = client.post(
            f"/api/v1/users/{another_user_id}/tasks",
            headers=auth_header,
            json=task_data
        )

        assert response.status_code == 404


class TestUpdateOtherUserTaskReturns404:
    """T027: Test update other user task returns 404."""

    def test_update_other_user_task_returns_404(
        self,
        client: TestClient,
        auth_header: dict,
        another_user_id: str
    ):
        """User cannot update another user's task."""
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"title": "Hacked Title"}

        response = client.patch(
            f"/api/v1/users/{another_user_id}/tasks/{fake_task_id}",
            headers=auth_header,
            json=update_data
        )

        assert response.status_code == 404


class TestDeleteOtherUserTaskReturns404:
    """T028: Test delete other user task returns 404."""

    def test_delete_other_user_task_returns_404(
        self,
        client: TestClient,
        auth_header: dict,
        another_user_id: str
    ):
        """User cannot delete another user's task."""
        fake_task_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(
            f"/api/v1/users/{another_user_id}/tasks/{fake_task_id}",
            headers=auth_header
        )

        assert response.status_code == 404


# =============================================================================
# Additional Task CRUD Tests (Own Resources)
# =============================================================================


class TestTaskCRUDOperations:
    """Test full CRUD operations on own tasks."""

    def test_create_read_update_delete_own_task(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Full CRUD flow for own task."""
        # CREATE
        task_data = {
            "title": "CRUD Test Task",
            "description": "Testing full CRUD",
            "completed": False
        }
        create_response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json=task_data
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # READ
        read_response = client.get(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}",
            headers=auth_header
        )
        assert read_response.status_code == 200
        assert read_response.json()["title"] == "CRUD Test Task"

        # UPDATE
        update_response = client.patch(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}",
            headers=auth_header,
            json={"completed": True}
        )
        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True

        # DELETE
        delete_response = client.delete(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}",
            headers=auth_header
        )
        assert delete_response.status_code == 204

        # VERIFY DELETED
        verify_response = client.get(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}",
            headers=auth_header
        )
        assert verify_response.status_code == 404

    def test_get_nonexistent_task_returns_404(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Getting a non-existent task returns 404."""
        fake_task_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks/{fake_task_id}",
            headers=auth_header
        )

        assert response.status_code == 404


class TestTaskValidation:
    """Test task input validation."""

    def test_create_task_empty_title_fails(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Task with empty title should fail validation."""
        task_data = {
            "title": "",
            "description": "Description",
            "completed": False
        }

        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json=task_data
        )

        assert response.status_code == 422  # Validation error

    def test_create_task_title_too_long_fails(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Task with title over 255 chars should fail validation."""
        task_data = {
            "title": "x" * 256,
            "description": "Description",
            "completed": False
        }

        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json=task_data
        )

        assert response.status_code == 422


class TestTaskFiltering:
    """Test task filtering functionality."""

    def test_filter_completed_tasks(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """Can filter tasks by completion status."""
        # Create completed task
        client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Completed Task", "completed": True}
        )

        # Create incomplete task
        client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Incomplete Task", "completed": False}
        )

        # Filter completed only
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks?completed=true",
            headers=auth_header
        )

        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["completed"] is True
