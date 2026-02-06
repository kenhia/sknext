"""Tests for data models."""

from pathlib import Path

from sknext.models import ParseError, Phase, Section, Task, TasksFile


class TestTask:
    """Tests for Task dataclass."""

    def test_task_creation(self):
        """Test creating a valid task."""
        task = Task(
            id="T001",
            description="Create project structure",
            completed=False,
            priority=False,
            story_tag=None,
            line_number=10,
            raw_line="- [ ] T001 Create project structure",
        )
        assert task.id == "T001"
        assert task.description == "Create project structure"
        assert not task.completed
        assert not task.priority
        assert task.story_tag is None
        assert task.line_number == 10

    def test_task_with_priority(self):
        """Test task with priority marker."""
        task = Task(
            id="T002",
            description="[P] Parallel task",
            completed=False,
            priority=True,
            story_tag=None,
            line_number=15,
            raw_line="- [ ] T002 [P] Parallel task",
        )
        assert task.priority

    def test_task_with_story_tag(self):
        """Test task with story tag."""
        task = Task(
            id="T003",
            description="[US1] User story task",
            completed=False,
            priority=False,
            story_tag="US1",
            line_number=20,
            raw_line="- [ ] T003 [US1] User story task",
        )
        assert task.story_tag == "US1"

    def test_completed_task(self):
        """Test completed task."""
        task = Task(
            id="T004",
            description="Completed task",
            completed=True,
            priority=False,
            story_tag=None,
            line_number=25,
            raw_line="- [X] T004 Completed task",
        )
        assert task.completed


class TestSection:
    """Tests for Section dataclass."""

    def test_section_creation(self):
        """Test creating a valid section."""
        section = Section(
            title="Setup",
            level=3,
            tasks=[],
            line_number=5,
            purpose="Initialize project",
        )
        assert section.title == "Setup"
        assert section.level == 3
        assert len(section.tasks) == 0
        assert section.purpose == "Initialize project"

    def test_section_with_tasks(self):
        """Test section containing tasks."""
        tasks = [
            Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1"),
            Task("T002", "Task 2", True, False, None, 11, "- [X] T002 Task 2"),
            Task("T003", "Task 3", False, False, None, 12, "- [ ] T003 Task 3"),
        ]
        section = Section("Implementation", 3, tasks, 8, None)
        assert len(section.tasks) == 3
        assert section.total_count() == 3

    def test_section_has_uncompleted_tasks(self):
        """Test section.has_uncompleted_tasks() method."""
        tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
        ]
        section = Section("Test", 3, tasks, 5, None)
        assert section.has_uncompleted_tasks()

    def test_section_all_completed(self):
        """Test section with all completed tasks."""
        tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", True, False, None, 11, "- [X] T002 Task 2"),
        ]
        section = Section("Test", 3, tasks, 5, None)
        assert not section.has_uncompleted_tasks()

    def test_section_uncompleted_count(self):
        """Test section.uncompleted_count() method."""
        tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
            Task("T003", "Task 3", False, False, None, 12, "- [ ] T003 Task 3"),
        ]
        section = Section("Test", 3, tasks, 5, None)
        assert section.uncompleted_count() == 2


class TestPhase:
    """Tests for Phase dataclass."""

    def test_phase_creation(self):
        """Test creating a valid phase."""
        phase = Phase(number=1, title="Setup", sections=[], line_number=3)
        assert phase.number == 1
        assert phase.title == "Setup"
        assert len(phase.sections) == 0

    def test_phase_with_sections(self):
        """Test phase containing sections."""
        sections = [
            Section("Section 1", 3, [], 5, None),
            Section("Section 2", 3, [], 8, None),
        ]
        phase = Phase(1, "Foundation", sections, 3)
        assert len(phase.sections) == 2

    def test_phase_has_uncompleted_work(self):
        """Test phase.has_uncompleted_work() method."""
        tasks = [Task("T001", "Task", False, False, None, 10, "- [ ] T001 Task")]
        section = Section("Test", 3, tasks, 8, None)
        phase = Phase(1, "Test", [section], 5)
        assert phase.has_uncompleted_work()

    def test_phase_all_completed(self):
        """Test phase with all work completed."""
        tasks = [Task("T001", "Task", True, False, None, 10, "- [X] T001 Task")]
        section = Section("Test", 3, tasks, 8, None)
        phase = Phase(1, "Test", [section], 5)
        assert not phase.has_uncompleted_work()

    def test_phase_uncompleted_task_count(self):
        """Test phase.uncompleted_task_count() method."""
        section1_tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
        ]
        section2_tasks = [
            Task("T003", "Task 3", False, False, None, 15, "- [ ] T003 Task 3"),
        ]
        sections = [
            Section("Sec 1", 3, section1_tasks, 8, None),
            Section("Sec 2", 3, section2_tasks, 13, None),
        ]
        phase = Phase(1, "Test", sections, 5)
        assert phase.uncompleted_task_count() == 2

    def test_phase_total_task_count(self):
        """Test phase.total_task_count() method."""
        section1_tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
        ]
        section2_tasks = [
            Task("T003", "Task 3", False, False, None, 15, "- [ ] T003 Task 3"),
        ]
        sections = [
            Section("Sec 1", 3, section1_tasks, 8, None),
            Section("Sec 2", 3, section2_tasks, 13, None),
        ]
        phase = Phase(1, "Test", sections, 5)
        assert phase.total_task_count() == 3


class TestTasksFile:
    """Tests for TasksFile dataclass."""

    def test_tasksfile_creation(self):
        """Test creating a valid TasksFile."""
        tasks_file = TasksFile(file_path=Path("/tmp/tasks.md"), phases=[], parse_errors=[])
        assert tasks_file.file_path == Path("/tmp/tasks.md")
        assert len(tasks_file.phases) == 0
        assert len(tasks_file.parse_errors) == 0

    def test_get_all_tasks(self):
        """Test TasksFile.get_all_tasks() method."""
        section1_tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
        ]
        section2_tasks = [
            Task("T003", "Task 3", False, False, None, 15, "- [ ] T003 Task 3"),
        ]
        sections = [
            Section("Sec 1", 3, section1_tasks, 8, None),
            Section("Sec 2", 3, section2_tasks, 13, None),
        ]
        phase = Phase(1, "Test", sections, 5)
        tasks_file = TasksFile(Path("/tmp/tasks.md"), [phase], [])

        all_tasks = tasks_file.get_all_tasks()
        assert len(all_tasks) == 3

    def test_get_uncompleted_tasks(self):
        """Test TasksFile.get_uncompleted_tasks() method."""
        section_tasks = [
            Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1"),
            Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
            Task("T003", "Task 3", False, False, None, 12, "- [ ] T003 Task 3"),
        ]
        section = Section("Test", 3, section_tasks, 8, None)
        phase = Phase(1, "Test", [section], 5)
        tasks_file = TasksFile(Path("/tmp/tasks.md"), [phase], [])

        uncompleted = tasks_file.get_uncompleted_tasks()
        assert len(uncompleted) == 2
        assert all(not task.completed for task in uncompleted)

    def test_get_phases_with_uncompleted_work(self):
        """Test TasksFile.get_phases_with_uncompleted_work() method."""
        # Phase 1: all completed
        phase1_tasks = [Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1")]
        phase1_section = Section("Sec", 3, phase1_tasks, 8, None)
        phase1 = Phase(1, "Complete", [phase1_section], 5)

        # Phase 2: has uncompleted
        phase2_tasks = [Task("T002", "Task 2", False, False, None, 15, "- [ ] T002 Task 2")]
        phase2_section = Section("Sec", 3, phase2_tasks, 13, None)
        phase2 = Phase(2, "In Progress", [phase2_section], 12)

        tasks_file = TasksFile(Path("/tmp/tasks.md"), [phase1, phase2], [])
        uncompleted_phases = tasks_file.get_phases_with_uncompleted_work()
        assert len(uncompleted_phases) == 1
        assert uncompleted_phases[0].number == 2

    def test_is_complete(self):
        """Test TasksFile.is_complete() method."""
        completed_tasks = [Task("T001", "Task 1", True, False, None, 10, "- [X] T001 Task 1")]
        section = Section("Sec", 3, completed_tasks, 8, None)
        phase = Phase(1, "Test", [section], 5)
        tasks_file = TasksFile(Path("/tmp/tasks.md"), [phase], [])
        assert tasks_file.is_complete()

    def test_is_not_complete(self):
        """Test TasksFile.is_complete() returns False when tasks remain."""
        tasks = [Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1")]
        section = Section("Sec", 3, tasks, 8, None)
        phase = Phase(1, "Test", [section], 5)
        tasks_file = TasksFile(Path("/tmp/tasks.md"), [phase], [])
        assert not tasks_file.is_complete()


class TestParseError:
    """Tests for ParseError dataclass."""

    def test_parse_error_creation(self):
        """Test creating a ParseError."""
        error = ParseError(
            line_number=42,
            line_content="- [] T001 Malformed",
            error_type="MalformedTask",
            message="Checkbox must have single space",
        )
        assert error.line_number == 42
        assert error.line_content == "- [] T001 Malformed"
        assert error.error_type == "MalformedTask"
        assert "space" in error.message
