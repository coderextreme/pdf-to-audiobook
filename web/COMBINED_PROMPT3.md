# Combined Implementation Prompt: OAuth 2.0 and Reliable Batch PDF-to-Audiobook Conversion

## Project

Repository: https://github.com/coderextreme/pdf-to-audiobook-web/

A previously modified version is available as `pdf-to-audiobook-web-oauth2-batch-fixed.zip`.

Act as a senior full-stack software engineer. Inspect the actual repository, understand its existing architecture, and implement secure OAuth 2.0 authentication and reliable batch PDF-to-audiobook conversion. Preserve existing functionality and return a complete, working, tested repository.

**Do not merely describe the changes or provide pseudocode. Implement them in the source code, run the available tests, fix regressions, and provide the complete corrected source as a ZIP archive.**

## 1. OAuth 2.0 / OpenID Connect authentication

Implement OAuth 2.0 Authorization Code flow with PKCE (S256), preferably using OpenID Connect when the identity provider supports it.

Requirements:

* Add OAuth login to the existing authentication UI without removing username/password authentication.
* Make the OAuth provider configurable through environment variables.
* Support configurable client ID, client secret where applicable, authorization endpoint, token endpoint, user-info endpoint, issuer, redirect URI, and required scopes.
* Keep client secrets and token-exchange operations on the server. Never expose confidential credentials in browser JavaScript.
* Generate and validate OAuth `state` to protect against CSRF.
* Generate and validate PKCE code verifiers and challenges.
* Validate OIDC ID-token signatures, issuer, audience, expiration, nonce, and other required claims when using OIDC.
* Use secure, HTTP-only session cookies with appropriate `Secure` and `SameSite` settings for the deployment environment.
* Prevent open redirects, session fixation, account impersonation, and unsafe automatic account linking.
* Integrate OAuth identities with the existing SQLite user and session model.
* Use a stable provider subject identifier to associate OAuth identities with local accounts. Do not automatically link accounts based only on an unverified email address.
* Ensure login, logout, session refresh, and account switching behave correctly.
* Protect authenticated conversion, queue, and download endpoints according to the existing authorization model.
* Keep local development and existing authentication operational when OAuth is not configured.
* Fail safely and provide useful server-side diagnostics if OAuth configuration or provider communication fails.
* Add `.env.example` entries and document provider registration, callback URLs, scopes, secrets, and deployment setup.

Do not introduce a new authentication framework or database schema without first determining whether the existing implementation already provides equivalent capabilities.

## 2. Fix batch conversion so each PDF produces its own audiobook

The current implementation has a critical concurrency concern: the `AudiobookConverter` is stateful, while the server may launch multiple worker threads using a shared global converter instance. Concurrent jobs may overwrite shared conversion properties, including input paths, output paths, voice configuration, or TTS state.

Investigate the actual code and choose a robust solution.

Requirements:

* Every uploaded PDF must be associated with its own independent job and conversion state.
* Every job must process the correct source document.
* Every job must generate its own audiobook using the correct extracted text, voice, settings, and TTS output.
* No job may overwrite another job's input, temporary files, output file, metadata, or audio buffer.
* Give each job a unique output filename, incorporating a collision-resistant job identifier or equivalent unique identifier.
* Handle PDFs with identical filenames or identical filename stems without collisions.
* Use unique temporary directories or files for each job, with appropriate cleanup.
* Do not share a mutable converter instance across concurrent jobs unless its thread safety is proven. Prefer independent converter instances; if that is not possible, implement explicit synchronization around the complete stateful conversion operation.
* Ensure asynchronous callbacks and worker tasks retain the correct job context.
* Verify that each job's completion status and output path refer to that job's actual result.
* Prevent incomplete, zero-byte, stale, or missing audio files from being marked as successful.
* Preserve retry behavior and ensure retries do not overwrite unrelated jobs.
* Keep the batch UI's download actions associated with the correct output file.
* Ensure generated files remain distinct when downloading individually or as a batch archive.
* Preserve progress reporting, queue behavior, error handling, and existing supported audio formats.

Example expected output:

```text
chapter_a_<unique-job-id>.mp3
chapter_b_<unique-job-id>.mp3
```

The filenames are illustrative; follow the application's existing naming conventions where possible.

**Important:** Unique filenames alone are insufficient. Fix the underlying state-sharing, data-association, and concurrency problems.

## 3. Regression tests for batch conversion

Create automated tests that reproduce the original failure and verify the correction.

At minimum:

1. Submit two deliberately different PDFs in the same batch.
2. Verify each job receives the correct source PDF.
3. Verify each output is generated from the corresponding document, not the other document.
4. Verify the output paths are distinct.
5. Verify the generated audio files are distinct and nonempty.
6. Verify each output's content or decoded audio corresponds to its source document. Do not rely exclusively on file hashes, because identical legitimate inputs or deterministic encoders may produce identical bytes.
7. Submit multiple PDFs with the same filename stem and verify there are no collisions.
8. Run several conversions concurrently and repeat the test to detect race conditions.
9. Simulate conversion failures and verify that retries do not corrupt successful jobs.
10. Verify that empty or missing output files result in a failed job rather than a successful one.
11. Verify batch downloads return the correct file for each job.
12. Verify temporary files are isolated and cleaned up safely.

Use deterministic mocks for TTS tests where appropriate, and include at least one integration test that exercises the real document-processing pipeline when the environment supports it.

## 4. Authentication and authorization tests

Add automated tests for:

* OAuth login initiation.
* Correct authorization URL and PKCE challenge generation.
* Successful callback and token exchange.
* Invalid, missing, or mismatched `state`.
* Invalid PKCE verifier.
* Invalid or expired tokens.
* OIDC issuer, audience, signature, nonce, and expiration validation.
* Missing or invalid user identity information.
* OAuth provider errors and timeouts.
* Logout and session invalidation.
* Session fixation and unsafe redirect protections.
* Preventing account linking based solely on an unverified email address.
* Access to conversion and download endpoints without authentication.
* Access control for users who do not own the requested job.
* Preservation of existing username/password login behavior.
* OAuth-disabled behavior in local development.

Mock external identity providers so tests do not require real credentials or live OAuth services.

## 5. Preserve and verify existing application functionality

Before modifying the source, inspect the frontend, backend, converter, database schema, session management, queue, and existing tests.

Preserve existing behavior unless a change is required for correctness or security, including:

* Single-file conversion.
* Batch conversion.
* User authentication and session handling.
* Per-user queue visibility and job ownership.
* Organization-specific queue permissions, including existing `queue:read` and `queue:manage` capabilities.
* Queue refresh when users or sessions change.
* Correct download permissions and file associations.
* Frontend progress indicators and error reporting.
* Existing audio playback and supported output formats.
* Existing API contracts unless changes are necessary and documented.

Do not delete existing functionality to make tests pass. Avoid broad rewrites when targeted fixes are sufficient.

## 6. Security, configuration, and deployment

* Keep secrets out of source control and generated ZIP archives.
* Use environment variables for OAuth credentials and other deployment-specific secrets.
* Validate uploaded files, output paths, and user-supplied filenames.
* Prevent path traversal and unauthorized file access.
* Use safe file creation and cleanup procedures.
* Apply reasonable upload limits, timeouts, and error handling.
* Ensure authentication and authorization are enforced server-side, not only in the frontend.
* Document database migrations or schema changes.
* Document environment setup, dependency installation, OAuth configuration, build commands, test commands, and production deployment.
* Do not claim production readiness without verifying the relevant security controls and tests.

## 7. Build and test requirements

Inspect the repository's actual package managers, scripts, dependencies, and runtime requirements before running commands.

Run all applicable checks, including:

* Frontend type checking.
* Frontend production build.
* Frontend unit and component tests.
* Backend unit and integration tests.
* OAuth security tests.
* Batch concurrency and regression tests.
* Linting and static analysis.
* Relevant API and download authorization tests.

Resolve test failures introduced by the changes. If an existing failure is unrelated, identify it explicitly and provide the evidence.

If dependencies are missing, install them when possible. If a check cannot run, state the exact reason and do not report it as passing.

Review the final diff for accidental deletion of existing features, leaked secrets, debug code, stale build artifacts, and generated databases.

## 8. Required deliverables

Return:

1. A complete ZIP archive containing the corrected application source.
2. All source changes required for OAuth 2.0/OIDC and the batch-conversion fix.
3. Automated regression and security tests.
4. Updated `.env.example` and setup documentation.
5. A concise implementation summary identifying the root cause of the batch duplication problem and how it was fixed.
6. A list of commands executed and their actual results.
7. A clear list of any remaining failures, untested behaviors, configuration requirements, and deployment caveats.

Exclude `.git` history, production credentials, local `.env` files, databases containing user data, encryption keys, caches, and unnecessary generated artifacts from the ZIP.

Ensure the archive contains all required source and configuration templates so another developer can install dependencies, configure OAuth, build the application, and run the tests.

## Acceptance criteria

The work is complete only when:

* OAuth login works with a correctly configured provider and existing authentication remains available.
* OAuth state, PKCE, token validation, session security, and authorization checks are tested.
* Multiple different PDFs can be converted concurrently without cross-contamination.
* Every batch item receives a separate output path and correctly associated audiobook.
* Regression tests demonstrate that different inputs do not accidentally produce the same result because of shared mutable state.
* Single-file conversion, queue permissions, and download behavior continue to work.
* The production build and applicable automated tests have been run, with their actual outcomes documented.
* The complete corrected source is delivered as a ZIP archive.

Prioritize correctness, security, backward compatibility, and reproducible testing over minimizing the number of source changes.
