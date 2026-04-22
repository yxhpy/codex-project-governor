.PHONY: test init-example

test:
	python3 tests/selftest.py
	python3 tests/test_smart_routing_guard.py
	python3 tests/test_subagent_activation.py
	python3 tests/test_plugin_upgrade_migrator.py
	python3 tests/test_clean_reinstall_manager.py

init-example:
	python3 tools/init_project.py --mode existing --target ./tmp-example
