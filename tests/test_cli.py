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


class TestDashboardCommand:
    """Test dashboard command."""

    def test_dash_no_interactive(self):
        """Dashboard renders in non-interactive mode."""
        result = runner.invoke(app, ["dash", "--no-interactive"])
        assert result.exit_code == 0
        assert "DevOps" in result.output
        assert "Revenue" in result.output
        assert "Agents" in result.output
        assert "System" in result.output

    def test_dash_help(self):
        """Dashboard help shows options."""
        result = runner.invoke(app, ["dash", "--help"])
        assert result.exit_code == 0
        assert "refresh" in result.output.lower() or "interactive" in result.output.lower()

    def test_dash_appears_in_help(self):
        """Dash command visible in main help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "dash" in result.output


class TestInitCommand:
    """Test init command."""

    def test_init_help(self):
        """Init help shows usage."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "init" in result.output.lower() or "Initialize" in result.output

    def test_init_creates_directories(self):
        """Init creates data directories and reports success."""
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "ready" in result.output.lower() or "Init Complete" in result.output


class TestMarketCommands:
    """Test market sub-commands."""

    def test_market_research_help(self):
        """Market research help shows usage."""
        result = runner.invoke(app, ["market", "research", "--help"])
        assert result.exit_code == 0
        assert "domain" in result.output.lower()

    def test_market_analyze_help(self):
        """Market analyze help shows usage."""
        result = runner.invoke(app, ["market", "analyze", "--help"])
        assert result.exit_code == 0
        assert "url" in result.output.lower()

    def test_market_competitors_help(self):
        """Market competitors help shows usage."""
        result = runner.invoke(app, ["market", "competitors", "--help"])
        assert result.exit_code == 0
        assert "domain" in result.output.lower()


class TestRecipeCommands:
    """Test recipe sub-commands."""

    def test_recipe_list_empty(self):
        """Recipe list works with no recipes."""
        result = runner.invoke(app, ["recipe", "list"])
        assert result.exit_code == 0
        assert "No recipes" in result.output or "recipe" in result.output.lower()

    def test_recipe_create_help(self):
        """Recipe create help shows usage."""
        result = runner.invoke(app, ["recipe", "create", "--help"])
        assert result.exit_code == 0
        assert "name" in result.output.lower()

    def test_recipe_run_help(self):
        """Recipe run help shows usage."""
        result = runner.invoke(app, ["recipe", "run", "--help"])
        assert result.exit_code == 0
        assert "name" in result.output.lower()


class TestLogsCommands:
    """Test logs sub-commands."""

    def test_logs_show_empty(self):
        """Logs show works with no log entries."""
        result = runner.invoke(app, ["logs", "show"])
        assert result.exit_code == 0
        assert "No log entries" in result.output or "log" in result.output.lower()

    def test_logs_tail_empty(self):
        """Logs tail works with no log entries."""
        result = runner.invoke(app, ["logs", "tail"])
        assert result.exit_code == 0
        assert "No log entries" in result.output or "log" in result.output.lower()

    def test_logs_clear_abort(self):
        """Logs clear aborts when user declines confirmation."""
        result = runner.invoke(app, ["logs", "clear"], input="n\n")
        assert result.exit_code != 0 or "Aborted" in result.output


class TestAllCommandsInHelp:
    """Test that all command groups appear in main help."""

    def test_all_groups_in_help(self):
        """All 8 command groups appear in --help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for group in ("devops", "revenue", "marketing", "agents", "system", "market", "logs", "recipe"):
            assert group in result.output, f"'{group}' missing from --help"

    def test_standalone_commands_in_help(self):
        """Standalone commands dash, init, version appear in --help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for cmd in ("dash", "init", "version"):
            assert cmd in result.output, f"'{cmd}' missing from --help"
