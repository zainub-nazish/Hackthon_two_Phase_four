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


# =============================================================================
# Task ID  : T018
# Phase V Tests — Advanced Task Features (US1)
# Spec Ref : speckit.tasks → T018
# Plan Ref : speckit.plan → Section 3: API Contracts
# =============================================================================


class TestPhaseVTaskFields:
    """Phase V: Tasks now support due_date, priority, tags, recurrence."""

    def test_create_task_with_priority_returns_priority(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks with priority=high returns task with priority=high."""
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "High priority task", "priority": "high"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"

    def test_create_task_invalid_priority_rejected(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks with priority=extreme returns 422."""
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Bad priority", "priority": "extreme"},
        )
        assert response.status_code == 422

    def test_create_task_with_tags_returns_tags(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks with tags returns task with correct tags."""
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Tagged task", "tags": ["work", "urgent"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert "work" in data["tags"]
        assert "urgent" in data["tags"]

    def test_create_task_with_recurrence(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks with recurrence stores recurrence config."""
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={
                "title": "Daily standup",
                "recurrence": {"interval": "daily", "every": 1},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["recurrence"]["interval"] == "daily"
        assert data["recurrence"]["every"] == 1

    def test_create_task_default_priority_is_medium(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks without priority defaults to 'medium'."""
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Default priority task"},
        )
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"

    def test_response_includes_phase_v_fields(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """GET /tasks response items include Phase V fields."""
        # Create a task first
        client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Phase V field check"},
        )
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
        )
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert "priority" in item
            assert "tags" in item
            assert "due_date" in item


class TestPhaseVSearchAndFilter:
    """Phase V: GET /tasks supports search, priority filter, and sort."""

    def test_filter_by_priority(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """GET /tasks?priority=low returns only low-priority tasks."""
        # Create a low-priority task
        client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Low priority", "priority": "low"},
        )
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks?priority=low",
            headers=auth_header,
        )
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert item["priority"] == "low"

    def test_invalid_priority_filter_returns_400(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """GET /tasks?priority=extreme returns 400."""
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks?priority=extreme",
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_search_by_title_keyword(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """GET /tasks?search=unique returns tasks matching title."""
        client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "UniqueSearchableTask123"},
        )
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks?search=UniqueSearchableTask123",
            headers=auth_header,
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert any("UniqueSearchableTask123" in i["title"] for i in items)

    def test_sort_by_created_at_asc(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """GET /tasks?sort=created_at&sort_dir=asc returns tasks in ascending order."""
        response = client.get(
            f"/api/v1/users/{test_user_id}/tasks?sort=created_at&sort_dir=asc",
            headers=auth_header,
        )
        assert response.status_code == 200


class TestCompleteEndpoint:
    """Phase V: POST /tasks/{id}/complete sets completed_at."""

    def test_complete_task_sets_completed_at(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks/{id}/complete returns completed=True with completed_at."""
        # Create task
        create_resp = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Task to complete"},
        )
        assert create_resp.status_code == 201
        task_id = create_resp.json()["id"]

        # Complete it
        complete_resp = client.post(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}/complete",
            headers=auth_header,
        )
        assert complete_resp.status_code == 200
        data = complete_resp.json()
        assert data["completed"] is True
        assert data["completed_at"] is not None

    def test_complete_nonexistent_task_returns_404(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks/{bad_id}/complete returns 404."""
        import uuid
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks/{uuid.uuid4()}/complete",
            headers=auth_header,
        )
        assert response.status_code == 404

    def test_complete_already_completed_returns_409(
        self, client: TestClient, auth_header: dict, test_user_id: str
    ):
        """POST /tasks/{id}/complete on an already-completed task returns 409."""
        create_resp = client.post(
            f"/api/v1/users/{test_user_id}/tasks",
            headers=auth_header,
            json={"title": "Already done"},
        )
        task_id = create_resp.json()["id"]

        # First complete — OK
        client.post(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}/complete",
            headers=auth_header,
        )
        # Second complete — conflict
        response = client.post(
            f"/api/v1/users/{test_user_id}/tasks/{task_id}/complete",
            headers=auth_header,
        )
        assert response.status_code == 409
