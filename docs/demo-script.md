# Manual QA walkthrough: tenant isolation

This walkthrough is intentionally manual first. The automated tests are there to repeat these checks after every change.

## 1. Create two worlds

Use the synthetic identities in the project:

- Alice: Tenant A
- Bob: Tenant B

Give each tenant a private project. Before testing permissions, confirm the data really belongs to different tenants.

## 2. Test the normal path

List projects as Alice. She should see the Tenant A project. List projects as Bob. He should see the Tenant B project.

This proves the happy path before we start trying to cross the boundary.

## 3. Test the direct-object path

Copy Bob’s project ID and request it as Alice. The API should return `404` and no Bob data should appear in the response.

This is the check people miss when they only test the list screen.

## 4. Test a forbidden mutation

As Alice, try to rename Bob’s project. Expect a denial. Then read Bob’s project as Bob and confirm the name is unchanged.

The read-back is the real oracle. A response code alone is not enough.

## 5. Test role differences

Try the same operations as owner, admin, member, and viewer. Compare the result with `docs/authorization-matrix.md`.

Pay attention to the member case: a member can create and update in this example, but cannot delete or create privileged exports. A viewer can read but cannot mutate.

## 6. Test less-visible data paths

Create an export, a shared link, and a background job. Check each one from the wrong tenant. Revoke the shared link and try the old token again.

These are the paths that often bypass the main UI and expose a SaaS product’s real authorization quality.

## 7. Show the automation

Run `pytest -m boundary`, `pytest -m rbac`, and `pytest -m side_effect`. Explain that every mutation test reads the object back after the attempted action.

## The line to use in an interview

“I don’t stop at ‘the button was hidden.’ I test the request directly, try a foreign object ID, and read the record back to check whether a forbidden request caused a side effect.”
