# Contributing to Ridder Field (φCDM)

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the Geometric Early Dark Energy research code.

---

## Ways to Contribute

### 1. Scientific Discussion
- Open an issue to discuss the physics
- Suggest improvements to the model
- Point out inconsistencies or errors

### 2. Code Improvements
- Bug fixes
- Performance optimizations
- Documentation improvements
- Test coverage

### 3. Reproducing Results
- Verify MCMC chains on different systems
- Test with different likelihood combinations
- Report any discrepancies

---

## Getting Started

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/StevenRidder/Ridder-Field.git
cd Ridder-Field

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Compile CLASS
cd phase2/class
make clean && make -j4
cd python && pip install -e .
```

### Run Tests

```bash
# Quick smoke test
cd phase3
python -c "from classy import Class; print('CLASS works!')"

# Run a short MCMC chain
cobaya-run configs/ridder_v3_baseline.yaml -f
```

---

## Code Style

### Python
- Follow PEP 8
- Use type hints where practical
- Document functions with docstrings

### C (CLASS modifications)
- Follow existing CLASS style
- Document all new functions
- Keep changes minimal and well-isolated

### YAML (Cobaya configs)
- Use consistent indentation (2 spaces)
- Comment non-obvious parameters
- Group related parameters together

---

## Submitting Changes

### For Bug Fixes

1. Fork the repository
2. Create a branch: `git checkout -b fix/description`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### For New Features

1. Open an issue first to discuss
2. Fork the repository
3. Create a branch: `git checkout -b feature/description`
4. Implement with tests
5. Update documentation
6. Submit a pull request

### Commit Messages

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain the problem and why this change fixes it.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
```

---

## Important Files

| File | Description | Notes |
|------|-------------|-------|
| `phase2/class/source/ridder_unified_potential.c` | Core φ-field implementation | Be careful! |
| `phase3/configs/*.yaml` | MCMC configurations | Test changes |
| `phase2/paper/ridder_cosmology_paper.tex` | Main paper | For authors only |

---

## Questions?

- **Email**: sridder@post.harvard.edu
- **Issues**: [GitHub Issues](https://github.com/StevenRidder/Ridder-Field/issues)

---

## Code of Conduct

Be respectful and constructive. This is a scientific project—disagreements should be resolved through evidence and reasoned argument.

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

