import os

from src.app.Configuration import Configuration


def test_load_json():
    json_str = """{
  "process_finder_count": 1,
  "process_collector_count": 1,
  "fetcher_count": 1,
  "fetcher_process_count": 15,
  "hierarchy_fetcher_worker_count": 16,
  "active_build_dir_path": null,
  "saves_path": null
}
"""
    config: Configuration
    with open("test_config_no_path", "w+") as config_file:
        config_file.write(json_str)
        config_file.seek(0)
        print(config_file.read())
        config = Configuration.load("test_config_no_path")
        os.remove("test_config_no_path")
    assert config.hierarchy_fetcher_worker_count == 16
    assert config.active_build_dir_path != "None"
    assert config.saves_path != "None"


def test_load_json_with_set_path():
    json_str = """
    {
      "process_finder_count": 1,
      "process_collector_count": 1,
      "fetcher_count": 1,
      "fetcher_process_count": 15,
      "hierarchy_fetcher_worker_count": 16,
      "active_build_dir_path": "test\\test",
      "saves_path": "saves_path_test"
    }
    """
    config: Configuration
    with open("test_config_path_set", "w+") as config_file:
        config_file.write(json_str)
        config_file.seek(0)
        config = Configuration.load("test_config_path_set")
        os.remove("test_config_path_set")
    assert config.hierarchy_fetcher_worker_count == 16
    assert config.saves_path == "saves_path_test"
    assert config.active_build_dir_path == "test\test"


def test_load_wrong_json():
    json_str = """
{
  "process_collector_count": 1,
  "fetcher_count": 1,
  "fetcher_process_count": 15,
  "hierarchy_fetcher_worker_count": 16,
}
"""
    try:
        with open("test_config_wrong", "w+") as config_file:
            config_file.write(json_str)
            config_file.seek(0)
            Configuration.load("test_config_wrong")
            assert False
    except:
        assert True
    os.remove("test_config_wrong")


if __name__ == "__main__":
    test_load_json()
    test_load_json_with_set_path()
    test_load_wrong_json()
