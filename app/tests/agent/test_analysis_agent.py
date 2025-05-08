import textwrap
import pytest

from app.core.setting import gemini_settings
from app.llm.agent.analysis_agent import TestAnalysisAgent
from app.llm.model_factory import ModelFactory
from app.schemas.model_factory import GeminiParams
from app.schemas.structured_output import TestFileAnalysis


@pytest.mark.asyncio
async def test_validate_vitest():
    agent = TestAnalysisAgent(
        model=await ModelFactory().load_llm(
            GeminiParams(api_key=gemini_settings.GEMINI_API_KEY)
        ),
    )

    expected_response = TestFileAnalysis(
        test_headers_indentation=4,
        last_single_test_line_number=6,
        last_import_line_number=1,
    )

    result = await agent.validate_vitest(get_test_file_content())

    assert result == expected_response


def get_test_file_content():
    return textwrap.dedent(
        """
        import { describe, test, expect } from 'vitest';
        
        describe('Test Suite', () => {
            test('should pass', () => {
                expect(true).toBe(true);
            });
        });
        """
    ).lstrip()
