# Authorization matrix

| Operation | owner | admin | member | viewer | Cross-tenant |
|---|---:|---:|---:|---:|---:|
| List/read own projects | yes | yes | yes | yes | 404 |
| Create project | yes | yes | yes | 403 | n/a |
| Update own project | yes | yes | yes | 403 | 404 |
| Delete own project | yes | yes | no | 403 | 404 |
| Create/read export | yes | yes | no | no | 404 |
| Create/revoke shared link | yes | yes | no | no | 404 |
| Create/read background job | yes | yes | no | no | 404 |

The test suite asserts this matrix against the local demonstration API. It does not claim the matrix is appropriate for every SaaS product.
