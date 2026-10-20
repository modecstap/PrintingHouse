# How to Organize web-ui Code

Steps for creating and changing the structure of `src/`. Target structure: [reference guide](reference.md).

## Add a Component

1. Decide whether the component contains business logic.
2. If it does not, create `components/generic/<name>/`.
3. If it does, find the domain directory it belongs to: `components/<domain>/`. If there is none, create it.
4. If the component is small and serves only one parent component, place it next to the parent file: `product/product-price.jsx`. Stop here.
5. Otherwise, create a directory for the component and the main file named after it: `product/product.jsx`.
6. Add the test and styles next to the main file: `product.test.jsx`, `product.module.css`.
7. Do not create `api/`, `models/`, `handlers/`, or `components/` in advance.

## Split a Growing Component

Signs: the main file is hard to read, mixes API calls, data processing, and event handling, or the directory contains many helper components.

1. Move backend and third-party service calls into `api/`. Expose them as functions: `fetchProduct(id)`.
2. Move data validation and transformation into `models/`. See [Validate API Data](#validate-api-data).
3. Move reactions to input, clicks, and other events into `handlers/`.
4. Move helper React components into `components/`.
5. Create only the subdirectories from steps 1–4 that received code.
6. Update imports and run the tests.

```text
before:                      after:
product/                     product/
  product.jsx                  api/
  product-price.jsx              product.js
  product-gallery.jsx          models/
  product.test.jsx               product.js
                               components/
                                 product-price.jsx
                                 product-gallery.jsx
                               product.jsx
                               product.test.jsx
```

## Add a Utility

1. Check `lib/` for a module with the same purpose. If it exists, add the function there.
2. Otherwise, create a module directly in `lib/`. Name it after its purpose: `format-price.js`, not `helpers.js`.
3. Do not create `utils/`, `helpers/`, or `services/` inside `lib/`.

## Wrap a Third-Party Library

1. Create a module in `lib/` named after the task the library solves: `lib/error-reporting.js`, not `lib/sentry.js`.
2. Import the library only in this module.
3. Export functions for the operations the project needs: `reportError(error)`.
4. Replace all direct imports of the library in the rest of the code with calls to the module.

## Validate API Data

1. Create `models/<model>.js` in the component directory.
2. Write a function `to<Model>(raw)`. Check each field the component uses and throw an `Error` with the model and field name if a check fails.
3. Return a new object with only the fields the component uses.
4. Call the function in `api/` on the response, before returning it.
5. Pass the result to the component. Do not check the data again inside the component.

## Add a Test

1. Create the test next to the tested file with the `.test` suffix: `product.jsx` and `product.test.jsx`.
2. If the same environment setup is already used in another test, move it to `test-utils/` as a function: `renderWithAuth(ui, user)`.
3. Replace the repeated setup in both tests with a call to that function.

## Add a Dependency

1. Check whether Hooks or the Context API solve the task. If they do, do not add the library.
2. Check whether `lib/` already wraps a library with the same purpose. If it does, use that module.
3. Add the library and wrap it as described in [Wrap a Third-Party Library](#wrap-a-third-party-library).
