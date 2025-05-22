import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def read_file(path):
    with open(os.path.join(BASE_DIR, path), 'r') as f:
        return f.read()


class TestFiles(unittest.TestCase):
    def test_agent_instructions_v1_contains_sections(self):
        text = read_file('playwright/llm-automation/agent_instructions_v1.txt')
        self.assertIn('ANALYSIS PHASE', text)
        self.assertIn('PLANNING PHASE', text)
        self.assertIn('EXECUTION PHASE', text)
        self.assertIn('REPORTING PHASE', text)

    def test_agent_instructions_v2_contains_sections(self):
        text = read_file('playwright/llm-automation/agent_instructions_v2.txt')
        self.assertIn('ANALYSIS & PLANNING', text)
        self.assertIn('EXECUTION:', text)
        self.assertIn('REPORTING:', text)

    def test_readme_contains_key_sections(self):
        readme = read_file('README.md')
        self.assertIn('# AI-Powered QA Automation', readme)
        self.assertIn('## Overview', readme)
        self.assertIn('## Future Enhancements', readme)

    def test_requirements_contains_openai(self):
        requirements = read_file('requirements.txt')
        self.assertIn('openai', requirements)


if __name__ == '__main__':
    unittest.main()
