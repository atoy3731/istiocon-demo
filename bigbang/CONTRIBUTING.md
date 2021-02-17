# Contributing

Thanks for contributing to this repository!

This repository follows the following conventions:

* [Semantic Versioning](https://semver.org/)
* [Keep a Changelog](https://keepachangelog.com/)
* [Conventional Commits](https://www.conventionalcommits.org/)

Development requires the Kubernetes CLI tool as well as a Kubernetes cluster. [k3d](https://k3d.io) is recommended as a lightweight local option for standing up Kubernetes clusters.

To contribute a change:

1. Create a branch on the cloned repository
1. Make the changes in code.
1. Test by deploying [Big Bang](https://repo1.dsop.io/platform-one/big-bang/umbrella) to your Kubernetes cluster and verifying overrides.
1. Make commits using the [Conventional Commits](https://www.conventionalcommits.org/) format. This helps with automation for changelog. Update `CHANGELOG.md` in the same commit using the [Keep a Changelog](https://keepachangelog.com). Depending on tooling maturity, this step may be automated.
1. Ensure all new commits from the `main` branch are rebased into your branch.
1. Open a merge request. If this merge request is solving a preexisting issue, add the issue reference into the description of the MR.
1. Wait for a maintainer of the repository (see CODEOWNERS) to approve.
1. If you have permissions to merge, you are responsible for merging. Otherwise, a CODEOWNER will merge the commit.
