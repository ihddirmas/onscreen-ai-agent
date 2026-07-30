```markdown
# onscreen-ai-agent Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `onscreen-ai-agent` TypeScript codebase. You'll learn how to structure files, write imports/exports, follow commit conventions, and create and run tests using Playwright. This guide is ideal for contributors aiming for consistency and maintainability in this repository.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example:  
    ```plaintext
    agent_core.ts
    user_input_handler.ts
    ```

### Import Style
- Use **relative imports** for referencing local modules.
  - Example:
    ```typescript
    import helper from './utils/helper';
    ```

### Export Style
- Use **default exports** for modules.
  - Example:
    ```typescript
    // In agent_core.ts
    const AgentCore = { /* ... */ };
    export default AgentCore;
    ```

### Commit Messages
- Follow **conventional commit** format.
- Use prefixes such as `test`.
- Keep commit messages concise (average ~61 characters).
  - Example:
    ```plaintext
    test: add agent core unit tests for input validation
    ```

## Workflows

### Running Tests
**Trigger:** When you want to verify code correctness or before submitting a pull request  
**Command:** `/run-tests`

1. Ensure Playwright is installed:  
   ```bash
   npm install --save-dev playwright
   ```
2. Run all test suites:  
   ```bash
   npx playwright test
   ```
3. Review the output for passing/failing tests.

### Adding a New Feature
**Trigger:** When implementing a new functionality  
**Command:** `/add-feature`

1. Create a new file using snake_case naming (e.g., `feature_name.ts`).
2. Write your TypeScript code, using relative imports and default exports.
3. Add or update corresponding test files (see Testing Patterns).
4. Commit changes using a conventional commit message:
   ```bash
   git commit -m "feat: add feature_name module"
   ```

### Writing Tests
**Trigger:** When adding or updating code that needs test coverage  
**Command:** `/write-test`

1. Create a test file with the `.spec.ts` suffix (e.g., `feature_name.spec.ts`).
2. Use Playwright's testing APIs to write your test cases.
   - Example:
     ```typescript
     import { test, expect } from '@playwright/test';
     import feature from './feature_name';

     test('should perform expected behavior', () => {
       expect(feature()).toBe(true);
     });
     ```
3. Run tests to verify:
   ```bash
   npx playwright test
   ```

## Testing Patterns

- **Framework:** Playwright
- **Test file pattern:** `*.spec.ts`
- **Location:** Tests are typically placed alongside the modules they test, using the same base name.
- **Example test:**
  ```typescript
  import { test, expect } from '@playwright/test';
  import agentCore from './agent_core';

  test('agentCore initializes correctly', () => {
    expect(agentCore.init()).toBeTruthy();
  });
  ```

## Commands
| Command         | Purpose                                      |
|-----------------|----------------------------------------------|
| /run-tests      | Run all Playwright test suites               |
| /add-feature    | Steps to add a new feature/module            |
| /write-test     | Steps to create and run a new test           |
```
