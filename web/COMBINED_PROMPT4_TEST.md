# Master Implementation Prompt: Secure PDF-to-Audiobook Application, OAuth 2.0, Batch Conversion, and Comprehensive Testing

## Project

Repository: https://github.com/coderextreme/pdf-to-audiobook-web/

Application: PDF-to-Audiobook Web

The project converts uploaded documents into audiobook files. Review the existing repository and preserve its current functionality while implementing the requirements below.

## 1. Core implementation requirements

### OAuth 2.0 and authentication

* Implement OAuth 2.0 authentication using a configurable identity provider.
* Preserve local username/password authentication if already supported.
* Implement secure OAuth authorization-code flow, state validation, callback handling, and PKCE where supported and appropriate.
* Store authentication sessions securely using HttpOnly cookies with appropriate Secure and SameSite settings.
* Implement login, logout, session restoration, expired-session handling, and authentication failure messages.
* Never expose client secrets, session identifiers, access tokens, or other credentials in client-side code, logs, or URLs.
* Require authentication for protected APIs, file uploads, previews, queue operations, audio playback, and downloads.
* Ensure that switching users clears the previous user's client-side state before loading the new user's data.

### Batch conversion

* Ensure every uploaded document creates its own independent conversion job and output file.
* Prevent output filename collisions using unique job identifiers or another reliable uniqueness mechanism.
* Never overwrite one job's output with another job's output.
* Ensure batch jobs maintain separate status, progress, errors, metadata, and output paths.
* Test batch conversions with multiple documents, including documents with identical source filenames.
* Ensure each completed job downloads and plays its own corresponding audio file.

### Single-file conversion

* Preserve the existing single-file conversion workflow.
* Provide upload progress, conversion progress, queue status, error reporting, playback, and authenticated downloads.
* Ensure the user can play or download a completed audiobook without exposing private filesystem paths or bypassing authentication.

## 2. Queue ownership and authorization

Implement explicit, server-side authorization for every queue and audio resource.

* Keep `userId` as the immutable identity of the user who submitted a job.
* Use a separate `assignedUserId` field for reassignment.
* Normalize legacy assigned jobs without accidentally losing their original submitter.
* Allow the submitting user to view their own jobs.
* Allow the assigned user to view jobs assigned to them.
* Allow organization-level queue access only when the user has the explicit, organization-scoped `queue:read` or `queue:manage` capability.
* Do not treat organization membership alone as authorization to inspect all organization jobs.
* Do not let a system-admin role bypass organization queue capability checks unless an explicitly documented and authorized policy requires it.
* Make `queue:manage` imply the ability to read and manage the relevant organization queue.
* Restrict job assignment and capability delegation to appropriately authorized organization managers.
* Validate organization membership and scope on every assignment or delegation operation.
* Keep queue clearing and deletion appropriately scoped to the authenticated user's own jobs, unless a separately authorized administrative operation is explicitly implemented.
* Apply the same access-control rules to queue listings, individual job details, audio streaming, downloads, server-sent events (SSE), and organization job endpoints.
* Prevent unauthorized users from discovering job existence through differences in error messages or response behavior.

## 3. Audio output validation and downloads

* Treat a missing audio file as a conversion error.
* Treat a zero-byte audio file as a conversion error.
* Emit appropriate conversion-error and queue-change events when output validation fails.
* Reject empty audio blobs in the frontend.
* Do not mark a job successful or start playback if its output is missing or empty.
* Implement authenticated Blob-based audio fetching for both Single File and Batch interfaces.
* Ensure download buttons are functional and appear only when the user is authorized and a valid completed output is available.
* Preserve the correct filename in downloads, including suitable handling of `Content-Disposition`.
* Clean up temporary object URLs when no longer needed.
* Test audio content types, filenames, empty responses, missing files, unauthorized requests, and network failures.

## 4. Security hardening

Implement and test the following protections:

* Validate uploaded files by extension, size, content signature, and actual parsing where appropriate.
* Enforce a configurable upload-size limit, with a reasonable default such as 25 MB.
* Reject malformed or unsupported files with safe, actionable errors.
* Prevent path traversal and ensure resolved input/output paths remain inside permitted directories.
* Apply JSON request-body limits and appropriate API rate limits.
* Bound conversion concurrency and resource usage.
* Avoid returning stack traces, secrets, filesystem paths, or internal implementation details to clients.
* Configure strict production Content Security Policy (CSP), security headers, and explicit production CORS origins.
* Disable unnecessary server-identifying headers.
* Bind the Python backend to loopback by default when it is intended to be private behind the Node server.
* Protect cookie-based state-changing operations against CSRF using an appropriate strategy.
* Validate redirect destinations and OAuth callback configuration.
* Ensure logout invalidates the server-side session and clears the session cookie.
* Ensure SSE does not require bearer tokens in query-string URLs.
* Ensure private files cannot be fetched directly through unprotected static paths.
* Maintain development compatibility with Vite and its WebSocket connections without weakening the production security policy.

## 5. Login switching and frontend state

When the authenticated user changes or logs out:

* Clear the old queue and organization data.
* Clear active audio, playback state, progress indicators, and user-specific cached state.
* Close or replace old SSE subscriptions.
* Reconnect SSE under the new authenticated session.
* Fetch the new user's queue only after the authentication transition is complete.
* Prevent stale asynchronous requests from restoring data belonging to the previous user.

## 6. Comprehensive backend testing

Retain and expand the Python unit, mock, integration, and behavioral tests.

Cover:

* Authentication and session validation.
* OAuth callback success and failure.
* Authorization and organization capability enforcement.
* Queue visibility, ownership, assignment, deletion, and clearing.
* Upload validation and path confinement.
* Conversion worker success and failure.
* Missing and zero-byte output files.
* Unique filenames and independent batch outputs.
* Audio playback and download authorization.
* SSE event filtering and error propagation.
* API rate limits and request-size limits.
* Malformed requests and safe error responses.
* Session invalidation and logout.
* Regression cases for previously fixed bugs.

Mock expensive neural text-to-speech model execution where appropriate for deterministic tests. Clearly distinguish mocked tests from tests that exercise the real model, real audio generation, or production OAuth provider.

Do not claim comprehensive coverage merely because the number of functions was inventoried. Report actual tests, coverage metrics, and untested paths separately.

## 7. Comprehensive frontend testing

Use Vitest and React Testing Library for unit, component, and behavioral testing. Use Playwright for browser-based end-to-end testing.

### API unit tests

Test:

* Authentication headers and cookie/session behavior.
* API success and error responses.
* HTTP 401, 403, 404, and 500 responses.
* Malformed JSON, network errors, and timeouts where applicable.
* Audio Blob fetching, content types, filenames, and empty responses.
* Upload errors and batch upload behavior.
* SSE event parsing, reconnection, and cleanup.
* Session changes and stale request handling.

### React component tests

Test the existing `AuthModal`, `App`, `SingleFileTab`, `BatchTab`, and queue components.

Cover:

* Local login success and failure.
* OAuth sign-in entry point and failure handling.
* Preservation of entered credentials after a failed login.
* Queue rendering and filtering.
* Single-file upload, conversion progress, completion, playback, and download.
* Batch upload and independent job/output handling.
* Zero-byte output rejection.
* Authenticated audio download behavior.
* Login switching and logout cleanup.
* Proper handling of loading states, disabled controls, and errors.

### Browser end-to-end tests

Use Playwright to test the running application in a real browser.

Cover:

* Login and logout.
* OAuth flow using a controlled test provider or a deterministic mocked OAuth environment.
* Single-file upload and conversion.
* Multiple-document batch conversion.
* Playback and download.
* Queue filtering and progress updates.
* Session expiration and user switching.
* Browser console errors, failed network requests, CSP violations, and WebSocket failures.
* Cookie security and protected endpoint behavior.
* Two-user authorization scenarios.

For two-user tests:

1. User A submits a job and can view it.
2. User B cannot view, stream, or download User A's job.
3. An authorized organization queue manager assigns the job to User B.
4. User B can view and access the assigned job.
5. User A retains access as the original submitter.
6. Unrelated users remain unauthorized.

Collect useful Playwright traces, screenshots, console output, and failure diagnostics.

## 8. Fix the current Vitest component-test failures

The current test run reports 19 frontend tests: 16 passing and 3 failing in `tests/frontend/components.test.tsx`. The latest reported run had two authentication test failures; earlier output also showed queue filename assertions failing because multiple jobs legitimately rendered the same filename.

Inspect the actual source and test files before changing anything. Do not assume that an earlier patch was correct.

### Authentication test query failures

The test code previously used:

```ts
within(screen.getByRole('form')).getByRole('button', {
  name: /sign in/i,
})
```

This fails because the form is not reliably discoverable by the `form` role when it has no accessible name.

The proposed replacement is:

```ts
const passwordInput = screen.getByPlaceholderText('••••••••••••')
const loginForm = passwordInput.closest('form')

if (!loginForm) {
  throw new Error('Login form not found')
}

await user.click(
  within(loginForm).getByRole('button', { name: /sign in/i }),
)
```

Apply the fix to both authentication tests:

* `submits local login credentials and passes authenticated result to App`
* `renders authentication failures without losing entered credentials`

Also inspect the actual `AuthModal.tsx` markup. The login-name and password labels may not be correctly associated with their inputs. Prefer correcting accessible markup in the application, using proper `<label htmlFor="...">` and matching input IDs or equivalent accessible naming, rather than permanently weakening the tests to use placeholder queries. Preserve the existing design and functionality.

The login submit button must be queried within the login form because the interface has both a Sign In tab and a Sign In submit button.

### Queue filename assertion failures

Multiple jobs may legitimately display the same source filename. Do not assume that the filename is unique.

Where the test expects multiple jobs to display `book.mp3`, use a query that matches the intended number of elements, for example:

```ts
expect(screen.getAllByText('book.mp3')).toHaveLength(2)
```

After filtering, verify the number of matching items appropriate to the filter state. Prefer stable job identifiers or accessible row labels when that produces a more meaningful assertion.

### Verify the fix instead of merely claiming success

* Run the complete frontend Vitest suite.
* Run the Python test suite.
* Run linting and type checking.
* Run Playwright tests where the required browser and application services are available.
* Fix all failures demonstrated by actual output.
* Do not claim tests passed unless they were actually executed.
* If execution is unavailable, state the exact environmental limitation and provide the commands needed to verify the changes.

## 9. Test layout and commands

Preserve the existing project structure where practical. Organize tests clearly into API unit tests, component tests, behavioral tests, and browser E2E tests.

Maintain useful npm scripts such as:

```bash
npm run test:frontend
npm run test:frontend:watch
npm run test:frontend:coverage
npm run test:frontend:unit
npm run test:frontend:behavior
npm run test:e2e
npm run test:e2e:headed
npm run test:e2e:debug
npm run test:all
```

Provide a top-level test runner that executes backend and frontend tests and reports each result accurately. It must return a nonzero exit code when a required test suite fails.

Detect missing dependencies such as `pytest`, Node.js, npm packages, or Playwright browsers and explain how to install them. Do not silently skip required tests.

Keep browser E2E tests optional only when explicitly requested or when the documented runner mode allows it. Make this distinction clear in the test summary.

## 10. Implementation and delivery requirements

* Start by inspecting the actual repository and all relevant files.
* Preserve existing features, routes, authentication options, UI behavior, and conversion functionality.
* Avoid replacing working code with simplified stubs.
* Make minimal, targeted changes where possible.
* Use maintainable types, clear error handling, and security checks on the server.
* Add regression tests for every reported bug.
* Review changes for regressions, missing imports, invalid test selectors, incorrect paths, and mismatched frontend/backend contracts.
* Ensure all referenced test files actually exist and all npm scripts point to valid files.
* Do not claim a test suite is complete based only on source-string checks.
* Provide a complete ZIP of the corrected project or test package, with all necessary source files and documentation.
* Include a concise change log, installation instructions, environment configuration requirements, test commands, and a test-results report.
* Clearly list any remaining failures, limitations, or tests that were not executed.

## Acceptance criteria

The work is complete only when:

1. OAuth 2.0 and local authentication work according to configuration.
2. Batch jobs produce distinct, correct output files without collisions.
3. Queue visibility, job assignment, and organization capabilities are enforced server-side.
4. Audio playback and downloads are authenticated and reject missing or empty files.
5. Switching users cannot expose stale private data.
6. Security controls are tested with positive and negative cases.
7. The current authentication component-test failures are fixed.
8. Queue tests correctly account for duplicate filenames.
9. Backend, frontend, and available E2E test results are reported truthfully.
10. A complete, usable ZIP and reproducible verification instructions are delivered.

**Priority:** Fix demonstrated failures first, then execute the full regression suite. Preserve existing application functionality throughout. Do not substitute claims of success for actual verification.
