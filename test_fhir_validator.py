import fhir_validator as m
import pathlib
import pytest
import os


def test_lookup():
    r = m.lookup('creatinine')
    assert 'top_hit' in r and 'score' in r
    pdir = pathlib.Path(__file__).parent
    rows = m.process_csv(str(pdir / 'sample.csv'), str(pdir / 'tmp_test_out.csv'))
    assert len(rows) >= 1
    # Cleanup temp file
    tmp = pdir / 'tmp_test_out.csv'
    if tmp.exists():
        os.remove(str(tmp))


def test_lookup_returns_dict_structure():
    """Verify lookup returns expected dict structure."""
    r = m.lookup('hemoglobin')
    assert isinstance(r, dict)
    assert 'query' in r
    assert 'top_hit' in r
    assert 'score' in r
    assert 'all' in r
    assert isinstance(r['all'], list)


def test_process_csv_file_not_found():
    """Verify FileNotFoundError for missing input."""
    with pytest.raises(FileNotFoundError):
        m.process_csv('/nonexistent/path.csv', '/tmp/out.csv')


def test_process_csv_empty_headers():
    """Verify ValueError for CSV with no headers."""
    pdir = pathlib.Path(__file__).parent
    empty_csv = pdir / 'tmp_empty.csv'
    empty_csv.write_text('')
    try:
        with pytest.raises(ValueError):
            m.process_csv(str(empty_csv), str(pdir / 'tmp_out.csv'))
    finally:
        if empty_csv.exists():
            os.remove(str(empty_csv))


def test_build_parser_single_command():
    """Verify CLI parser accepts single command."""
    p = m.build_parser()
    args = p.parse_args(['single', 'creatinine'])
    assert args.cmd == 'single'
    assert args.query == 'creatinine'


def test_build_parser_batch_command():
    """Verify CLI parser accepts batch command."""
    p = m.build_parser()
    args = p.parse_args(['batch', '--input', 'in.csv', '--output', 'out.csv'])
    assert args.cmd == 'batch'
    assert args.input == 'in.csv'
    assert args.output == 'out.csv'


def test_main_single_returns_zero():
    """Verify main returns 0 for single command."""
    assert m.main(['single', 'test']) == 0


def test_main_batch_returns_zero(tmp_path):
    """Verify main returns 0 for batch command."""
    # Create a minimal CSV
    csv_file = tmp_path / 'test_in.csv'
    csv_file.write_text('query\ncreatinine\n')
    out_file = tmp_path / 'test_out.csv'
    assert m.main(['batch', '--input', str(csv_file), '--output', str(out_file)]) == 0
    assert out_file.exists()
