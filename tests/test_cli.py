"""Tests for mekon CLI core functionality."""

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestMainCli:
    """Test the main CLI app."""

    def test_version(self):
        """Version command outputs version string."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Mekon CLI" in result.output

    def test_no_command_shows_help(self):
        """Running without command shows overview."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Mekon CLI" in result.output

    def test_help(self):
        """Help flag works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "devops" in result.output
        assert "revenue" in result.output
        assert "marketing" in result.output
        assert "agents" in result.output
        assert "system" in result.output


class TestSystemCommands:
    """Test system sub-commands."""

    def test_system_info(self):
        """System info shows version."""
        result = runner.invoke(app, ["system", "info"])
        assert result.exit_code == 0
        assert "Mekon CLI" in result.output

    def test_system_config(self):
        """System config shows settings."""
        result = runner.invoke(app, ["system", "config"])
        assert result.exit_code == 0
        assert "Configuration" in result.output

    def test_system_health(self):
        """System health runs checks."""
        result = runner.invoke(app, ["system", "health"])
        assert result.exit_code == 0
        assert "Health" in result.output


class TestDevopsCommands:
    """Test devops sub-commands."""

    def test_devops_status(self):
        """DevOps status shows deployment info."""
        result = runner.invoke(app, ["devops", "status"])
        assert result.exit_code == 0
        assert "Status" in result.output

    def test_devops_deploy_unknown_target(self):
        """Deploy with unknown target shows error."""
        result = runner.invoke(app, ["devops", "deploy", "unknown-platform"])
        assert result.exit_code == 1

    def test_devops_build_missing_project(self):
        """Build with missing project shows error."""
        result = runner.invoke(app, ["devops", "build", "--project", "/nonexistent/path"])
        # Build should fail since the dir doesn't exist and cmd fails
        assert result.exit_code != 0 or "error" in result.output.lower() or "Error" in result.output


class TestRevenueCommands:
    """Test revenue sub-commands."""

    def test_revenue_dashboard_empty(self):
        """Revenue dashboard with no data."""
        result = runner.invoke(app, ["revenue", "dashboard"])
        assert result.exit_code == 0

    def test_revenue_report_empty(self):
        """Revenue report with no data."""
        result = runner.invoke(app, ["revenue", "report"])
        assert result.exit_code == 0
