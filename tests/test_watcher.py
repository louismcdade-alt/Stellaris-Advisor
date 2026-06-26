from advisor import watcher


def _redirect_last_campaign(monkeypatch, tmp_path):
    """Point the module's persisted-state file at a throwaway path so tests
    never touch the real project-root last_campaign.txt."""
    target = tmp_path / 'last_campaign.txt'
    monkeypatch.setattr(watcher, '_last_campaign_path', lambda: str(target))
    return target


def test_read_last_campaign_returns_empty_when_file_missing(monkeypatch, tmp_path):
    _redirect_last_campaign(monkeypatch, tmp_path)
    assert watcher._read_last_campaign() == ''


def test_write_then_read_last_campaign_round_trips(monkeypatch, tmp_path):
    _redirect_last_campaign(monkeypatch, tmp_path)
    watcher._write_last_campaign('my_campaign_folder')
    assert watcher._read_last_campaign() == 'my_campaign_folder'


def test_advisor_state_defaults_campaign_from_persisted_value(monkeypatch, tmp_path):
    _redirect_last_campaign(monkeypatch, tmp_path)
    watcher._write_last_campaign('saved_campaign')
    state = watcher.AdvisorState(save_root=str(tmp_path))
    assert state.campaign == 'saved_campaign'


def test_advisor_state_explicit_campaign_overrides_persisted_value(monkeypatch, tmp_path):
    _redirect_last_campaign(monkeypatch, tmp_path)
    watcher._write_last_campaign('saved_campaign')
    state = watcher.AdvisorState(save_root=str(tmp_path), campaign='cli_campaign')
    assert state.campaign == 'cli_campaign'


def test_set_campaign_persists_the_choice(monkeypatch, tmp_path):
    _redirect_last_campaign(monkeypatch, tmp_path)
    state = watcher.AdvisorState(save_root=str(tmp_path))
    state.set_campaign('chosen_folder')
    assert watcher._read_last_campaign() == 'chosen_folder'
    # A fresh state (simulating a relaunch) should pick it back up.
    relaunched = watcher.AdvisorState(save_root=str(tmp_path))
    assert relaunched.campaign == 'chosen_folder'


def test_set_campaign_with_empty_string_clears_persisted_value(monkeypatch, tmp_path):
    _redirect_last_campaign(monkeypatch, tmp_path)
    watcher._write_last_campaign('old_campaign')
    state = watcher.AdvisorState(save_root=str(tmp_path))
    state.set_campaign('')  # back to auto = newest across all campaigns
    assert watcher._read_last_campaign() == ''
    relaunched = watcher.AdvisorState(save_root=str(tmp_path))
    assert relaunched.campaign is None
