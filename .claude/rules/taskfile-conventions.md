# Taskfile Conventions

> Task -- The Modern Task Runner -- A fast, cross-platform build tool inspired by Make, designed for modern workflows.

**Taskfile.yml** is the primary task runner for this project. The root `Taskfile.yml` includes modular namespace directories from `./tasks/`.

## Structure

```text
Taskfile.yml              # Root: includes all namespaces
./tasks/
├── build/
│   └── Taskfile.yml      # Plugin build tasks
├── deploy/
│   └── Taskfile.yml      # Deployment and validation
├── rust/
│   └── Taskfile.yml      # Rust toolchain tasks
├── python/
│   └── Taskfile.yml      # Python toolchain tasks
└── {namespace}/
    └── Taskfile.yml      # Additional namespaces
```

## Conventions

- **Namespaces**: Each `./tasks/{namespace}/` directory contains a `Taskfile.yml`
- **Variables**: Use `{{.BINARY}}` for OS-aware binary paths
- **Descriptions**: Keep task `desc` fields concise and colon-free (or quote them)

## Common Tasks

```bash
task build              # Build all plugins
task build -- name      # Build specific plugin
task lint               # Run all linters
task test               # Run all tests
task all                # Lint, test, build
```

## Resources

- [docs](https://taskfile.dev/docs/guide)
- [style guide](https://taskfile.dev/docs/styleguide)
- [github.com/go-task/task](https://github.com/go-task/task)
