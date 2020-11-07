- [How do we work with Git, PR & Github](#how-we-use-git)

# How we use Git
- Master branch is only used for new versions. DO NOT MAKE A PULL REQUEST ON THIS BRANCH !
- Develop branch is used when there is a new feature
- For bug fix, there is two kind of bugs:
  - Important bugs:
    - These bugs may be severe - fixing them is a high priority
    - These bugs will have "Important" tag on GitHub
    - When fixed, you should create 2 PRs: One targetting the main branch & one targetting the development branch
    - Make sure to test rigorously - the changes could be applied in production code fairly soon, buggy code would be disastrous
  - Other bugs:
    - These bugs will have "Non-Important" tag on GitHub
    - When fixed, PR should target "develop" branch

## Pull Request
- Use minimal commit ! Squash & rebase your changes whenever you edit your PR before submitting ! Don't do like [this](https://github.com/tazz4843/McPy/pull/20) guy !
- Prefixes like `[FIX]` or `[IMP]` in Pull Requests should be avoided. You can still use it in commits.
- More informations about Squash & rebase [here](https://www.internalpointers.com/post/squash-commits-into-one-git), [here](https://www.devroom.io/2011/07/05/git-squash-your-latests-commits-into-one/) or [here (french)](https://www.ekino.com/articles/comment-squasher-efficacement-ses-commits-avec-git)
