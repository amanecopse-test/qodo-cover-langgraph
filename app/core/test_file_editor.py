from typing import List, Optional


class TestSnapshot:
    def __init__(
        self,
        test_file: str,
        line_number_to_insert_imports_after: int,
        line_number_to_insert_tests_after: int,
        coverage_percent: Optional[int] = None,
    ):
        self.test_file: str = test_file
        self.line_number_to_insert_imports_after: int = (
            line_number_to_insert_imports_after
        )
        self.line_number_to_insert_tests_after: int = line_number_to_insert_tests_after
        self.coverage_percent: Optional[int] = coverage_percent


class SnapshotEditor:
    def __init__(
        self,
        test_file: str,
        line_number_to_insert_imports_after: int,
        line_number_to_insert_tests_after: int,
        single_test_indent: int = 2,
    ):
        self.test_file: str = test_file
        self.line_number_to_insert_imports_after: int = (
            line_number_to_insert_imports_after
        )
        self.line_number_to_insert_tests_after: int = line_number_to_insert_tests_after
        self.single_test_indent: int = single_test_indent
        self.history: List[TestSnapshot] = []
        self.coverage_percent: Optional[int] = None

    def add_new_test(self, additional_test: str, additional_imports: str) -> str:
        # 현재 테스트 정보 백업
        new_test_history = TestSnapshot(
            test_file=self.test_file,
            line_number_to_insert_imports_after=self.line_number_to_insert_imports_after,
            line_number_to_insert_tests_after=self.line_number_to_insert_tests_after,
            coverage_percent=self.coverage_percent,
        )
        self.history.append(new_test_history)

        needed_indent = self.single_test_indent
        additional_test_indented = "\n".join(
            [f"{' ' * needed_indent}{line}" for line in additional_test.splitlines()]
        )
        original_test_file_lines = self.test_file.splitlines()

        # 임포트 전처리
        additional_import_lines = []
        if additional_imports:
            raw_import_lines = additional_imports.splitlines()
            for line in raw_import_lines:
                # 중복 제외
                if line.strip() and all(
                    line.strip() != existing.strip()
                    for existing in original_test_file_lines
                ):
                    additional_import_lines.append(line)

        # 임포트 삽입
        inserted_lines_count = 0
        if additional_import_lines:
            original_test_file_lines = (
                original_test_file_lines[: self.line_number_to_insert_imports_after]
                + additional_import_lines
                + original_test_file_lines[self.line_number_to_insert_imports_after :]
            )
            inserted_lines_count = len(additional_import_lines)

        # 테스트 삽입 지점 갱신
        updated_test_insertion_point = self.line_number_to_insert_tests_after
        if inserted_lines_count > 0:
            updated_test_insertion_point += inserted_lines_count

        # 테스트 삽입
        additional_test_lines = additional_test_indented.splitlines()
        original_test_file_lines = (
            original_test_file_lines[:updated_test_insertion_point]
            + additional_test_lines
            + original_test_file_lines[updated_test_insertion_point:]
        )

        # 테스트 정보 업데이트
        self.test_file = "\n".join(original_test_file_lines)
        self.line_number_to_insert_tests_after += (
            len(additional_test_lines) + inserted_lines_count
        )
        if inserted_lines_count > 0:
            self.line_number_to_insert_imports_after += inserted_lines_count

        return self.test_file

    def rollback(self) -> None:
        if len(self.history) == 0:
            return

        item = self.history.pop()
        self.test_file = item.test_file
        self.line_number_to_insert_imports_after = (
            item.line_number_to_insert_imports_after
        )
        self.line_number_to_insert_tests_after = item.line_number_to_insert_tests_after
        self.coverage_percent = item.coverage_percent
