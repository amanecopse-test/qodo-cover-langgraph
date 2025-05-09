import pytest
from app.core.snapshot_editor import SnapshotEditor


@pytest.fixture
def sample_test_file():
    return """import { describe, it, expect } from 'vitest'

describe('Sample test suite', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
})
"""


@pytest.fixture
def vitest_template(sample_test_file):
    return SnapshotEditor(
        test_file_content=sample_test_file,
        line_number_to_insert_imports_after=1,
        line_number_to_insert_tests_after=6,
        single_test_indent=2,
    )


def test_add_new_test_without_imports(vitest_template):
    # Given
    additional_test = """it('should add new test', () => {
  expect(1 + 1).toBe(2)
})"""
    additional_imports = ""

    # When
    result = vitest_template.add_new_test(additional_test, additional_imports)

    # Then
    expected = """import { describe, it, expect } from 'vitest'

describe('Sample test suite', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
  it('should add new test', () => {
    expect(1 + 1).toBe(2)
  })
})"""
    assert result == expected
    assert vitest_template.line_number_to_insert_tests_after == 9


def test_add_new_test_with_imports(vitest_template):
    # Given
    additional_test = """it('should test math', () => {
  expect(add(1, 1)).toBe(2)
})"""
    additional_imports = "import { add } from './math'"

    # When
    result = vitest_template.add_new_test(additional_test, additional_imports)

    # Then
    expected = """import { describe, it, expect } from 'vitest'
import { add } from './math'

describe('Sample test suite', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
  it('should test math', () => {
    expect(add(1, 1)).toBe(2)
  })
})"""
    assert result == expected
    assert vitest_template.line_number_to_insert_imports_after == 2
    assert vitest_template.line_number_to_insert_tests_after == 10


def test_add_duplicate_imports(vitest_template):
    # Given
    additional_test = """it('should test math', () => {
  expect(add(1, 1)).toBe(2)
})"""
    additional_imports = (
        "import { describe, it, expect } from 'vitest'"  # Already exists
    )

    # When
    result = vitest_template.add_new_test(additional_test, additional_imports)

    # Then
    expected = """import { describe, it, expect } from 'vitest'

describe('Sample test suite', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
  it('should test math', () => {
    expect(add(1, 1)).toBe(2)
  })
})"""
    assert result == expected
    assert vitest_template.line_number_to_insert_imports_after == 1
    assert vitest_template.line_number_to_insert_tests_after == 9


def test_rollback(vitest_template):
    # Given
    initial_test_file = vitest_template.test_file_content
    additional_test = """it('should be rolled back', () => {
  expect(true).toBe(false)
})"""
    additional_imports = "import { something } from './else'"

    # When
    vitest_template.add_new_test(additional_test, additional_imports)
    vitest_template.rollback()

    # Then
    assert vitest_template.test_file_content == initial_test_file
    assert vitest_template.line_number_to_insert_imports_after == 1
    assert vitest_template.line_number_to_insert_tests_after == 6


def test_multiple_rollbacks(vitest_template):
    # Given
    initial_test_file = vitest_template.test_file_content
    test1 = "it('test1', () => {})"
    test2 = "it('test2', () => {})"
    test3 = "it('test3', () => {})"

    # When
    vitest_template.add_new_test(test1, "")
    vitest_template.add_new_test(test2, "")
    vitest_template.add_new_test(test3, "")

    # Then
    assert len(vitest_template.history) == 3

    # When rolling back
    vitest_template.rollback()
    vitest_template.rollback()
    vitest_template.rollback()

    # Then
    assert vitest_template.test_file_content == initial_test_file
    assert len(vitest_template.history) == 0


def test_rollback_empty_history(vitest_template):
    # Given
    initial_test_file = vitest_template.test_file_content

    # When
    vitest_template.rollback()

    # Then
    assert vitest_template.test_file_content == initial_test_file
    assert len(vitest_template.history) == 0


def test_indentation(vitest_template):
    # Given
    additional_test = """it('should have correct indentation', () => {
  const value = 1
  expect(value).toBe(1)
})"""
    additional_imports = ""

    # When
    result = vitest_template.add_new_test(additional_test, additional_imports)

    # Then
    expected = """import { describe, it, expect } from 'vitest'

describe('Sample test suite', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
  it('should have correct indentation', () => {
    const value = 1
    expect(value).toBe(1)
  })
})"""
    assert result == expected
